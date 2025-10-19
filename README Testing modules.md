# Testing modules for backend

## Scope and goals

* Validate the backend’s API contract for `/api/healthz` and `/api/search`.
* Enforce the **no‑hallucination** policy (return a clear message when no visualisation is available).
* Guard basic **performance** (latency smoke test, ~P95 < 3s over 20 requests).
* Verify that the **vector database is correctly imported** (~189k rows in `langchain_pg_embedding`).
* Provide a **one‑click, containerised** workflow (Docker Compose).

## What’s included

* **Health test**

  * `tests/test_healthz.py` — `/api/healthz` returns 200 and DB status (`ok|down`).
* **/api/search – success path**

  * `tests/test_search.py` — Deep‑link URL composition contains required keys (`metadataId`, `collectionYear`, `statisticalArea`, optional `sex/age/sa4Name`).
  * `api/tests/test_api_search_ok.py` — API echoes `metadataId` and returns a valid URL.
* **/api/search – error & policy**

  * `api/tests/test_api_search_errors.py` — invalid `year` → HTTP 400; natural‑language query with no match → HTTP 200 + clear **no‑match** message.
* **Latency smoke**

  * `api/tests/test_perf_search_latency.py` — ~P95 latency under 3000 ms across 20 requests (warm‑up included).
* **Database import verification**

  * `tests/db/test_embeddings_count.py` — row count in `langchain_pg_embedding` is in the expected band (180k–200k).

## Key implementation notes

* **No hallucination**: the search endpoint returns `{"message":"No matching dataset/visualisation found."}` for unresolved natural‑language queries.
* **Structured requests**: when a valid `metadataId` is supplied, the backend composes the Atlas deep‑link URL with the correct query parameters.
* **Input validation**: non‑numeric `year` returns HTTP 400; obviously invalid `metadataId` (e.g., placeholders) is rejected to avoid misleading blank maps.

## One‑click run (PowerShell)

```powershell
# Project root
cd C:\Users\<you>\Documents\GitHub\RAG_Backend

# 1) Start / restart
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build

# 2) (First‑time) import vectors and verify row count
$cid = (docker compose ps -q pgvector-db)
docker cp .\vector_backup.sql "$cid`:/tmp/vector_backup.sql"
docker exec -i "$cid" bash -lc "psql -v ON_ERROR_STOP=1 --echo-errors -U postgres -d vector_db -f /tmp/vector_backup.sql"
docker exec "$cid" psql -U postgres -d vector_db -c "SELECT COUNT(*) AS rows FROM langchain_pg_embedding;"

# 3) Run the whole suite (health, API, latency, row‑count)
docker compose exec backend bash -lc "pip install -q pytest pytest-django && pytest -q"
```

## Run subsets

```powershell
# Health only
docker compose exec backend bash -lc "pytest -q tests/test_healthz.py"

# API behaviour (success + errors)
docker compose exec backend bash -lc "pytest -q tests/test_search.py api/tests/test_api_search_ok.py api/tests/test_api_search_errors.py"

# Latency smoke
docker compose exec backend bash -lc "pytest -q api/tests/test_perf_search_latency.py"

# Row‑count verification
docker compose exec backend bash -lc "pytest -q tests/db/test_embeddings_count.py"
```

## Troubleshooting quick list

* **`C: invalid compose project`** → In `docker-compose.yml` use `- "${DATA_DIR}:/data"` (with quotes) and set `DATA_DIR` with forward slashes in `.env`.
* **`relation ... does not exist`** → Re‑import vectors (Step 2) and re‑run tests.
* **Blank map when opening URL** → Use a real `metadataId` (e.g., `cm...`/`cl...`). Some Atlas pages show a base map until a region is selected; pass region code if the site supports it.
* **`pytest: command not found`** → Install once: `docker compose exec backend bash -lc "pip install -q pytest pytest-django"`.

## Files added/changed (testing modules)

* `api/views.py` — search logic (validation, no‑match policy, URL composer) and `/api/healthz`.
* `api/urls.py` — routes for `healthz` and `search`.
* `tests/` — health & URL‑composition tests; DB row‑count test.
* `api/tests/` — API success, API errors, latency smoke.
* `pytest.ini` — config for Django tests discovery.
* `scripts/import_vectors.sh` — wait→drop→import→count.

## Exit criteria

* `pytest -q` → **all green**.
* Opening any returned `url` loads the Atlas page with correct query parameters.
* DB row count ≈ **189k** after import.
