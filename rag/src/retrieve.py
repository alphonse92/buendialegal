import os
import sys
import warnings
from typing import List

from langchain_core.documents import Document

from common import build_vector_store

warnings.filterwarnings("ignore")

TOP_K = int(os.getenv("RAG_RETRIEVE_TOP_K", "15"))


def retrieve(question: str, top_k: int = TOP_K) -> List[tuple[Document, float]]:
    """Return (document, score) pairs sorted by relevance."""
    collection_name = os.getenv("RAG_LC_COLLECTION", "vector_agent")
    store = build_vector_store(collection_name)
    return store.similarity_search_with_score(question, k=top_k)


def format_results(question: str, results: List[tuple[Document, float]]) -> str:
    """Format results as XML that AI agents (Claude, GPT, etc.) parse reliably."""
    lines: list[str] = []
    lines.append(f'<retrieval query="{question}" results="{len(results)}">')

    for i, (doc, score) in enumerate(results, 1):
        path = doc.metadata.get("file_path") or doc.metadata.get("source") or "unknown"
        lines.append(f'  <chunk index="{i}" score="{score:.4f}" file="{path}">')
        # Indent code for readability but preserve original content
        for code_line in doc.page_content.splitlines():
            lines.append(f"    {code_line}")
        lines.append("  </chunk>")

    lines.append("</retrieval>")
    return "\n".join(lines)


def main(argv: list[str]) -> None:
    if not argv:
        print('Usage: python agent_retrieve.py "your question here"')
        return

    question = " ".join(argv)

    try:
        results = retrieve(question)
        if not results:
            print(f'<retrieval query="{question}" results="0" />')
            return
        print(format_results(question, results))
    except Exception as exc:
        print(f"Error during retrieval: {exc}")


if __name__ == "__main__":
    main(sys.argv[1:])
