"""Academy Ruins API client and on-disk caching for CR text + diffs."""

import json
from pathlib import Path

import httpx

API_BASE = "https://api.academyruins.com"
DATA_DIR = Path(__file__).parent.parent / "data" / "history"
VERSIONS_DIR = DATA_DIR / "versions"
DIFFS_DIR = DATA_DIR / "diffs"

_client: httpx.Client | None = None


def _get_client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(
            base_url=API_BASE,
            timeout=60.0,
            follow_redirects=True,
            headers={"User-Agent": "MTGRuler-history/0.1"},
        )
    return _client


def fetch_cr_text(set_code: str, force: bool = False) -> str:
    """Fetch raw CR text for a set code, with disk caching.

    Returns the text content. Caches as parser/data/history/versions/{set_code}.txt.
    Raises httpx.HTTPStatusError on API errors.
    """
    set_code = set_code.upper()
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = VERSIONS_DIR / f"{set_code}.txt"

    if cache_file.exists() and not force:
        return cache_file.read_text(encoding="utf-8")

    client = _get_client()
    resp = client.get(f"/file/cr/{set_code}", params={"format": "txt"})
    resp.raise_for_status()
    text = resp.text
    cache_file.write_text(text, encoding="utf-8")
    return text


def fetch_diff(old_set: str, new_set: str, force: bool = False) -> dict:
    """Fetch the structured diff between two adjacent CR versions.

    Caches as parser/data/history/diffs/{old}_{new}.json.
    Returns the diff dict, or raises if Academy Ruins has no diff for this pair.
    """
    old_set = old_set.upper()
    new_set = new_set.upper()
    DIFFS_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = DIFFS_DIR / f"{old_set}_{new_set}.json"

    if cache_file.exists() and not force:
        return json.loads(cache_file.read_text(encoding="utf-8"))

    client = _get_client()
    resp = client.get("/diff/cr", params={"old": old_set, "new": new_set, "nav": "true"})
    resp.raise_for_status()
    data = resp.json()
    if "detail" in data and "No diff" in data.get("detail", ""):
        raise ValueError(f"No diff between {old_set} and {new_set}")
    cache_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def fetch_latest_diff_with_nav() -> dict:
    """Fetch the latest diff (no params), used as the entry point for walking
    the version chain backward via prevSourceCode."""
    client = _get_client()
    resp = client.get("/diff/cr", params={"nav": "true"})
    resp.raise_for_status()
    return resp.json()
