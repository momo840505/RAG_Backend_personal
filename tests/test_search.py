# tests/test_search.py
"""
Purpose
-------
End-to-end happy-path tests for /api/search using a *structured* request.

Notes
-----
- Use a *real* ACYWA metadataId so the backend validation passes.
- We assert URL composition, not the front-end rendering.
"""
import json
from urllib.parse import urlparse, parse_qs

def _qs(url):
    return {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}

def test_search_minimal(client):
    # real metadataId; year/area chosen from a known-good example
    payload = {"metadataId": "cm1eeg7aacf1ikh34d25j35dc", "year": 2010, "area_level": "SA3"}
    resp = client.post("/api/search/", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 200, resp.content
    qs = _qs(resp.json()["url"])
    # core params present
    assert qs["metadataId"] == "cm1eeg7aacf1ikh34d25j35dc"
    assert qs["collectionYear"] == "2010"
    assert qs["statisticalArea"] == "SA3"

def test_search_with_region_passthrough(client):
    payload = {
        "metadataId": "cm0vzjaqdz68tkh34n38fxf9l",  # another valid id
        "year": 2019,
        "area_level": "STATE",
        "sa4Name": "Perth - South East",  # UI hint; site may accept or ignore; we ensure it's forwarded
    }
    resp = client.post("/api/search/", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 200
    qs = _qs(resp.json()["url"])
    assert qs.get("metadataId") == "cm0vzjaqdz68tkh34n38fxf9l"
    assert qs.get("collectionYear") == "2019"
    assert qs.get("statisticalArea") == "STATE"
    assert qs.get("sa4Name") == "Perth - South East"
