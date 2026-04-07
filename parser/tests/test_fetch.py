# parser/tests/test_fetch.py
import json
from pathlib import Path


def test_parse_en_rules_structure():
    """Test that EN rules text can be parsed into chapter dict."""
    sample = """Magic: The Gathering Comprehensive Rules

These rules are effective as of...

Contents
1. Game Concepts
100. General
101. The Magic Golden Rules

1. Game Concepts

100. General

100.1. These Magic rules apply to any Magic game with two or more players...

100.2. To play, each player needs their own deck...

101. The Magic Golden Rules

101.1. Whenever a card's text directly contradicts these rules, the card takes precedence...

101.2. When a rule or effect allows or directs something to happen...

2. Parts of a Card

200. General

200.1. The parts of a card are name, mana cost...

Glossary

Abandon — ...
"""
    from fetch_rules import parse_en_chapters
    chapters = parse_en_chapters(sample)

    assert "1" in chapters, "Chapter 1 should exist"
    assert "2" in chapters, "Chapter 2 should exist"
    assert any("100.1" in entry["rule_ref"] for entry in chapters["1"])
    assert any("101.1" in entry["rule_ref"] for entry in chapters["1"])
    for entry in chapters["1"]:
        assert "rule_ref" in entry
        assert "text" in entry
        assert len(entry["text"]) > 0
