import os
import sys
import warnings
from datetime import datetime, timezone

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from common import build_vector_store

warnings.filterwarnings("ignore")

COLLECTION = os.getenv("RAG_JOURNAL_COLLECTION", "agent_journal")
CHUNK_SIZE = int(os.getenv("RAG_JOURNAL_CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("RAG_JOURNAL_CHUNK_OVERLAP", "200"))
SOURCE = os.getenv("RAG_JOURNAL_SOURCE", "agent")


def main(argv: list[str]) -> None:
    if not argv:
        print('Usage: python journal.py "journal entry text here"')
        return

    text = " ".join(argv)
    timestamp = datetime.now(timezone.utc).isoformat()
    metadata = {"timestamp": timestamp, "source": SOURCE, "type": "journal"}

    if len(text) > CHUNK_SIZE:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        chunks = splitter.split_text(text)
        docs = [Document(page_content=c, metadata=metadata.copy()) for c in chunks]
    else:
        docs = [Document(page_content=text, metadata=metadata)]

    vector_store = build_vector_store(COLLECTION)
    vector_store.add_documents(docs)

    print(f"Journaled {len(docs)} chunk(s) into '{COLLECTION}'")


if __name__ == "__main__":
    main(sys.argv[1:])

