"""Tests for history.fetch module — focuses on cache logic without hitting network."""

import json
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tempfile
import pytest
from unittest.mock import patch, MagicMock

from history import fetch as fetch_mod


def test_fetch_cr_text_uses_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_mod, "VERSIONS_DIR", tmp_path)
    cache_file = tmp_path / "ODY.txt"
    cache_file.write_text("cached content", encoding="utf-8")

    mock_client = MagicMock()
    monkeypatch.setattr(fetch_mod, "_get_client", lambda: mock_client)

    result = fetch_mod.fetch_cr_text("ODY")
    assert result == "cached content"
    mock_client.get.assert_not_called()


def test_fetch_cr_text_writes_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_mod, "VERSIONS_DIR", tmp_path)
    mock_resp = MagicMock()
    mock_resp.text = "fresh content"
    mock_resp.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    monkeypatch.setattr(fetch_mod, "_get_client", lambda: mock_client)

    result = fetch_mod.fetch_cr_text("XYZ")
    assert result == "fresh content"
    assert (tmp_path / "XYZ.txt").read_text(encoding="utf-8") == "fresh content"


def test_fetch_diff_raises_on_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(fetch_mod, "DIFFS_DIR", tmp_path)
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"detail": "No diff between these set codes found"}
    mock_resp.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    monkeypatch.setattr(fetch_mod, "_get_client", lambda: mock_client)

    with pytest.raises(ValueError, match="No diff"):
        fetch_mod.fetch_diff("FOO", "BAR")
