"""Tests for history.walk_versions module — mock fetch_diff to test chain walking."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch
from history import walk_versions


def test_walk_includes_pre_akh_and_chain(monkeypatch, tmp_path):
    monkeypatch.setattr(walk_versions, "VERSIONS_INDEX", tmp_path / "idx.json")

    latest = {
        "sourceCode": "B", "sourceSet": "Beta",
        "destCode": "C", "destSet": "Charlie",
        "creationDay": "2024-01-01",
        "nav": {"prevSourceCode": "A"},
    }
    diff_AB = {
        "sourceCode": "A", "sourceSet": "Alpha",
        "destCode": "B", "destSet": "Beta",
        "creationDay": "2023-01-01",
        "nav": {"prevSourceCode": None},
    }

    monkeypatch.setattr(walk_versions, "fetch_latest_diff_with_nav", lambda: latest)
    monkeypatch.setattr(walk_versions, "fetch_diff",
                        lambda old, new: diff_AB if (old, new) == ("A", "B") else (_ for _ in ()).throw(ValueError()))

    chain = walk_versions.walk_all_versions(max_steps=10)
    codes = [v["set_code"] for v in chain]
    # Pre-AKH known sets are prepended, then chain A→B→C follows
    assert "6ED" in codes
    assert "A" in codes
    assert "B" in codes
    assert "C" in codes
    # Last entry should have no next
    assert chain[-1]["set_code"] == "C"
    assert chain[-1]["next_set_code"] is None
    # 6ED should be before A
    assert codes.index("6ED") < codes.index("A")
