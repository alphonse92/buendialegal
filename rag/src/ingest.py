import argparse
import os
import warnings
from pathlib import Path
from typing import Iterable, List

import psycopg
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from common import build_vector_store, get_pgvector_connection_string

warnings.filterwarnings("ignore")

# nomic-embed-text supports 8192 tokens (~6k chars). Larger chunks preserve
# more semantic context (full functions, class definitions, route handlers).
CHUNK_SIZE = int(os.getenv("RAG_LC_CHUNK_SIZE", "3000"))
CHUNK_OVERLAP = int(os.getenv("RAG_LC_CHUNK_OVERLAP", "400"))

EXT_TO_LANGUAGE: dict[str, Language] = {
    ".ts": Language.TS,
    ".js": Language.JS,
    ".py": Language.PYTHON,
    ".md": Language.MARKDOWN,
    ".html": Language.HTML,
    ".swift": Language.SWIFT,
    ".go": Language.GO,
    ".java": Language.JAVA,
    ".kt": Language.KOTLIN,
    ".rs": Language.RUST,
    ".rb": Language.RUBY,
    ".php": Language.PHP,
    ".cs": Language.CSHARP,
    ".c": Language.C,
    ".h": Language.C,
    ".cpp": Language.CPP,
}

DEFAULT_REQUIRED_EXTS = ".ts,.js,.json,.sql,.md"
REQUIRED_EXTS_ENV_VAR = "REQUIRED_EXTS"


def _get_plain_pg_connection_string() -> str:
    """Return a psycopg-compatible connection string (without sqlalchemy prefix)."""
    return get_pgvector_connection_string().replace("postgresql+psycopg", "postgresql")


def create_generic_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )


def get_splitter_for_path(path: Path) -> RecursiveCharacterTextSplitter:
    ext = path.suffix.lower()
    language = EXT_TO_LANGUAGE.get(ext)
    print(f"Processing {path} lang: {ext}")
    if language is not None:
        return RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
    return create_generic_splitter()


def iter_source_files(codebase_path: Path, exts: Iterable[str]) -> Iterable[Path]:
    normalized_exts = {e if e.startswith(".") else f".{e}" for e in exts}
    for root, _, files in os.walk(codebase_path):
        for name in files:
            if any(name.endswith(ext) for ext in normalized_exts):
                yield Path(root) / name


def get_required_exts() -> list[str]:
    """Return the list of extensions to ingest.

    Values come from the REQUIRED_EXTS environment variable as a
    comma-separated string, falling back to DEFAULT_REQUIRED_EXTS
    when the variable is not set.
    """
    raw_exts = os.getenv(REQUIRED_EXTS_ENV_VAR, DEFAULT_REQUIRED_EXTS)
    return [ext.strip() for ext in raw_exts.split(",")]


def delete_embeddings_for_file(file_path: str) -> int:
    """Delete all embeddings whose metadata.file_path matches the given path."""
    conn_str = _get_plain_pg_connection_string()
    deleted = 0
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM langchain_pg_embedding "
                "WHERE cmetadata->>'file_path' = %s",
                (file_path,),
            )
            deleted = cur.rowcount
        conn.commit()
    return deleted


def get_existing_file_sizes(root: Path | None = None) -> dict[str, int | None]:
    """Return mapping of file_path -> stored file_size (if any) from the vector store.

    When root is provided, only entries whose file_path is under that directory
    are returned.
    """
    conn_str = _get_plain_pg_connection_string()
    sizes: dict[str, int | None] = {}
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            if root is not None:
                prefix = str(root)
                if not prefix.endswith("/"):
                    prefix = prefix + "/"
                cur.execute(
                    "SELECT DISTINCT cmetadata->>'file_path', "
                    "       cmetadata->>'file_size' "
                    "FROM langchain_pg_embedding "
                    "WHERE cmetadata->>'file_path' LIKE %s",
                    (prefix + "%",),
                )
            else:
                cur.execute(
                    "SELECT DISTINCT cmetadata->>'file_path', "
                    "       cmetadata->>'file_size' "
                    "FROM langchain_pg_embedding "
                    "WHERE cmetadata ? 'file_path'",
                )
            for path, size_str in cur.fetchall():
                existing_size: int | None = None
                if size_str is not None:
                    try:
                        existing_size = int(size_str)
                    except (TypeError, ValueError):
                        existing_size = None
                sizes[path] = existing_size
    return sizes


def should_reingest(current_size: int, existing_size: int | None) -> bool:
    """Return True if we should re-ingest given current and stored sizes."""
    if existing_size is None:
        return True
    return current_size != existing_size


def sync_ingest_directory(
    vector_store, root: Path, exts: Iterable[str]
) -> tuple[int, int]:
    """Smart sync ingestion for a directory tree.

    - Re-ingests files whose size has changed or is missing in metadata.
    - Skips files whose stored size matches the current size.
    - Deletes embeddings for files that no longer exist on disk.
    """
    exts = list(exts)
    existing_sizes = get_existing_file_sizes(root=root)

    total_files = 0
    total_chunks = 0

    disk_files: set[str] = set()

    for path in iter_source_files(root, exts):
        path_str = str(path)
        disk_files.add(path_str)
        current_size = path.stat().st_size
        existing_size = existing_sizes.get(path_str)

        if should_reingest(current_size, existing_size):
            if existing_size is None:
                print(f"Reingesting {path_str}, size stored was unknown")
            else:
                print(
                    f"Reingesting {path_str}, size changed from {existing_size} to {current_size}"
                )
            total_files += 1
            total_chunks += ingest_file(vector_store, path)
        else:
            print(f"Omited {path_str}, size are equal")

    # Delete embeddings for files that are in the DB under this root but no longer on disk.
    for db_path in existing_sizes.keys():
        if db_path not in disk_files:
            deleted = delete_embeddings_for_file(db_path)
            if deleted > 0:
                print(f"Deleted vectors for missing file {db_path}")

    return total_files, total_chunks


