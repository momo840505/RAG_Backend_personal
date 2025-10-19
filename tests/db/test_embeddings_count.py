# tests/db/test_embeddings_count.py

"""
Purpose
-------
Database post-import validation: ensure the embeddings table contains
roughly 189k rows after importing `vector_backup.sql`.

What it validates
-----------------
- Table `langchain_pg_embedding` exists and has 180k–200k rows.

How to import (from project root)
---------------------------------
1) Start services:
   docker compose -f docker-compose.yml -f docker-compose.data.yml up -d --build
2) Place vector_backup.sql at repo root and import:
   $cid = (docker compose ps -q pgvector-db)
   docker cp ".\\vector_backup.sql" "$cid`:/tmp/vector_backup.sql"
   docker exec -i "$cid" bash -lc "psql -v ON_ERROR_STOP=1 -U postgres -d vector_db -f /tmp/vector_backup.sql"
"""
import os, psycopg2, pytest

@pytest.mark.parametrize("table", ["langchain_pg_embedding"])
def test_embedding_table_rowcount(table):
    conn = psycopg2.connect(
        host=os.getenv("PG_HOST", "pgvector-db"),
        port=int(os.getenv("PG_PORT", "5432")),
        dbname=os.getenv("PG_DB", "vector_db"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "team_7"),
    )
    cur = conn.cursor()
    cur.execute(f"SELECT count(*) FROM {table};")
    (n,) = cur.fetchone()
    cur.close(); conn.close()

    # Expect around 189,270 rows according to the client dump and meeting notes.
    assert 180_000 <= n <= 200_000, f"Row count {n} outside expected range for {table}"
