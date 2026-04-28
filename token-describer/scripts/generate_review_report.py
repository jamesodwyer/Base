#!/usr/bin/env python3
"""
Generate a batch review report for token descriptions needing human verification.

Scans one or more token JSON files for tokens that either:
  (a) have no $description field, or
  (b) have a provisional description that has not been Figma-verified
      (detected by the absence of a $extensions.figmaVerified flag).

Tokens are grouped by semantic category and written to REVIEW-PENDING.md
in the token-describer directory. The user fills in decisions in the
markdown table, then runs apply-review.py to apply them.

Usage:
    # Scan all token files (default — reads tokens/ relative to project root)
    python3 token-describer/scripts/generate-review-report.py

    # Scan a specific file
    python3 token-describer/scripts/generate-review-report.py tokens/semantic/colorLight.json

    # Scan a directory
    python3 token-describer/scripts/generate-review-report.py tokens/semantic/
"""

import json
import os
import sys
from datetime import date
from pathlib import Path


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

# Output file is written to the token-describer root so it is easy to find.
SCRIPT_DIR = Path(__file__).parent
TOKEN_DESCRIBER_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = TOKEN_DESCRIBER_DIR.parent
OUTPUT_FILE = TOKEN_DESCRIBER_DIR / "REVIEW-PENDING.md"

# Token JSON keys that are metadata, not child nodes.
METADATA_KEYS = {"$type", "$value", "$description", "$extensions"}

# Maps first path segments (or sub-segments) to readable category labels.
# Order matters: first match wins. Tuples of (check_function, label).
CATEGORY_RULES = [
    # Interactive: color.interactive.*
    (lambda parts: len(parts) >= 2 and parts[0] == "color" and parts[1] == "interactive", "interactive"),
    # Text: color.text.*
    (lambda parts: len(parts) >= 2 and parts[0] == "color" and parts[1] == "text", "text"),
    # Icon: color.icon.*
    (lambda parts: len(parts) >= 2 and parts[0] == "color" and parts[1] == "icon", "icon"),
    # Input: color.input.*
    (lambda parts: len(parts) >= 2 and parts[0] == "color" and parts[1] == "input", "input"),
    # Feedback: color.feedback.*
    (lambda parts: len(parts) >= 2 and parts[0] == "color" and parts[1] == "feedback", "feedback"),
    # Surface: color.surface.*
    (lambda parts: len(parts) >= 2 and parts[0] == "color" and parts[1] == "surface", "surface"),
    # Elevation: color.elevation.* or top-level elevation.*
    (lambda parts: (len(parts) >= 2 and parts[0] == "color" and parts[1] == "elevation")
                   or parts[0] == "elevation", "elevation"),
    # Selected/active/disabled/focus (all semantic color sub-groups)
    (lambda parts: len(parts) >= 2 and parts[0] == "color"
                   and parts[1] in ("selected", "active", "disabled", "focus", "status"), "semantic-color"),
    # Border (semantic)
    (lambda parts: parts[0] == "borderRadius" or (parts[0] == "border" and len(parts) >= 2), "border"),
    # Typography (semantic)
    (lambda parts: parts[0] == "typography", "typography"),
    # Component: button / icon / layout
    (lambda parts: parts[0] in ("button", "icon", "layout"), "component"),
    # Core primitives
    (lambda parts: parts[0] == "core", "core"),
    # Brand / raw colors
    (lambda parts: parts[0] == "color" and len(parts) >= 2
                   and parts[1] in ("brand", "accent", "neutrals", "common", "ism"), "brand"),
]

# Categories that need human review (core/brand descriptions are pattern-generated
# and generally don't need Figma verification).
REVIEW_CATEGORIES = {
    "interactive", "text", "icon", "input", "feedback",
    "surface", "elevation", "semantic-color", "border",
    "typography", "component",
}


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def is_token(obj: dict) -> bool:
    """Return True if the dict is a leaf token (has $type and $value)."""
    return isinstance(obj, dict) and "$type" in obj and "$value" in obj


def is_figma_verified(obj: dict) -> bool:
    """
    Return True if the token carries a figmaVerified flag in its extensions.

    Token Studio stores custom metadata in $extensions. We look for:
        $extensions.figmaVerified = true
    """
    extensions = obj.get("$extensions", {})
    if not isinstance(extensions, dict):
        return False
    return extensions.get("figmaVerified", False) is True


def categorise(path_parts: list) -> str:
    """Return the category label for a token path."""
    for check, label in CATEGORY_RULES:
        if check(path_parts):
            return label
    return "other"


def collect_tokens(data: dict, path_parts: list, results: list) -> None:
    """
    Recursively walk the token tree and collect tokens needing review.

    A token is collected if:
      - It has no $description, OR
      - It has a $description but is NOT Figma-verified (provisional)

    Appends dicts with keys: path, description, category, reason.
    """
    if not isinstance(data, dict):
        return

    if is_token(data):
        description = data.get("$description", "").strip()
        category = categorise(path_parts)

        # Only raise tokens in review-worthy categories for human attention.
        if category not in REVIEW_CATEGORIES:
            return

        if not description:
            results.append({
                "path": ".".join(path_parts),
                "description": "",
                "category": category,
                "reason": "no description",
            })
        elif not is_figma_verified(data):
            results.append({
                "path": ".".join(path_parts),
                "description": description,
                "category": category,
                "reason": "provisional — not Figma-verified",
            })
        return

    for key, value in data.items():
        if key in METADATA_KEYS:
            continue
        if isinstance(value, dict):
            collect_tokens(value, path_parts + [key], results)


