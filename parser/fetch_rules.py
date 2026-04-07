"""Fetch and parse MTG Comprehensive Rules (EN + CN)."""

import re
import json
import httpx
from bs4 import BeautifulSoup
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
RAW_DIR = DATA_DIR / "raw"

EN_RULES_URL = "https://media.wizards.com/2025/downloads/MagicCompRules%2020250404.txt"
CN_WIKI_BASE = "https://wiki.mtgjudge.cn/cr"
CN_CHAPTER_PAGES = list(range(1, 10))  # /cr:1 through /cr:9
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def fetch_en_rules(force: bool = False) -> str:
    """Download the official EN Comprehensive Rules text file."""
    out = RAW_DIR / "comp_rules_en.txt"
    if out.exists() and not force:
        return out.read_text(encoding="utf-8")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    resp = httpx.get(EN_RULES_URL, follow_redirects=True, timeout=60)
    resp.raise_for_status()
    text = resp.content.decode("utf-8-sig")
    # Normalize line endings: \r\n -> \n, then lone \r -> \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    out.write_text(text, encoding="utf-8")
    return text


def parse_en_chapters(text: str) -> dict[str, list[dict]]:
    """
    Parse EN rules text into a dict keyed by chapter number.
    Each value is a list of {"rule_ref": "100.1a", "text": "..."}.
    """
    chapters: dict[str, list[dict]] = {}
    lines = text.split("\n")

    in_rules = False
    has_rules = False
    current_chapter = None

    # Top-level chapters: "1. Game Concepts", "2. Parts of a Card", etc.
    chapter_pattern = re.compile(r"^(\d{1,2})\.\s+[A-Z]")
    # Section headings: "100. General", "101. The Magic Golden Rules", etc.
    section_pattern = re.compile(r"^(\d{3})\.\s+(.+)$")
    # Individual rules: "100.1. text" or "100.1a text" (subrules have no trailing dot)
    rule_pattern = re.compile(r"^(\d{3}\.\d+[a-z]?)\.?\s+(.+)")

    current_rule_ref = None
    current_rule_lines: list[str] = []

    def flush_rule():
        nonlocal current_rule_ref, current_rule_lines, has_rules
        if current_rule_ref and current_chapter is not None:
            chapters.setdefault(current_chapter, []).append({
                "rule_ref": current_rule_ref,
                "text": " ".join(current_rule_lines).strip(),
            })
            has_rules = True
        current_rule_ref = None
        current_rule_lines = []

    for line in lines:
        stripped = line.strip()

        # Stop at the Glossary section (but only after we've parsed actual rules,
        # since "Glossary" also appears in the Table of Contents).
        if stripped.lower() == "glossary" and has_rules:
            flush_rule()
            break

        # Check for top-level chapter heading (e.g. "1. Game Concepts")
        ch_match = chapter_pattern.match(stripped)
        if ch_match and not rule_pattern.match(stripped) and not section_pattern.match(stripped):
            flush_rule()
            current_chapter = ch_match.group(1)
            in_rules = True
            continue

        # Skip section headings (e.g. "100. General") — they don't change chapter
        if section_pattern.match(stripped) and not rule_pattern.match(stripped):
            flush_rule()
            continue

        if not in_rules:
            continue

        rule_match = rule_pattern.match(stripped)
        if rule_match:
            flush_rule()
            current_rule_ref = rule_match.group(1)
            current_rule_lines = [rule_match.group(2)]
        elif current_rule_ref and stripped:
            current_rule_lines.append(stripped)

    flush_rule()
    return chapters


# ---------------------------------------------------------------------------
# CN rules (scraped from wiki.mtgjudge.cn)
# ---------------------------------------------------------------------------

# Matches rule refs like "100.1." or "100.1a" at the start of a line.
_CN_RULE_RE = re.compile(r"^(\d{3}\.\d+[a-z]?)\.?\s+(.+)", re.DOTALL)


def parse_cn_page(html: str) -> list[dict]:
    """
    Parse a CN wiki HTML page into a list of {"rule_ref": "100.1", "text": "..."}.

    Each rule is a <p> containing an <a class="abookmark">, followed by
    English text, a <br/>, then Chinese text.  We extract only the Chinese.
    """
    soup = BeautifulSoup(html, "lxml")
    entries: list[dict] = []

    for p_tag in soup.find_all("p"):
        anchor = p_tag.find("a", class_="abookmark")
        if anchor is None:
            continue

        # Get the full text content, split on the <br/> tag.
        # The structure is: [anchor img] EN_LINE <br/> CN_LINE
        # We use .decode_contents() to preserve <br/> as text, then split.
        inner = p_tag.decode_contents()
        # Split on <br/> or <br> or <br />
        parts = re.split(r"<br\s*/?\s*>", inner)
        if len(parts) < 2:
            continue

        # The Chinese text is in the last part after the <br/>
        cn_part = BeautifulSoup(parts[-1], "lxml").get_text().strip()
        if not cn_part:
            continue

        # Extract rule_ref from the Chinese line
        m = _CN_RULE_RE.match(cn_part)
        if m:
            entries.append({
                "rule_ref": m.group(1),
                "text": m.group(2).strip(),
            })

    return entries


def fetch_cn_rules(force: bool = False) -> dict[str, list[dict]]:
    """
    Scrape CN translation from wiki.mtgjudge.cn/cr.

    Returns dict[str, list[dict]] keyed by chapter number (str),
    where each entry is {"rule_ref": "100.1", "text": "Chinese text..."}.
    """
    out = RAW_DIR / "entries_cn_raw.json"
    if out.exists() and not force:
        return json.loads(out.read_text(encoding="utf-8"))

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    chapters: dict[str, list[dict]] = {}

    headers = {"User-Agent": _USER_AGENT}
    with httpx.Client(
        headers=headers,
        follow_redirects=True,
        timeout=60,
        http2=False,
    ) as client:
        for ch in CN_CHAPTER_PAGES:
            url = f"{CN_WIKI_BASE}:{ch}"
            # Simple retry loop for flaky SSL/connection issues
            last_err: Exception | None = None
            for attempt in range(3):
                try:
                    resp = client.get(url)
                    resp.raise_for_status()
                    last_err = None
                    break
                except (httpx.HTTPError, httpx.ConnectError) as e:
                    last_err = e
            if last_err is not None:
                raise last_err

            entries = parse_cn_page(resp.text)
            if entries:
                chapters[str(ch)] = entries

    out.write_text(json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8")
    return chapters


if __name__ == "__main__":
    out_dir = DATA_DIR / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching EN rules...")
    text = fetch_en_rules()
    en_chapters = parse_en_chapters(text)
    en_out = out_dir / "entries_en.json"
    en_out.write_text(json.dumps(en_chapters, ensure_ascii=False, indent=2), encoding="utf-8")
    en_total = sum(len(v) for v in en_chapters.values())
    print(f"Parsed {len(en_chapters)} EN chapters, {en_total} rule entries.")
    print(f"Saved to {en_out}")

    print("Fetching CN rules...")
    cn_chapters = fetch_cn_rules()
    cn_out = out_dir / "entries_cn.json"
    cn_out.write_text(json.dumps(cn_chapters, ensure_ascii=False, indent=2), encoding="utf-8")
    cn_total = sum(len(v) for v in cn_chapters.values())
    print(f"Parsed {len(cn_chapters)} CN chapters, {cn_total} rule entries.")
    print(f"Saved to {cn_out}")
