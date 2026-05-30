#!/usr/bin/env bash

set -euo pipefail

# Reset the rag-backend-db Postgres instance completely from inside the rag-backend-app container.
# This drops and recreates the public schema and re-adds the pgvector extension.

DB_HOST="${DB_HOST:-db}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-password}"

export PGPASSWORD="$DB_PASSWORD"

echo "Resetting database '$DB_NAME' on host '$DB_HOST'..."

psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "DROP SCHEMA IF EXISTS public CASCADE;"
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "CREATE SCHEMA public;"
psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "Database reset complete."

