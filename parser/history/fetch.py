"""Fetch CR text from Academy Ruins API and hudecekpetr.cz archive, with disk caching."""

import json
from pathlib import Path

import httpx

API_BASE = "https://api.academyruins.com"
ARCHIVE_BASE = "https://hudecekpetr.cz/other/rulebooks"
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


# Mapping from version ID to hudecekpetr.cz archive filename.
# Used for pre-AKH versions and early rulebooks that Academy Ruins doesn't have.
ARCHIVE_FILES: dict[str, str] = {
    # Pre-CR era (narrative rulebooks)
    "ALPHA": "rulebook-alpha-1993/index.html",
    "UNLIMITED": "rulebook-unlimited-1993-12-01.txt",
    "REVISED": "rulebook-revised-1994-04.txt",
    "5TH": "rulebook-fifth-1997-03/",
    # CR era — hudecekpetr has dated files instead of set codes
    "CR-1999-04": "comprehensive-1999-04-23.txt",
    "CR-2001-07": "comprehensive-2001-07-23.txt",
    "CR-2001-09": "comprehensive-2001-09-24.txt",
    "CR-2002-02": "comprehensive-2002-02-20.txt",
    "CR-2002-10": "comprehensive-2002-10-07.txt",
    "CR-2003-03": "comprehensive-2003-03-15.txt",
    "CR-2004-10": "comprehensive-2004-10-01.txt",
    "CR-2005-02": "comprehensive-2005-02-01.txt",
    "CR-2005-08": "comprehensive-2005-08-01.txt",
    "CR-2005-10": "comprehensive-2005-10-01.txt",
    "CR-2006-01": "comprehensive-2006-01-04.txt",
    "CR-2006-02": "comprehensive-2006-02-01.txt",
    "CR-2006-05": "comprehensive-2006-05-01.txt",
    "CR-2006-07": "comprehensive-2006-07-15.txt",
    "CR-2006-10": "comprehensive-2006-10-01.txt",
    "CR-2007-02": "comprehensive-2007-02-01.txt",
    "CR-2007-05": "comprehensive-2007-05-01.txt",
    "CR-2007-07": "comprehensive-2007-07-13.txt",
    "CR-2007-09": "comprehensive-2007-09-07.txt",
    "CR-2007-10": "comprehensive-2007-10-01.txt",
    "CR-2008-02": "comprehensive-2008-02-01.txt",
    "CR-2008-05": "comprehensive-2008-05-01.txt",
    "CR-2008-07": "comprehensive-2008-07-15.txt",
    "CR-2008-10": "comprehensive-2008-10-01.txt",
    "CR-2009-02": "comprehensive-2009-02-01.txt",
    "CR-2009-05": "comprehensive-2009-05-01.txt",
    "CR-2009-07": "comprehensive-2009-07-08.txt",
    "CR-2009-09": "comprehensive-2009-09-04.txt",
    "CR-2009-10": "comprehensive-2009-10-05.txt",
    "CR-2010-02": "comprehensive-2010-02-01.txt",
    "CR-2010-04": "comprehensive-2010-04-23.txt",
    "CR-2010-06": "comprehensive-2010-06-18.txt",
    "CR-2010-07": "comprehensive-2010-07-16.txt",
    "CR-2010-10": "comprehensive-2010-10-01.txt",
    "CR-2011-02": "comprehensive-2011-02-04.txt",
    "CR-2011-04": "comprehensive-2011-04-01.txt",
    "CR-2011-05": "comprehensive-2011-05-01.txt",
    "CR-2011-06": "comprehensive-2011-06-17.txt",
    "CR-2011-07": "comprehensive-2011-07-15.txt",
    "CR-2011-09": "comprehensive-2011-09-30.txt",
    "CR-2012-02": "comprehensive-2012-02-01.txt",
    "CR-2012-05": "comprehensive-2012-05-01.txt",
    "CR-2012-06": "comprehensive-2012-06-01.txt",
    "CR-2012-07": "comprehensive-2012-07-01.txt",
    "CR-2012-10": "comprehensive-2012-10-01.txt",
    "CR-2013-02": "comprehensive-2013-02-01.txt",
    "CR-2013-04": "comprehensive-2013-04-29.txt",
    "CR-2013-07": "comprehensive-2013-07-11.txt",
    "CR-2013-09": "comprehensive-2013-09-27.txt",
    "CR-2013-11": "comprehensive-2013-11-01.txt",
    "CR-2014-02": "comprehensive-2014-02-01.txt",
    "CR-2015-01": "comprehensive-2015-01-23.txt",
    "CR-2015-03": "comprehensive-2015-03-27.txt",
}


def fetch_cr_text(set_code: str, force: bool = False) -> str:
    """Fetch raw CR text for a version, with disk caching.

    Tries Academy Ruins first, then falls back to hudecekpetr.cz archive.
    """
    set_code = set_code.upper()
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = VERSIONS_DIR / f"{set_code}.txt"

    if cache_file.exists() and not force:
        return cache_file.read_text(encoding="utf-8")

    # Try hudecekpetr archive first (for pre-AKH and dated versions)
    if set_code in ARCHIVE_FILES:
        filename = ARCHIVE_FILES[set_code]
        url = f"{ARCHIVE_BASE}/{filename}"
        with httpx.Client(timeout=60.0, follow_redirects=True) as c:
            resp = c.get(url)
            resp.raise_for_status()
            text = resp.text
        cache_file.write_text(text, encoding="utf-8")
        return text

    # Academy Ruins API
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
