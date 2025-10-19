# tests/conftest.py

"""
Purpose
-------
Pytest configuration for Django tests.

What it does
------------
- Ensures the Django test client host ("testserver") is accepted by ALLOWED_HOSTS,
  so requests like client.get("/api/healthz/") won't be blocked in tests.

Notes
-----
- Keep this file small and deterministic; avoid mutating global state beyond
  what's necessary for test isolation.
"""
import pytest

@pytest.fixture(autouse=True)
def _allow_testserver(settings):
    # Django test client uses host "testserver".
    # Make sure it is always allowed during tests.
    settings.ALLOWED_HOSTS = list(getattr(settings, "ALLOWED_HOSTS", [])) + ["testserver"]
