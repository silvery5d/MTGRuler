"""Run the full history pipeline: walk versions, baseline extract, incremental
extract chain, compute metrics, detect spikes."""

import argparse
import sys
from pathlib import Path

from .walk_versions import walk_all_versions, load_versions_index
from .fetch import fetch_cr_text
from .parse_version import parse_version
from .baseline_extract import baseline_extract, CONCEPT_DBS_DIR
from .incremental_extract import incremental_extract
from .metrics import compute_all_metrics, METRICS_FILE
from .detect_spikes import detect_and_analyze, SPIKES_FILE


def run(
    baseline_set: str | None = None,
    max_versions: int | None = None,
    skip_extract: bool = False,
    skip_metrics: bool = False,
    skip_spikes: bool = False,
    force: bool = False,
):
    print("=" * 60)
    print("MTG History Pipeline")
    print("=" * 60)

    print("\n[1/6] Walking version chain...")
    if force:
        versions = walk_all_versions()
    else:
        versions = load_versions_index()
    print(f"  Found {len(versions)} versions: {versions[0]['set_code']} ... {versions[-1]['set_code']}")

    if max_versions:
        versions = versions[:max_versions]
        print(f"  Limited to first {max_versions} versions")

    print("\n[2/6] Pre-fetching CR text + diffs...")
    for i, v in enumerate(versions):
        print(f"  [{i+1}/{len(versions)}] {v['set_code']}", end="\r")
        try:
            fetch_cr_text(v["set_code"])
            parse_version(v["set_code"])
        except Exception as e:
            print(f"\n  WARN: failed to fetch {v['set_code']}: {e}")
    print()

    if not skip_extract:
        baseline_code = baseline_set or versions[0]["set_code"]
        print(f"\n[3/6] Baseline extraction: {baseline_code}")
        baseline_extract(baseline_code, force=force)

        print(f"\n[4/6] Incremental extraction across {len(versions) - 1} versions...")
        baseline_idx = next((i for i, v in enumerate(versions) if v["set_code"] == baseline_code), 0)
        for i in range(baseline_idx + 1, len(versions)):
            prev = versions[i - 1]["set_code"]
            curr = versions[i]["set_code"]
            print(f"  [{i}/{len(versions) - 1}] {prev} → {curr}")
            try:
                incremental_extract(prev, curr, force=force)
            except Exception as e:
                print(f"    ERROR: {e}")
                print(f"    Skipping {curr} and continuing")

    if not skip_metrics:
        print(f"\n[5/6] Computing metrics for all versions...")
        timeline = compute_all_metrics(versions)
        print(f"  Wrote {len(timeline)} metric records to {METRICS_FILE}")
    else:
        import json
        timeline = json.loads(METRICS_FILE.read_text(encoding="utf-8")) if METRICS_FILE.exists() else []

    if not skip_spikes:
        print(f"\n[6/6] Detecting spikes + LLM analysis...")
        spikes = detect_and_analyze(timeline, force=force)
        print(f"  Found {len(spikes)} spikes; analysis saved to {SPIKES_FILE}")

    print("\n" + "=" * 60)
    print("History pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="MTG History Pipeline")
    ap.add_argument("--baseline-set", type=str, help="Set code to use as baseline (default: earliest)")
    ap.add_argument("--max-versions", type=int, help="Limit to first N versions for testing")
    ap.add_argument("--skip-extract", action="store_true")
    ap.add_argument("--skip-metrics", action="store_true")
    ap.add_argument("--skip-spikes", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    run(
        baseline_set=args.baseline_set,
        max_versions=args.max_versions,
        skip_extract=args.skip_extract,
        skip_metrics=args.skip_metrics,
        skip_spikes=args.skip_spikes,
        force=args.force,
    )
