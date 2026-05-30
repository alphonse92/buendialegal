# Invoke with: make -f betteragents.mk <target>
COMPOSE_FILE ?= docker-compose.rag.yml
RAG_CONTAINER ?= app

# --- Infrastructure ---

up: ## Start RAG infrastructure (db + rag container)
	docker compose -f $(COMPOSE_FILE) up -d --build

down: ## Stop and remove containers
	docker compose -f $(COMPOSE_FILE) down

logs: ## Tail container logs
	docker compose -f $(COMPOSE_FILE) logs -f

# --- RAG Operations ---

ingest: ## Ingest codebase into vector store
	docker exec $(RAG_CONTAINER) python ingest.py

ingest-sync: ## Ingest codebase into vector store
	docker exec $(RAG_CONTAINER) python ingest.py --sync

ingest-one: ## Ingest a single file. Usage: make -f betteragents.mk ingest-one p="src/App.tsx"
	@if [ -z "$(p)" ]; then echo 'Usage: make -f betteragents.mk ingest-one p="path/inside/codebase"'; exit 1; fi
	docker exec $(RAG_CONTAINER) python ingest.py --sync --file "$(p)"

ask: ## Ask a question about the codebase. Usage: make -f betteragents.mk ask q="how does the counter work?"
	@if [ -z "$(q)" ]; then echo 'Usage: make -f betteragents.mk ask q="your question"'; exit 1; fi
	docker exec $(RAG_CONTAINER) python ask.py "$(q)"

retrieve: ## Retrieve relevant code chunks. Usage: make -f betteragents.mk retrieve q="counter component"
	@if [ -z "$(q)" ]; then echo 'Usage: make -f betteragents.mk retrieve q="your question"'; exit 1; fi
	docker exec $(RAG_CONTAINER) python retrieve.py "$(q)"

translate: ## Translate phrase. Usage: make -f betteragents.mk translate lang=Japanese tone=formal ph="Good morning"
	@if [ -z "$(lang)" ] || [ -z "$(tone)" ] || [ -z "$(ph)" ]; then echo 'Usage: make -f betteragents.mk translate lang=<target> tone=<tone> ph="phrase"'; exit 1; fi
	docker exec $(RAG_CONTAINER) python translate.py "$(lang)" "$(tone)" "$(ph)"

learn: ## Store learned knowledge. Usage: make -f betteragents.mk learn t="knowledge text"
	@if [ -z "$(t)" ]; then echo 'Usage: make -f betteragents.mk learn t="knowledge text"'; exit 1; fi
	docker exec $(RAG_CONTAINER) python learn.py "$(t)"

remember: ## Recall learned knowledge. Usage: make -f betteragents.mk remember q="how does auth work?" m=classic|verbose
	@if [ -z "$(q)" ]; then echo 'Usage: make -f betteragents.mk remember q="your question" m=classic|verbose'; exit 1; fi
	docker exec $(RAG_CONTAINER) python remember.py "$(or $(m),verbose)" "$(q)"

vague: ## Quick shallow memory scan. Usage: make -f betteragents.mk vague q="domain backend"
	@if [ -z "$(q)" ]; then echo 'Usage: make -f betteragents.mk vague q="your prompt"'; exit 1; fi
	docker exec $(RAG_CONTAINER) python vague.py "$(q)"

journal: ## Store a journal entry. Usage: make -f betteragents.mk journal t="completed auth feature, commits: abc123"
	@if [ -z "$(t)" ]; then echo 'Usage: make -f betteragents.mk journal t="journal entry text"'; exit 1; fi
	docker exec $(RAG_CONTAINER) python journal.py "$(t)"

reset-db: ## Reset the vector database (drops all indexed data)
	docker exec $(RAG_CONTAINER) ./reset.sh

# --- Helpers ---

test: ## Run end-to-end RAG test and save output to test_result.log
	@echo "Running rag/test.sh, writing output to test_result.log"
	@bash rag/test.sh > test_result.log 2>&1
	@echo "Test results written to $(PWD)/test_result.log"

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

.PHONY: up down logs ingest ask retrieve translate learn remember vague journal reset-db test help
.DEFAULT_GOAL := help
