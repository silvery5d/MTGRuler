"""Tests for history.detect_spikes — focuses on find_spikes pure function."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from history.detect_spikes import find_spikes, _get_nested


def test_get_nested():
    assert _get_nested({"a": {"b": {"c": 5}}}, "a.b.c") == 5.0
    assert _get_nested({"a": {"b": 0}}, "a.b") == 0.0
    assert _get_nested({}, "x.y") == 0.0


def make_metric(set_code, uc):
    return {
        "set_code": set_code,
        "set_name": set_code,
        "release_date": "2020-01-01",
        "scale": {"rule_count": 100},
        "graph": {"concept_count": 100, "relation_count": 100},
        "cognitive": {"uc_total": uc},
        "mechanic": {"keyword_count": 50},
    }


def test_find_spikes_detects_outlier():
    metrics = [
        make_metric("V1", 1000),
        make_metric("V2", 1010),
        make_metric("V3", 1020),
        make_metric("V4", 1030),
        make_metric("V5", 1500),
        make_metric("V6", 1510),
    ]
    spikes = find_spikes(metrics)
    spiked_codes = [s["set_code"] for s in spikes]
    assert "V5" in spiked_codes


def test_find_spikes_handles_short_series():
    assert find_spikes([]) == []
    assert find_spikes([make_metric("V1", 100)]) == []
