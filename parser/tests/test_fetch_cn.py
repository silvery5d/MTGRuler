# parser/tests/test_fetch_cn.py
"""Tests for CN wiki scraping functions."""


SAMPLE_HTML = """
<div class="page">
<h2 class="sectionedit2" id="总则_general">100. 总则 General</h2>
<p>
<a name="cr100-1" class="abookmark"><img src="/_media/bmanchor.gif" width="1" height="1" /></a>100.1. These Magic rules apply to any Magic game with two or more players, including two-player games and multiplayer games.<br/>

100.1. 这些万智牌规则适用于任何两位或是更多牌手的万智牌游戏，包含双人游戏和多人游戏。
</p>

<p>
<a name="cr100-1a" class="abookmark"><img src="/_media/bmanchor.gif" width="1" height="1" /></a>100.1a A two-player game is a game that begins with only two players.<br/>

100.1a 双人游戏指在游戏开始时只有两位牌手的游戏。
</p>

<p>
<a name="cr100-2" class="abookmark"><img src="/_media/bmanchor.gif" width="1" height="1" /></a>100.2. To play, each player needs their own deck of traditional Magic cards.<br/>

100.2. 进行游戏时，每位牌手需要拥有自己的传统万智牌套牌。
</p>
</div>
"""


def test_parse_cn_page():
    """Test parsing a CN wiki HTML page into rule entries."""
    from fetch_rules import parse_cn_page

    entries = parse_cn_page(SAMPLE_HTML)

    assert len(entries) == 3
    assert entries[0]["rule_ref"] == "100.1"
    assert "万智牌" in entries[0]["text"]
    assert "These Magic rules" not in entries[0]["text"]

    assert entries[1]["rule_ref"] == "100.1a"
    assert "双人游戏" in entries[1]["text"]

    assert entries[2]["rule_ref"] == "100.2"
    assert "套牌" in entries[2]["text"]


def test_parse_cn_page_extracts_chinese_only():
    """Test that parse_cn_page extracts only the Chinese text, not English."""
    from fetch_rules import parse_cn_page

    entries = parse_cn_page(SAMPLE_HTML)
    for entry in entries:
        # Should not contain the English sentence
        assert "two-player game" not in entry["text"]
        assert "Magic rules apply" not in entry["text"]


def test_parse_cn_page_empty_html():
    """Test that parse_cn_page handles empty/no-rules HTML gracefully."""
    from fetch_rules import parse_cn_page

    entries = parse_cn_page("<html><body><p>No rules here</p></body></html>")
    assert entries == []
