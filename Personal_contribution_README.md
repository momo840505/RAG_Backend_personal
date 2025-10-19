# Personal Contribution — Wei Ting Mo (momo0840505)

This fork shows my own contributions to our group backend project.

## Tasks I owned
- Backend **testing & verification baseline**: health checks, `/api/search` success+errors, P95 latency smoke, DB row-count, URL usability.
- **API**: added `/api/chat` and `/api/feedback` and registered routes in `api/urls.py`.
- **Minimal PGVector ingestion**: `scripts/ingest_sample.py` to ensure semantic context exists for tests/demos.
- **Dependencies & container startup**: aligned LangChain/PGVector versions; updated `docker-compose`/env to improve “clone-and-run”.

## Evidence (commits authored by me)
- Backend testing modules … (healthz, search success+errors, P95 latency, DB row-count)
- Add `/api/chat` and `/api/feedback` endpoints; register routes in `api/urls.py`
- feat(scripts): minimal PGVector ingestion; seed sample docs
- fix: align LangChain deps, update PGVector usage, add compose override; ignore bytecode

🔍 View only my commits on main repo:  
https://github.com/RoGWilson/RAG_Backend/commits?author=momo0840505

> Files likely touched: `tests/`, `api/`, `scripts/ingest_sample.py`, `requirements.txt`, `docker-compose.override.yml`, `README Testing modules.md`.

## Notes
My early baseline was consolidated by teammates into the final unit/E2E tests so the pipeline and tests stay consistent.
