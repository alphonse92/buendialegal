import os
import sys
import warnings
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from common import build_vector_store, build_llm

warnings.filterwarnings("ignore")

JOURNAL_COLLECTION = os.getenv("RAG_JOURNAL_COLLECTION", "agent_journal")


def load_system_prompt() -> str:
    prompt_path = Path(__file__).parent / "prompts" / "agent.md"
    return prompt_path.read_text()


def load_journal_rewrite_prompt() -> str:
    prompt_path = Path(__file__).parent / "prompts" / "journal-rewrite.md"
    return prompt_path.read_text()


def format_docs(docs: List[Document]) -> str:
    parts: List[str] = []
    for doc in docs:
        path = doc.metadata.get("file_path") or doc.metadata.get("source") or ""
        header = f"FILE: {path}" if path else ""
        if header:
            parts.append(header)
        parts.append(doc.page_content)
        parts.append("")
    return "\n".join(parts)


def format_journal_docs(docs: List[Document]) -> str:
    parts: List[str] = []
    for doc in docs:
        parts.append("JOURNAL:")
        parts.append(doc.page_content)
        parts.append("")
    return "\n".join(parts)


def extract_file_references(docs: List[Document]) -> List[str]:
    """Extract unique file paths from retrieved documents, preserving order."""
    seen = set()
    paths = []
    for doc in docs:
        path = doc.metadata.get("file_path") or doc.metadata.get("source") or ""
        if path and path not in seen:
            seen.add(path)
            paths.append(path)
    return paths


def build_rag_chain():
    collection_name = os.getenv("RAG_LC_COLLECTION", "vector_agent")
    vector_store = build_vector_store(collection_name)
    retriever = vector_store.as_retriever(search_kwargs={"k": 12})

    system_prompt = load_system_prompt()

    llm = build_llm()

    # Single-template prompt — proven to work with llama3.
    # from_messages with system/human roles causes llama3 to ignore context.
    prompt = ChatPromptTemplate.from_template(
        system_prompt
        + "\n\n---\n\n"
        + "Answer the question based ONLY on the following context:\n\n"
        + "{context}\n\n"
        + "Question: {question}\n"
    )

    answer_chain = prompt | llm | StrOutputParser()
    return retriever, answer_chain


def build_journal_rewrite_chain():
    prompt_text = load_journal_rewrite_prompt()
    prompt = ChatPromptTemplate.from_template(
        prompt_text
        + "\n\n---\n\n"
        + "Question: {question}\n"
        + "Context:\n{context}\n"
    )
    llm = build_llm()
    return prompt | llm | StrOutputParser()


def main(argv: list[str]) -> None:
    if not argv:
        print("Wrap the question in quotes")
        return

    question = " ".join(argv)

    try:
        retriever, answer_chain = build_rag_chain()

        docs = retriever.invoke(question)
        codebase_context = format_docs(docs)

        # Rewrite question for journal search using codebase context
        journal_docs: List[Document] = []
        try:
            journal_rewrite_chain = build_journal_rewrite_chain()
            rewritten_question = journal_rewrite_chain.invoke(
                {"question": question, "context": codebase_context}
            )
            journal_store = build_vector_store(JOURNAL_COLLECTION)
            journal_docs = journal_store.similarity_search(rewritten_question, k=5)
        except Exception:
            journal_docs = []

        context_parts: List[str] = [codebase_context] if codebase_context else []
        if journal_docs:
            journal_context = format_journal_docs(journal_docs)
            if journal_context:
                context_parts.append(journal_context)
        context = "\n\n".join(context_parts)

        response = answer_chain.invoke({"context": context, "question": question})

        file_refs = extract_file_references(docs)

        print(response)
        if file_refs or journal_docs:
            print("\n---\n")
            print("**References**")
            for path in file_refs:
                print(f"- {path}")
            for doc in journal_docs:
                ts = doc.metadata.get("timestamp", "")
                first_line = doc.page_content.strip().split("\n", 1)[0]
                label = ts or first_line[:80]
                print(f"- [journal] {label}")
    except Exception as exc:
        print(f"Error while running agentic RAG: {exc}")


if __name__ == "__main__":
    main(sys.argv[1:])
