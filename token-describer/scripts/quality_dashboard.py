#!/usr/bin/env python3
"""
Quality dashboard for the token-describer tool.

Reads all run manifests from token-describer/runs/ and prints a summary
of coverage trends, correction history, and validation error trends.
"""

import sys
from collections import Counter
from pathlib import Path

# Allow importing run-tracker from the same scripts/ directory.
sys.path.insert(0, str(Path(__file__).parent))
from run_tracker import load_all_manifests, load_overrides


def _bar(value, max_value, width=20):
    """Render a simple ASCII progress bar."""
    if max_value == 0:
        filled = 0
    else:
        filled = round((value / max_value) * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _pct_arrow(before, after):
    """Return a directional indicator for a coverage change."""
    diff = after - before
    if diff > 0:
        return f"+{diff:.1f}%"
    if diff < 0:
        return f"{diff:.1f}%"
    return "no change"


def print_dashboard():
    """Load all run manifests and print the quality dashboard."""
    manifests = load_all_manifests()
    overrides = load_overrides()

    sep = "=" * 60
    thin = "-" * 60

    print(sep)
    print("  TOKEN-DESCRIBER QUALITY DASHBOARD")
    print(sep)

    if not manifests:
        print("\n  No run manifests found in token-describer/runs/")
        print("  Run generate-descriptions.py to create the first manifest.")
        print(sep)
        return

    total_runs = len(manifests)
    print(f"\n  Total runs recorded : {total_runs}")

    # ── Coverage trend ────────────────────────────────────────────────
    first = manifests[0]
    latest = manifests[-1]

    first_coverage = first.get("coverage_after_pct", 0.0)
    latest_coverage = latest.get("coverage_after_pct", 0.0)
    change = _pct_arrow(first_coverage, latest_coverage)

    print(f"\n  Coverage trend")
    print(thin)
    print(f"  First run  ({first.get('date', 'unknown')[:10]})  :  {first_coverage:.1f}%")
    print(f"  Latest run ({latest.get('date', 'unknown')[:10]})  :  {latest_coverage:.1f}%  ({change})")
    print(f"  {_bar(latest_coverage, 100.0)}")

    # ── Per-run coverage table ────────────────────────────────────────
    if total_runs > 1:
        print(f"\n  Run-by-run coverage")
        print(thin)
        for m in manifests:
            date_str = m.get("date", "?")[:10]
            pct_after = m.get("coverage_after_pct", 0.0)
            pct_before = m.get("coverage_before_pct", 0.0)
            arrow = _pct_arrow(pct_before, pct_after)
            print(f"  {date_str}  {pct_after:6.1f}%  {arrow}")

    # ── Descriptions added per run ────────────────────────────────────
    total_added = sum(m.get("descriptions_added", 0) for m in manifests)
    avg_added = total_added / total_runs if total_runs else 0

    print(f"\n  Descriptions added")
    print(thin)
    print(f"  Total across all runs  :  {total_added}")
    print(f"  Average per run        :  {avg_added:.1f}")

    # ── Corrections / overrides ───────────────────────────────────────
    # Collect all corrections from every run manifest.
    all_corrections = []
    for m in manifests:
        all_corrections.extend(m.get("user_corrections", []))

    total_corrections = len(all_corrections)
    print(f"\n  User corrections")
    print(thin)
    print(f"  Total corrections recorded  :  {total_corrections}")
    print(f"  Active overrides in file    :  {len(overrides)}")

    if all_corrections:
        # Tally corrections by token category (first two path segments).
        category_counter = Counter()
        for c in all_corrections:
            path = c.get("token_path", "")
            parts = path.split(".")
            category = ".".join(parts[:2]) if len(parts) >= 2 else parts[0] if parts else "unknown"
            category_counter[category] += 1

        print(f"\n  Most-corrected token categories")
        print(thin)
        for category, count in category_counter.most_common(10):
            bar = _bar(count, category_counter.most_common(1)[0][1], width=15)
            print(f"  {category:<40}  {count:>3}  {bar}")

    # ── Validation error trend ────────────────────────────────────────
    has_validation_data = any(
        "validation_errors" in m or "validation_warnings" in m
        for m in manifests
    )

    if has_validation_data:
        print(f"\n  Validation trend")
        print(thin)
        print(f"  {'Date':<12}  {'Errors':>7}  {'Warnings':>9}")
        for m in manifests:
            date_str = m.get("date", "?")[:10]
            errors = m.get("validation_errors", 0)
            warnings = m.get("validation_warnings", 0)
            # Flag runs with errors so they stand out.
            flag = "  <-- errors present" if errors > 0 else ""
            print(f"  {date_str:<12}  {errors:>7}  {warnings:>9}{flag}")

        total_errors = sum(m.get("validation_errors", 0) for m in manifests)
        latest_errors = latest.get("validation_errors", 0)
        print(f"\n  Latest run errors   :  {latest_errors}")
        print(f"  Total errors (all)  :  {total_errors}")

    print(f"\n{sep}\n")


if __name__ == "__main__":
    print_dashboard()
