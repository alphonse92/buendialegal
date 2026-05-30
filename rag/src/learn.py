import os
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from common import build_vector_store, build_llm

warnings.filterwarnings("ignore")

COLLECTION = os.getenv("RAG_MEMORY_COLLECTION", "agent_memory")
CHUNK_SIZE = int(os.getenv("RAG_MEMORY_CHUNK_SIZE", "1500"))
CHUNK_OVERLAP = int(os.getenv("RAG_MEMORY_CHUNK_OVERLAP", "200"))
SOURCE = os.getenv("RAG_MEMORY_SOURCE", "agent")


def load_shallow_prompt() -> str:
    prompt_path = Path(__file__).parent / "prompts" / "shallow.md"
    return prompt_path.read_text()


def generate_shallow(text: str) -> str:
    try:
        prompt_text = load_shallow_prompt()
        prompt = ChatPromptTemplate.from_template(
            prompt_text + "\n\n---\n\nKnowledge: {text}\n"
        )
        llm = build_llm()
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"text": text})
        return result.strip()[:80]
    except Exception:
        return "(no summary)"


def main(argv: list[str]) -> None:
    if not argv:
        print('Usage: python learn.py "knowledge text here"')
        return

    text = " ".join(argv)
    timestamp = datetime.now(timezone.utc).isoformat()
    shallow = generate_shallow(text)
    metadata = {"timestamp": timestamp, "source": SOURCE, "shallow": shallow}

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

    print(f"Learned {len(docs)} chunk(s) into '{COLLECTION}' [shallow: {shallow}]")


if __name__ == "__main__":
    main(sys.argv[1:])
