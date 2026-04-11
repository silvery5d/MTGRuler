"""Walk the Academy Ruins CR version chain backward to enumerate all set codes."""

import json
from pathlib import Path

from .fetch import fetch_diff, fetch_latest_diff_with_nav, DATA_DIR

VERSIONS_INDEX = DATA_DIR / "versions_index.json"


def walk_all_versions(max_steps: int = 200) -> list[dict]:
    """Enumerate all CR versions by walking backward through the diff chain.

    Returns a list of version dicts ordered chronologically (oldest first):
        [{"set_code": "ODY", "set_name": "Odyssey", "release_date": "2001-09-24",
          "prev_set_code": null, "next_set_code": "TOR"}, ...]

    Caches the result to parser/data/history/versions_index.json.
    """
    latest = fetch_latest_diff_with_nav()
    chain: list[dict] = []

    current = {
        "set_code": latest["destCode"],
        "set_name": latest["destSet"],
        "release_date": latest.get("creationDay"),
        "prev_set_code": latest["sourceCode"],
        "next_set_code": None,
    }
    chain.append(current)

    chain.append({
        "set_code": latest["sourceCode"],
        "set_name": latest["sourceSet"],
        "release_date": None,
        "prev_set_code": latest.get("nav", {}).get("prevSourceCode"),
        "next_set_code": latest["destCode"],
    })

    steps = 0
    while chain[-1]["prev_set_code"] and steps < max_steps:
        prev_code = chain[-1]["prev_set_code"]
        curr_code = chain[-1]["set_code"]
        try:
            diff = fetch_diff(prev_code, curr_code)
        except (ValueError, Exception):
            break

        chain[-1]["release_date"] = diff.get("creationDay")
        chain.append({
            "set_code": diff["sourceCode"],
            "set_name": diff["sourceSet"],
            "release_date": None,
            "prev_set_code": diff.get("nav", {}).get("prevSourceCode"),
            "next_set_code": curr_code,
        })
        steps += 1

    chain.reverse()
    VERSIONS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    VERSIONS_INDEX.write_text(json.dumps(chain, ensure_ascii=False, indent=2), encoding="utf-8")
    return chain


def load_versions_index() -> list[dict]:
    """Load the cached versions index, or enumerate fresh if missing."""
    if VERSIONS_INDEX.exists():
        return json.loads(VERSIONS_INDEX.read_text(encoding="utf-8"))
    return walk_all_versions()
