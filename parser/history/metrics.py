"""Compute multi-dimensional complexity metrics from a single concept_db."""

import json
import sqlite3
from pathlib import Path
from statistics import mean, median

from .fetch import DATA_DIR
from .baseline_extract import CONCEPT_DBS_DIR

METRICS_FILE = DATA_DIR / "metrics.json"


def compute_understanding_complexity(conn: sqlite3.Connection) -> dict[str, int]:
    """Replicate server/src/utils/understanding-complexity.ts in Python.

    uc(A) = complexity(A) + sum(uc(B) for B where A DEPENDS_ON B)
    """
    rows = conn.execute("SELECT id, complexity FROM concepts").fetchall()
    base = {r[0]: (r[1] or 1) for r in rows}

    deps_rows = conn.execute(
        "SELECT source_id, target_id FROM relations WHERE type = 'DEPENDS_ON'"
    ).fetchall()
    depends_on: dict[str, list[str]] = {}
    for src, tgt in deps_rows:
        depends_on.setdefault(src, []).append(tgt)

    memo: dict[str, int] = {}
    in_progress: set[str] = set()

    def compute(cid: str) -> int:
        if cid in memo:
            return memo[cid]
        if cid in in_progress:
            return 0
        in_progress.add(cid)
        total = base.get(cid, 1)
        for dep in depends_on.get(cid, []):
            total += compute(dep)
        in_progress.remove(cid)
        memo[cid] = total
        return total

    for cid in base:
        compute(cid)
    return memo