def ingest_file(vector_store, file_path: Path) -> int:
    """Ingest a single file by deleting its existing chunks and re-adding fresh ones.

    Returns the number of chunks indexed for this file.
    """
    try:
        loader = TextLoader(str(file_path), encoding="utf-8")
        raw_docs = loader.load()
    except Exception as exc:  # pragma: no cover - best-effort logging
        print(f"Skipping file due to load error: {file_path} ({exc})")
        return 0

    # Split using a language-aware splitter when possible.
    splitter = get_splitter_for_path(file_path)
    chunks: List[Document] = splitter.split_documents(raw_docs)

    # Ensure file_path metadata is set and prepend file path to content
    # so the embedding captures location context. Also store the file size
    # so that sync mode can decide whether re-ingestion is necessary.
    file_size_bytes = file_path.stat().st_size
    for doc in chunks:
        source = doc.metadata.get("source") or str(file_path)
        doc.metadata.setdefault("file_path", source)
        doc.metadata["file_size"] = file_size_bytes
        doc.page_content = f"FILE: {source}\n\n{doc.page_content}"

    # Delete any existing vectors for this file, then add the fresh chunks.
    deleted = delete_embeddings_for_file(str(file_path))
    if deleted > 0:
      print(f"Deleted {deleted} existing vectors for {file_path}")

    if chunks:
        vector_store.add_documents(chunks)

    print(f"Ingested {len(chunks)} chunks for {file_path}")
    return len(chunks)


def start_ingestion(sync: bool = False) -> None:
    codebase_path_str = os.getenv("CODEBASE_PATH", "/codebase/")
    codebase_path = Path(codebase_path_str)

    exts = get_required_exts()

    collection_name = os.getenv("RAG_LC_COLLECTION", "vector_agent")
    vector_store = build_vector_store(collection_name)

    print(f"Reading files {exts} under {codebase_path}...")

    total_files = 0
    total_chunks = 0

    if sync:
        total_files, total_chunks = sync_ingest_directory(vector_store, codebase_path, exts)
    else:
        for path in iter_source_files(codebase_path, exts):
            total_files += 1
            total_chunks += ingest_file(vector_store, path)

    print(
        f"Indexed {total_chunks} chunks from {total_files} files into collection '{collection_name}'."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest code files into the PGVector collection."
    )
    parser.add_argument(
        "--file",
        type=str,
        help=(
            "If provided, ingest this path only. "
            "The path may be a single file or a directory. "
            "Relative paths are resolved under CODEBASE_PATH."
        ),
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help=(
            "If provided, perform a smart sync: only re-ingest files whose "
            "size has changed and delete embeddings for files that no longer exist."
        ),
    )
    args = parser.parse_args()

    collection_name = os.getenv("RAG_LC_COLLECTION", "vector_agent")
    vector_store = build_vector_store(collection_name)

    if args.file:
        codebase_path_str = os.getenv("CODEBASE_PATH", "/codebase/")
        codebase_path = Path(codebase_path_str)
        candidate_path = Path(args.file)
        if not candidate_path.is_absolute():
            candidate_path = codebase_path / candidate_path

        exts = get_required_exts()

        if candidate_path.is_dir():
            print(
                f"Ingesting all files under directory {candidate_path} "
                f"with extensions {exts}..."
            )
            if args.sync:
                total_files, total_chunks = sync_ingest_directory(
                    vector_store, candidate_path, exts
                )
            else:
                total_files = 0
                total_chunks = 0
                for path in iter_source_files(candidate_path, exts):
                    total_files += 1
                    total_chunks += ingest_file(vector_store, path)
            print(
                f"Indexed {total_chunks} chunks from {total_files} files into "
                f"collection '{collection_name}' from directory '{candidate_path}'."
            )
        else:
            print(f"Ingesting single file: {candidate_path}")
            if args.sync:
                # In sync mode, only re-ingest this file if its size has changed or
                # it has not been ingested before.
                path_str = str(candidate_path)
                existing_sizes = get_existing_file_sizes(root=None)
                current_size = candidate_path.stat().st_size
                existing_size = existing_sizes.get(path_str)
                if should_reingest(current_size, existing_size):
                    if existing_size is None:
                        print(f"Reingesting {path_str}, size stored was unknown")
                    else:
                        print(
                            f"Reingesting {path_str}, size changed from {existing_size} to {current_size}"
                        )
                    ingest_file(vector_store, candidate_path)
                else:
                    print(f"Omited {path_str}, size are equal")
            else:
                ingest_file(vector_store, candidate_path)
    else:
        start_ingestion(sync=args.sync)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Error while running LangChain ingestion")
        print(f"{exc}")