def find_token_files(target: str) -> list:
    """
    Return a sorted list of absolute paths to token JSON files.

    target can be:
      - A path to a single .json file
      - A path to a directory (walks recursively for *.json, skips $ files)
      - Empty string / None — defaults to <project_root>/tokens/
    """
    if not target:
        root = PROJECT_ROOT / "tokens"
    else:
        root = Path(target)

    if root.is_file():
        return [str(root)]

    if root.is_dir():
        found = []
        for dirpath, _dirs, files in os.walk(root):
            for fname in sorted(files):
                if fname.endswith(".json") and not fname.startswith("$"):
                    found.append(os.path.join(dirpath, fname))
        return found

    print(f"Error: path not found: {target}", file=sys.stderr)
    sys.exit(1)


def build_markdown(tokens_by_category: dict, total: int, scan_target: str) -> str:
    """Render the review markdown from the grouped token data."""
    today = date.today().isoformat()

    lines = [
        "# Token Description Review",
        "",
        f"Generated: {today}",
        f"Tokens needing review: {total}",
        f"Scanned: {scan_target}",
        "",
        "## How to fill in this file",
        "",
        "For each token row:",
        "- **Accept?** — write `y` to keep the provisional description as-is.",
        "- **New Description** — write a replacement if the provisional is wrong or missing.",
        "- **Notes** — optional. Record why you made the change (useful for the corrections log).",
        "",
        "Leave a row entirely blank to skip it — it will remain pending for the next review.",
        "",
        "Run `apply-review.py` when done to apply decisions to the token files.",
        "",
        "---",
        "",
    ]

    # Friendly display names for categories, in preferred display order.
    category_order = [
        ("interactive", "Interactive Tokens"),
        ("text",        "Text Tokens"),
        ("icon",        "Icon Tokens"),
        ("input",       "Input Tokens"),
        ("feedback",    "Feedback Tokens"),
        ("surface",     "Surface Tokens"),
        ("elevation",   "Elevation Tokens"),
        ("semantic-color", "Other Semantic Color Tokens"),
        ("border",      "Border and Border Radius Tokens"),
        ("typography",  "Typography Tokens"),
        ("component",   "Component Tokens"),
        ("other",       "Uncategorised Tokens"),
    ]

    for category_key, category_label in category_order:
        tokens = tokens_by_category.get(category_key, [])
        if not tokens:
            continue

        lines.append(f"## {category_label} ({len(tokens)})")
        lines.append("")
        lines.append("| Token Path | Provisional Description | Reason | Accept? | New Description | Notes |")
        lines.append("|---|---|---|---|---|---|")

        for token in tokens:
            # Escape any pipe characters in values to avoid breaking the table.
            path = token["path"].replace("|", "\\|")
            desc = token["description"].replace("|", "\\|") if token["description"] else "_(none)_"
            reason = token["reason"].replace("|", "\\|")
            lines.append(f"| {path} | {desc} | {reason} |  |  |  |")

        lines.append("")

    return "\n".join(lines)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point: scan token files and write REVIEW-PENDING.md."""
    scan_target = sys.argv[1] if len(sys.argv) > 1 else ""

    token_files = find_token_files(scan_target)
    print(f"Scanning {len(token_files)} token file(s)...")

    all_tokens = []

    for file_path in token_files:
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"  Warning: skipping {file_path} — invalid JSON: {exc}", file=sys.stderr)
            continue
        except OSError as exc:
            print(f"  Warning: skipping {file_path} — {exc}", file=sys.stderr)
            continue

        file_tokens: list = []
        collect_tokens(data, [], file_tokens)

        if file_tokens:
            print(f"  {file_path}: {len(file_tokens)} token(s) needing review")
        else:
            print(f"  {file_path}: all descriptions verified")

        all_tokens.extend(file_tokens)

    if not all_tokens:
        print("\nNothing to review — all tokens are verified or covered by core/brand patterns.")
        return

    # Group tokens by category.
    by_category: dict = {}
    for token in all_tokens:
        by_category.setdefault(token["category"], []).append(token)

    # Determine a human-readable label for the scanned path.
    if scan_target:
        scan_label = scan_target
    else:
        scan_label = str(PROJECT_ROOT / "tokens") + " (all files)"

    markdown = build_markdown(by_category, len(all_tokens), scan_label)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(markdown)

    print(f"\nReview file written to: {OUTPUT_FILE}")
    print(f"Total tokens needing review: {len(all_tokens)}")
    print("\nNext steps:")
    print("  1. Open REVIEW-PENDING.md and fill in Accept? / New Description columns.")
    print("  2. Run: python3 token-describer/scripts/apply-review.py")


if __name__ == "__main__":
    main()
