import json

def test_align_entries():
    """Test EN/CN alignment by rule_ref."""
    from preprocess import align_entries

    en_chapters = {
        "1": [
            {"rule_ref": "100.1", "text": "These Magic rules apply..."},
            {"rule_ref": "100.2", "text": "To play, each player needs..."},
            {"rule_ref": "101.1", "text": "Whenever a card's text..."},
        ]
    }
    cn_chapters = {
        "1": [
            {"rule_ref": "100.1", "text": "这些万智牌规则适用于..."},
            {"rule_ref": "100.2", "text": "进行游戏时..."},
        ]
    }
    aligned = align_entries(en_chapters, cn_chapters)

    assert len(aligned) == 3
    assert aligned[0]["rule_ref"] == "100.1"
    assert aligned[0]["text_en"] == "These Magic rules apply..."
    assert aligned[0]["text_cn"] == "这些万智牌规则适用于..."
    assert aligned[0]["chapter"] == "1"
    assert aligned[2]["rule_ref"] == "101.1"
    assert aligned[2]["text_cn"] == ""


def test_group_by_chapter():
    """Test grouping aligned entries back by chapter."""
    from preprocess import align_entries, group_by_chapter

    en = {"1": [{"rule_ref": "100.1", "text": "A"}],
          "2": [{"rule_ref": "200.1", "text": "B"}]}
    cn = {"1": [{"rule_ref": "100.1", "text": "甲"}],
          "2": [{"rule_ref": "200.1", "text": "乙"}]}

    aligned = align_entries(en, cn)
    grouped = group_by_chapter(aligned)

    assert "1" in grouped
    assert "2" in grouped
    assert grouped["1"][0]["text_en"] == "A"
    assert grouped["2"][0]["text_cn"] == "乙"