def compute_metrics(set_code: str, set_name: str, release_date: str | None,
                    prev_set_code: str | None = None) -> dict:
    """Compute the full MetricsRecord for a single version's DB."""
    set_code = set_code.upper()
    db_path = CONCEPT_DBS_DIR / f"{set_code}.db"
    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        rule_count = conn.execute("SELECT COUNT(*) FROM rule_texts").fetchone()[0]
        rule_text_rows = conn.execute("SELECT text_en FROM rule_texts WHERE text_en IS NOT NULL").fetchall()
        all_text = " ".join(r[0] for r in rule_text_rows)
        words = all_text.split()
        rule_total_words = len(words)
        rule_avg_length = round(rule_total_words / max(rule_count, 1), 1)

        chapter_count = conn.execute("SELECT COUNT(DISTINCT chapter) FROM concepts WHERE chapter IS NOT NULL").fetchone()[0]
        max_rule_depth = _compute_max_rule_depth(conn)

        concept_count = conn.execute("SELECT COUNT(*) FROM concepts").fetchone()[0]
        type_rows = conn.execute("SELECT type, COUNT(*) FROM concepts GROUP BY type").fetchall()
        concept_count_by_type = {t: c for t, c in type_rows}

        relation_count = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
        rel_type_rows = conn.execute("SELECT type, COUNT(*) FROM relations GROUP BY type").fetchall()
        relation_count_by_type = {t: c for t, c in rel_type_rows}

        isolated_concepts = conn.execute("""
            SELECT COUNT(*) FROM concepts c
            WHERE c.id NOT IN (SELECT source_id FROM relations)
              AND c.id NOT IN (SELECT target_id FROM relations)
        """).fetchone()[0]

        degree_rows = conn.execute("""
            SELECT id, (
                (SELECT COUNT(*) FROM relations WHERE source_id = c.id) +
                (SELECT COUNT(*) FROM relations WHERE target_id = c.id)
            ) as degree
            FROM concepts c
        """).fetchall()
        highly_connected_count = sum(1 for _, d in degree_rows if d > 10)

        uc_map = compute_understanding_complexity(conn)
        uc_values = list(uc_map.values())
        if uc_values:
            uc_total = sum(uc_values)
            uc_max = max(uc_values)
            uc_avg = round(uc_total / len(uc_values), 1)
            sorted_uc = sorted(uc_values)
            uc_p50 = sorted_uc[len(sorted_uc) // 2]
            uc_p90 = sorted_uc[int(len(sorted_uc) * 0.9)]
            uc_p99 = sorted_uc[min(int(len(sorted_uc) * 0.99), len(sorted_uc) - 1)]
        else:
            uc_total = uc_max = uc_avg = uc_p50 = uc_p90 = uc_p99 = 0

        top10 = sorted(uc_map.items(), key=lambda x: -x[1])[:10]
        top10_names = {
            row[0]: row[1] for row in conn.execute(
                f"SELECT id, name_en FROM concepts WHERE id IN ({','.join('?' * len(top10))})",
                [t[0] for t in top10],
            ).fetchall()
        } if top10 else {}
        uc_top10_concepts = [
            {"id": cid, "uc": uc, "name_en": top10_names.get(cid, cid)}
            for cid, uc in top10
        ]

        depends_on_chain_max = _compute_max_chain(conn)

        keyword_count = concept_count_by_type.get("Keyword", 0)
        card_type_count = concept_count_by_type.get("CardType", 0)
        evergreen_keyword_count = conn.execute(
            "SELECT COUNT(*) FROM concepts WHERE type = 'Keyword' AND complexity = 1"
        ).fetchone()[0]
        high_complexity_keywords = conn.execute(
            "SELECT COUNT(*) FROM concepts WHERE type = 'Keyword' AND complexity >= 4"
        ).fetchone()[0]

        keywords_added: list[str] = []
        keywords_removed: list[str] = []
        if prev_set_code:
            prev_db = CONCEPT_DBS_DIR / f"{prev_set_code.upper()}.db"
            if prev_db.exists():
                prev_conn = sqlite3.connect(prev_db)
                try:
                    prev_kw = {r[0] for r in prev_conn.execute(
                        "SELECT id FROM concepts WHERE type = 'Keyword'"
                    ).fetchall()}
                    curr_kw = {r[0] for r in conn.execute(
                        "SELECT id FROM concepts WHERE type = 'Keyword'"
                    ).fetchall()}
                    keywords_added = sorted(curr_kw - prev_kw)
                    keywords_removed = sorted(prev_kw - curr_kw)
                finally:
                    prev_conn.close()

        return {
            "set_code": set_code,
            "set_name": set_name,
            "release_date": release_date,
            "scale": {
                "rule_count": rule_count,
                "rule_total_words": rule_total_words,
                "rule_avg_length": rule_avg_length,
                "chapter_count": chapter_count,
                "max_rule_depth": max_rule_depth,
            },
            "graph": {
                "concept_count": concept_count,
                "concept_count_by_type": concept_count_by_type,
                "relation_count": relation_count,
                "relation_count_by_type": relation_count_by_type,
                "isolated_concepts": isolated_concepts,
                "highly_connected_count": highly_connected_count,
            },
            "cognitive": {
                "uc_total": uc_total,
                "uc_max": uc_max,
                "uc_avg": uc_avg,
                "uc_p50": uc_p50,
                "uc_p90": uc_p90,
                "uc_p99": uc_p99,
                "uc_top10_concepts": uc_top10_concepts,
                "depends_on_chain_max": depends_on_chain_max,
            },
            "mechanic": {
                "keyword_count": keyword_count,
                "keywords_added_since_prev": keywords_added,
                "keywords_removed_since_prev": keywords_removed,
                "card_type_count": card_type_count,
                "evergreen_keyword_count": evergreen_keyword_count,
                "high_complexity_keywords": high_complexity_keywords,
            },
        }
    finally:
        conn.close()


def _compute_max_rule_depth(conn: sqlite3.Connection) -> int:
    """Max sub-rule depth — count digits + letter chars in rule_ref."""
    rows = conn.execute("SELECT rule_ref FROM rule_texts WHERE rule_ref IS NOT NULL").fetchall()
    max_depth = 0
    for (ref,) in rows:
        depth = len([c for c in ref if c.isdigit() or c.isalpha()])
        max_depth = max(max_depth, depth)
    return max_depth


def _compute_max_chain(conn: sqlite3.Connection) -> int:
    """Longest DEPENDS_ON chain length using DFS."""
    deps_rows = conn.execute(
        "SELECT source_id, target_id FROM relations WHERE type = 'DEPENDS_ON'"
    ).fetchall()
    graph: dict[str, list[str]] = {}
    for src, tgt in deps_rows:
        graph.setdefault(src, []).append(tgt)

    memo: dict[str, int] = {}
    in_progress: set[str] = set()

    def longest(cid: str) -> int:
        if cid in memo:
            return memo[cid]
        if cid in in_progress:
            return 0
        in_progress.add(cid)
        best = 0
        for dep in graph.get(cid, []):
            best = max(best, 1 + longest(dep))
        in_progress.remove(cid)
        memo[cid] = best
        return best

    if not graph:
        return 0
    return max(longest(cid) for cid in graph)


def compute_all_metrics(versions: list[dict]) -> list[dict]:
    """Compute metrics for all versions in order. Returns the time series."""
    timeline = []
    for i, version in enumerate(versions):
        prev_code = versions[i - 1]["set_code"] if i > 0 else None
        try:
            record = compute_metrics(
                version["set_code"],
                version["set_name"],
                version.get("release_date"),
                prev_set_code=prev_code,
            )
            timeline.append(record)
        except FileNotFoundError as e:
            print(f"  Skipping {version['set_code']}: {e}")
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    return timeline
