# scripts/import_vectors.sh

#!/usr/bin/env bash
# Purpose
# -------
# Import the Postgres vector backup into the running "pgvector-db" container,
# without requiring psql to be installed on the host.
#
# Usage
#   ./scripts/import_vectors.sh ./vector_backup.sql
#
# What it does
# ------------
# - Waits for the container's Postgres to be ready (docker exec pg_isready)
# - Streams the SQL into the container's psql
# - Prints row count from langchain_pg_embedding at the end

set -euo pipefail
FILE="${1:-vector_backup.sql}"
echo "Waiting for 'pgvector-db'..."
for i in {1..60}; do
  if docker exec pgvector-db pg_isready -U postgres -d vector_db >/dev/null 2>&1; then break; fi
  sleep 2
  if [ $i -eq 60 ]; then echo "pgvector-db not ready"; exit 1; fi
done
echo "Dropping old tables (if any) ..."
docker exec pgvector-db psql -U postgres -d vector_db -c "DROP TABLE IF EXISTS langchain_pg_embedding CASCADE;" >/dev/null 2>&1 || true
docker exec pgvector-db psql -U postgres -d vector_db -c "DROP TABLE IF EXISTS langchain_pg_collection CASCADE;" >/dev/null 2>&1 || true
echo "Importing $FILE ..."
docker exec -i pgvector-db psql -v ON_ERROR_STOP=1 --echo-errors -U postgres -d vector_db < "$FILE"
echo "Verifying row count ..."
docker exec pgvector-db psql -U postgres -d vector_db -c "SELECT COUNT(*) AS rows FROM langchain_pg_embedding;"