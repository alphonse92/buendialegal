import os
import sys
import warnings
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from common import build_vector_store, build_llm

warnings.filterwarnings("ignore")

COLLECTION = os.getenv("RAG_MEMORY_COLLECTION", "agent_memory")
JOURNAL_COLLECTION = os.getenv("RAG_JOURNAL_COLLECTION", "agent_journal")
TOP_K = int(os.getenv("RAG_MEMORY_TOP_K", "10"))
THRESHOLD = float(os.getenv("RAG_MEMORY_THRESHOLD", "0.45"))


def load_system_prompt() -> str:
    prompt_path = Path(__file__).parent / "prompts" / "memory.md"
    return prompt_path.read_text()


def load_journal_rewrite_prompt() -> str:
    prompt_path = Path(__file__).parent / "prompts" / "journal-rewrite.md"
    return prompt_path.read_text()


PROMPT = ChatPromptTemplate.from_template(
    load_system_prompt()
    + "\n\n---\n\n"
    + "Knowledge:\n{context}\n\n"
    + "Question: {question}\n"
)

JOURNAL_REWRITE_PROMPT = ChatPromptTemplate.from_template(
    load_journal_rewrite_prompt()
    + "\n\n---\n\n"
    + "Question: {question}\n"
    + "Context:\n{context}\n"
)


def ask_llm(question: str, context: str) -> str:
    llm = build_llm()
    chain = PROMPT | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})


def rewrite_for_journal(question: str, context: str) -> str:
    llm = build_llm()
    chain = JOURNAL_REWRITE_PROMPT | llm | StrOutputParser()
    return chain.invoke({"question": question, "context": context})


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print('Usage: python remember.py <classic|verbose> "your question here"')
        return

    mode = argv[0]
    if mode not in ("classic", "verbose"):
        print('First argument must be "classic" or "verbose"')
        return

    question = " ".join(argv[1:])

    try:
        store = build_vector_store(COLLECTION)
        results = store.similarity_search_with_score(question, k=TOP_K)
    except Exception:
        results = []

    memory_filtered = [(doc, score) for doc, score in results if score <= THRESHOLD]

    if not memory_filtered:
        if mode == "classic":
            print("No relevant knowledge found.")
        else:
            print(f'<m q="{question}" t="{THRESHOLD}" />')
        return

    # Build context from memory results for both final answer and journal rewrite
    memory_context = "\n".join(doc.page_content for doc, _ in memory_filtered)

    # Try to rewrite the question for journal search using memory context
    journal_results: list[tuple] = []
    try:
        rewritten_question = rewrite_for_journal(question, memory_context)
        journal_store = build_vector_store(JOURNAL_COLLECTION)
        raw_journal_results = journal_store.similarity_search_with_score(
            rewritten_question, k=TOP_K
        )
        journal_results = [
            (doc, score) for doc, score in raw_journal_results if score <= THRESHOLD
        ]
    except Exception:
        journal_results = []

    combined: list[tuple] = []
    for doc, score in memory_filtered:
        combined.append((doc, score, "memory"))
    for doc, score in journal_results:
        combined.append((doc, score, "journal"))

    if not combined:
        if mode == "classic":
            print("No relevant knowledge found.")
        else:
            print(f'<m q="{question}" t="{THRESHOLD}" />')
        return

    context = "\n".join(doc.page_content for doc, _, _ in combined)
    answer = ask_llm(question, context)

    if mode == "classic":
        print(answer)
    else:
        print(f'<m q="{question}" t="{THRESHOLD}">')
        print(f"  <a>{answer}</a>")
        for i, (doc, score, src) in enumerate(combined, 1):
            print(f'  <k i="{i}" s="{score:.4f}" src="{src}">{doc.page_content}</k>')
        print("</m>")


if __name__ == "__main__":
    main(sys.argv[1:])
