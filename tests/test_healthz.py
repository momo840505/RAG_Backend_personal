# tests/test_healthz.py

"""
Purpose
-------
Basic readiness/health check test for the backend.

What it validates
-----------------
- /api/healthz/ returns HTTP 200
- JSON payload includes {"status":"ok", "db":"ok|down"}

Why this matters
----------------
CI and reviewers can quickly verify the service is alive and whether the DB is reachable.
"""
def test_healthz(client):
    resp = client.get("/api/healthz/")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "ok"
    # DB may be "down" if Postgres isn't wired for unit tests; the endpoint must not crash.
    assert body.get("db") in {"ok", "down"}
