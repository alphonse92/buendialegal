# RAG - Codebase Assistant

Local RAG pipeline using LangChain, Ollama, and pgvector to index and query codebases.

## Prerequisites

### Ollama

Install Ollama from [ollama.com](https://ollama.com) and pull the required models:

```bash
ollama pull nomic-embed-text   # embedding model
ollama pull llama3             # LLM for Q&A
```

### Context length and embeddings

Ollama models have a maximum context length (measured in tokens). If an embedding request
exceeds this limit, Ollama returns `the input length exceeds the context length`.

You can increase the context length (if your GPU has enough VRAM) by configuring Ollama:

```bash
OLLAMA_CONTEXT_LENGTH=64000 ollama serve
```

Refer to the Ollama documentation for safe context sizes on your hardware.

## Usage

Start the RAG infrastructure:

```bash
make -f betteragents.mk up
```

Index the codebase (run once, or after code changes):

```bash
make -f betteragents.mk ingest
```

Ask questions about the codebase:

```bash
make -f betteragents.mk ask q="how does authentication work?"
```

Retrieve raw chunks (useful for agent consumption):

```bash
make -f betteragents.mk retrieve q="auth middleware"
```

## Environment variables

Set these in your `docker-compose.yml` (see the `rag` service) or when running scripts locally.

### Ollama

| Variable       | Default                           | Description |
|----------------|-----------------------------------|-------------|
| `OLLAMA_HOST`  | `http://host.docker.internal:11434` | Ollama API base URL (embedding and LLM). |

### Models

| Variable           | Default               | Description |
|--------------------|-----------------------|-------------|
| `RAG_EMBED_MODEL`  | `nomic-embed-text`   | Embedding model used for indexing and retrieval. |
| `RAG_LLM_MODEL`    | `llama3`             | Chat model used for Q&A. |

### Database (PostgreSQL)

| Variable       | Default    | Description |
|----------------|------------|-------------|
| `DB_HOST`      | `db`       | PostgreSQL host. |
| `DB_PORT`      | `5432`     | PostgreSQL port. |
| `DB_NAME`      | `postgres` | Database name. |
| `DB_USER`      | `postgres` | Database user. |
| `DB_PASSWORD`  | `password` | Database password. |

### Codebase and indexing

| Variable              | Default                     | Description |
|-----------------------|-----------------------------|-------------|
| `CODEBASE_PATH`       | `/codebase/`                | Path to the codebase to index (mounted in the container). |
| `REQUIRED_EXTS`       | `.ts,.js,.json,.sql,.md`    | Comma-separated file extensions to include when ingesting. |
| `RAG_LC_COLLECTION`   | `vector_agent`              | LangChain PGVector collection name. |

### Ingestion tuning

Keep values below the embedding model's context limit to avoid ingest failures.

| Variable             | Default | Description |
|----------------------|---------|-------------|
| `RAG_LC_CHUNK_SIZE`  | `3000`  | Character chunk size for ingestion. |
| `RAG_LC_CHUNK_OVERLAP` | `400` | Overlap between chunks. |

### Retrieval

| Variable              | Default | Description |
|-----------------------|---------|-------------|
| `RAG_RETRIEVE_TOP_K`  | `15`    | Number of chunks returned by `retrieve.py`. |

### Agent memory

| Variable                  | Default          | Description |
|---------------------------|------------------|-------------|
| `RAG_MEMORY_COLLECTION`   | `agent_memory`   | PGVector collection for learned knowledge. |
| `RAG_MEMORY_CHUNK_SIZE`   | `1500`           | Max characters per chunk when splitting large inputs. |
| `RAG_MEMORY_CHUNK_OVERLAP`| `200`            | Overlap between chunks. |
| `RAG_MEMORY_SOURCE`       | `agent`          | Source label stored in metadata. |
| `RAG_MEMORY_TOP_K`        | `10`             | Max results to consider before threshold filtering. |
| `RAG_MEMORY_THRESHOLD`    | `0.45`           | Max distance score — results above this are discarded. |
