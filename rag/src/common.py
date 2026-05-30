import os

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_postgres.vectorstores import PGVector


def get_pgvector_connection_string() -> str:
    host = os.getenv("DB_HOST", "db")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "postgres")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "password")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


def get_embeddings() -> OllamaEmbeddings:
    ollama_host = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
    embed_model = os.getenv("RAG_EMBED_MODEL", "nomic-embed-text")
    return OllamaEmbeddings(model=embed_model, base_url=ollama_host)


def build_vector_store(collection_name: str) -> PGVector:
    return PGVector(
        embeddings=get_embeddings(),
        collection_name=collection_name,
        connection=get_pgvector_connection_string(),
        use_jsonb=True,
    )


def build_llm() -> ChatOllama:
    ollama_host = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
    llm_model = os.getenv("RAG_LLM_MODEL", "llama3")
    return ChatOllama(model=llm_model, base_url=ollama_host, temperature=0.0)
