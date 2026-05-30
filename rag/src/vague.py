import os
import sys
import warnings
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from common import build_vector_store, build_llm

warnings.filterwarnings("ignore")

COLLECTION = os.getenv("RAG_MEMORY_COLLECTION", "agent_memory")
TOP_K = int(os.getenv("RAG_VAGUE_TOP_K", "5"))
THRESHOLD = float(os.getenv("RAG_VAGUE_THRESHOLD", "0.45"))


def load_rewrite_prompt() -> str:
    prompt_path = Path(__file__).parent / "prompts" / "vague-rewrite.md"
    return prompt_path.read_text()


def rewrite_query(question: str) -> str:
    prompt_text = load_rewrite_prompt()
    prompt = ChatPromptTemplate.from_template(
        prompt_text + "\n\n---\n\nQuestion: {question}\n"
    )
    llm = build_llm()
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"question": question})


def main(argv: list[str]) -> None:
    if not argv:
        print('Usage: python vague.py "your prompt"')
        return

    question = " ".join(argv)

    try:
        rewritten = rewrite_query(question)
    except Exception:
        rewritten = question

    try:
        store = build_vector_store(COLLECTION)
        results = store.similarity_search_with_score(rewritten, k=TOP_K)
    except Exception:
        results = []

    filtered = [(doc, score) for doc, score in results if score <= THRESHOLD]

    # Deduplicate by shallow value
    seen_shallows = set()
    deduped = []
    for doc, score in filtered:
        shallow = doc.metadata.get("shallow", "(no summary)")
        if shallow not in seen_shallows:
            seen_shallows.add(shallow)
            deduped.append((doc, score, shallow))

    if not deduped:
        print(f'<vague q="{rewritten}" results="0" />')
        return

    print(f'<vague q="{rewritten}" results="{len(deduped)}">')
    for i, (doc, score, shallow) in enumerate(deduped, 1):
        print(f'  <s i="{i}" score="{score:.2f}">{shallow}</s>')
    print("</vague>")


if __name__ == "__main__":
    main(sys.argv[1:])
