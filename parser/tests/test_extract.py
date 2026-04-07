import json

def test_build_extraction_prompt():
    """Test that the extraction prompt includes rule entries."""
    from extract import build_extraction_prompt

    entries = [
        {"rule_ref": "702.9", "text_en": "Flying", "text_cn": "飞行", "chapter": "7"},
        {"rule_ref": "702.9a", "text_en": "A creature with flying...", "text_cn": "具有飞行异能的生物...", "chapter": "7"},
    ]
    prompt = build_extraction_prompt(entries, chapter="7")
    assert "702.9" in prompt
    assert "Flying" in prompt
    assert "飞行" in prompt


def test_parse_llm_response():
    """Test parsing a simulated LLM JSON response."""
    from extract import parse_llm_response

    raw = json.dumps({
        "concepts": [
            {
                "id": "keyword.flying",
                "name_en": "Flying",
                "name_cn": "飞行",
                "type": "Keyword",
                "rule_ref": "702.9",
                "definition_en": "A creature with flying can't be blocked except by creatures with flying or reach.",
                "definition_cn": "具有飞行异能的生物不能被不具有飞行或延势的生物阻挡。",
                "complexity": 2,
                "design_notes": "Core evasion mechanic"
            }
        ],
        "relations": [
            {
                "source_id": "keyword.flying",
                "target_id": "keyword.reach",
                "type": "INTERACTS_WITH",
                "rule_ref": "702.9a",
                "description": "Reach allows blocking creatures with flying"
            }
        ]
    })

    concepts, relations = parse_llm_response(raw)
    assert len(concepts) == 1
    assert concepts[0]["id"] == "keyword.flying"
    assert concepts[0]["type"] == "Keyword"
    assert len(relations) == 1
    assert relations[0]["type"] == "INTERACTS_WITH"


def test_parse_llm_response_handles_markdown_fence():
    """LLM sometimes wraps JSON in ```json ... ``` — parser should handle it."""
    from extract import parse_llm_response

    raw = '```json\n{"concepts": [], "relations": []}\n```'
    concepts, relations = parse_llm_response(raw)
    assert concepts == []
    assert relations == []
