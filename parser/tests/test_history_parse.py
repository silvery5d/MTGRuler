"""Tests for history.parse_version — uses a tiny synthetic CR text."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch
from history import parse_version as pv


def test_parse_version_uses_existing_parser(monkeypatch, tmp_path):
    sample_text = """1. Game Concepts

100. General

100.1. These Magic rules apply to any Magic game.
100.2. Some rules apply to specific cases.

Glossary

A bunch of terms here..."""

    monkeypatch.setattr(pv, "PARSED_DIR", tmp_path)
    monkeypatch.setattr(pv, "fetch_cr_text", lambda code, force=False: sample_text)

    chapters = pv.parse_version("TEST")
    assert "1" in chapters
    assert any(r["rule_ref"] == "100.1" for r in chapters["1"])


def test_to_rule_text_records():
    chapters = {
        "1": [{"rule_ref": "100.1", "text": "Hello"}],
        "2": [{"rule_ref": "200.1", "text": "World"}],
    }
    records = pv.to_rule_text_records(chapters)
    assert len(records) == 2
    assert records[0]["text_cn"] is None
    assert records[0]["chapter"] == "1"
