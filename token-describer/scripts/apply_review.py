#!/usr/bin/env python3
"""
Apply decisions from a filled-in REVIEW-PENDING.md to the token source files.

Reads the markdown table(s) produced by generate-review-report.py and, for
each row the user has filled in, either:
  - Keeps the provisional description (Accept? == "y" with no New Description)
  - Replaces the description with the value in New Description
  - Marks the token as Figma-verified in $extensions (for accepted rows)

Rows left entirely blank are skipped and remain pending for the next cycle.

After applying decisions the review file is moved to:
    token-describer/runs/review-YYYY-MM-DD.md

Usage:
    python3 token-describer/scripts/apply-review.py [--review path/to/REVIEW-PENDING.md]

Options:
    --review PATH   Override the default REVIEW-PENDING.md location.
                    Default: token-describer/REVIEW-PENDING.md
"""

import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))
from run_tracker import record_correction


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
TOKEN_DESCRIBER_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = TOKEN_DESCRIBER_DIR.parent
RUNS_DIR = TOKEN_DESCRIBER_DIR / "runs"
DEFAULT_REVIEW_FILE = TOKEN_DESCRIBER_DIR / "REVIEW-PENDING.md"
TOKENS_DIR = PROJECT_ROOT / "tokens"

METADATA_KEYS = {"$type", "$value", "$description", "$extensions"}


# ─── MARKDOWN PARSING ─────────────────────────────────────────────────────────

def parse_table_row(line: str) -> list:
    """
    Split a markdown table row into a list of cell strings.

    Handles leading/trailing pipes and strips whitespace from each cell.
    Returns an empty list if the line is not a table row.
    """
    line = line.strip()
    if not line.startswith("|"):
        return []
    # Remove leading and trailing pipe then split.
    cells = line.strip("|").split("|")
    return [cell.strip() for cell in cells]


def is_separator_row(cells: list) -> bool:
    """Return True if every cell is a markdown table separator (--- etc.)."""
    return all(re.fullmatch(r":?-+:?", c) for c in cells if c)


def parse_review_file(review_path: Path) -> list:
    """
    Parse REVIEW-PENDING.md and return a list of decision dicts.

    Only rows where the user has provided a value in Accept? or New Description
    are returned. Blank rows are silently skipped.

    Each dict has keys:
        token_path      str   Dot-separated token path
        old_description str   The provisional description shown to the user
        accept          bool  True if Accept? column contains "y" / "yes"
        new_description str   Value from New Description column (may be "")
        notes           str   Value from Notes column (may be "")
    """
    decisions = []

    with open(review_path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    # We expect columns in this order (positions 0-5):
    # | Token Path | Provisional Description | Reason | Accept? | New Description | Notes |
    # The Reason column (index 2) is read-only — we don't use it here.
    EXPECTED_MIN_COLS = 6
    COL_PATH = 0
    COL_PROVISIONAL = 1
    COL_ACCEPT = 3
    COL_NEW_DESC = 4
    COL_NOTES = 5

    in_table = False

    for line in lines:
        cells = parse_table_row(line)

        if not cells:
            in_table = False
            continue

        if is_separator_row(cells):
            in_table = True
            continue

        # Header row detection: first cell is "Token Path".
        if cells and cells[0].strip().lower() == "token path":
            in_table = True
            continue

        if not in_table:
            continue

        if len(cells) < EXPECTED_MIN_COLS:
            # Malformed row — skip silently.
            continue

        token_path = cells[COL_PATH]
        old_description = cells[COL_PROVISIONAL].replace("_(none)_", "").strip()
        accept_raw = cells[COL_ACCEPT].strip().lower()
        new_description = cells[COL_NEW_DESC].strip()
        notes = cells[COL_NOTES].strip() if len(cells) > COL_NOTES else ""

        # Skip rows the user left completely blank.
        if not accept_raw and not new_description:
            continue

        # Skip the header row if it slipped through.
        if token_path.lower() == "token path":
            continue

        accept = accept_raw in ("y", "yes", "true", "1")

        decisions.append({
            "token_path": token_path,
            "old_description": old_description,
            "accept": accept,
            "new_description": new_description,
            "notes": notes,
        })

    return decisions


# ─── TOKEN FILE DISCOVERY ─────────────────────────────────────────────────────

def find_all_token_files(tokens_dir: Path) -> list:
    """Return absolute paths of all non-metadata JSON files under tokens_dir."""
    found = []
    for dirpath, _dirs, files in os.walk(tokens_dir):
        for fname in sorted(files):
            if fname.endswith(".json") and not fname.startswith("$"):
                found.append(Path(dirpath) / fname)
    return found


# ─── TOKEN TREE MUTATION ──────────────────────────────────────────────────────

def is_token(obj: dict) -> bool:
    """Return True if the dict is a leaf token node."""
    return isinstance(obj, dict) and "$type" in obj and "$value" in obj


def find_and_update_token(data: dict, target_parts: list, new_description: str, mark_verified: bool) -> bool:
    """
    Recursively locate a token by its dot-separated path parts and update it.

    Sets $description to new_description. If mark_verified is True, also sets
    $extensions.figmaVerified = true to prevent the token from appearing in
    future review reports.

    Returns True if the token was found and updated, False otherwise.
    """
    if not target_parts:
        return False

    key = target_parts[0]
    remaining = target_parts[1:]

    if key not in data:
        return False

    node = data[key]

    if not isinstance(node, dict):
        return False

    # If this is the leaf token node (no more path segments to traverse).
    if not remaining:
        if is_token(node):
            node["$description"] = new_description
            if mark_verified:
                extensions = node.setdefault("$extensions", {})
                if not isinstance(extensions, dict):
                    extensions = {}
                    node["$extensions"] = extensions
                extensions["figmaVerified"] = True
            return True
        return False

    # Otherwise recurse, skipping metadata keys.
    if key in METADATA_KEYS:
        return False

    return find_and_update_token(node, remaining, new_description, mark_verified)


def apply_decision_to_files(decision: dict, token_files: list) -> bool:
    """
    Search all token files for the token referenced in decision and apply the
    description update to the first file where it is found.

    Returns True if the token was found and the file was updated.
    """
    token_path = decision["token_path"]
    path_parts = token_path.split(".")

    # Determine the final description to write.
    if decision["new_description"]:
        description = decision["new_description"]
        mark_verified = False  # User-provided; not from Figma
    elif decision["accept"]:
        description = decision["old_description"]
        mark_verified = True   # User accepted the provisional — treat as verified
    else:
        # Neither accepted nor replaced — nothing to do.
        return False

    for file_path in token_files:
        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError):
            continue

        if find_and_update_token(data, path_parts, description, mark_verified):
            with open(file_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
            return True

    return False


# ─── ARCHIVE HELPERS ──────────────────────────────────────────────────────────

def archive_review_file(review_path: Path) -> Path:
    """
    Move the processed review file into runs/ with a datestamped name.

    If a file with the same name already exists (e.g. two reviews on the same
    day), a numeric suffix is appended: review-2026-03-31-2.md, etc.
    """
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    base_name = f"review-{today}.md"
    destination = RUNS_DIR / base_name

    counter = 2
    while destination.exists():
        destination = RUNS_DIR / f"review-{today}-{counter}.md"
        counter += 1

    shutil.move(str(review_path), str(destination))
    return destination


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point: parse review file, apply decisions, archive the review."""

    # Resolve the review file path — support --review override.
    review_path = DEFAULT_REVIEW_FILE
    if "--review" in sys.argv:
        idx = sys.argv.index("--review")
        if idx + 1 < len(sys.argv):
            review_path = Path(sys.argv[idx + 1])
        else:
            print("Error: --review flag requires a path argument.", file=sys.stderr)
            sys.exit(1)

    if not review_path.exists():
        print(f"Error: review file not found: {review_path}", file=sys.stderr)
        print("Run generate-review-report.py first to create REVIEW-PENDING.md.", file=sys.stderr)
        sys.exit(1)

    print(f"Reading review file: {review_path}")
    decisions = parse_review_file(review_path)

    if not decisions:
        print("No decisions found in the review file.")
        print("Fill in the Accept? or New Description columns, then re-run.")
        return

    print(f"Found {len(decisions)} decision(s) to process.\n")

    # Load all token files once so we can search across them efficiently.
    token_files = find_all_token_files(TOKENS_DIR)
    if not token_files:
        print(f"Warning: no token files found under {TOKENS_DIR}", file=sys.stderr)

    accepted = 0
    corrected = 0
    not_found = 0

    for decision in decisions:
        token_path = decision["token_path"]
        updated = apply_decision_to_files(decision, token_files)

        if not updated:
            print(f"  NOT FOUND: {token_path}")
            not_found += 1
            continue

        # Determine which action was taken and record it.
        if decision["new_description"]:
            action_label = "corrected"
            corrected += 1
            old_desc = decision["old_description"]
            new_desc = decision["new_description"]
        else:
            action_label = "accepted"
            accepted += 1
            old_desc = decision["old_description"]
            new_desc = decision["old_description"]

        print(f"  {action_label.upper()}: {token_path}")
        if decision["new_description"]:
            print(f"    Was:  {old_desc or '(none)'}")
            print(f"    Now:  {new_desc}")

        # Log the correction for traceability (even accepted entries are recorded
        # so the review history is complete).
        # Signature matches run-tracker.py: (token_path, old_desc, new_desc, reason)
        record_correction(
            token_path,
            old_desc,
            new_desc,
            decision["notes"] or action_label,
        )

    # Count how many rows were left blank (still pending).
    # We do this by re-reading the file rather than tracking state above, so
    # the pending count reflects the actual file contents.
    pending = _count_pending_rows(review_path)

    # Archive the review file regardless of whether all rows were filled.
    archived_path = archive_review_file(review_path)

    print(f"\n{'=' * 50}")
    print("APPLY REVIEW COMPLETE")
    print(f"{'=' * 50}")
    print(f"  Accepted (kept provisional):  {accepted}")
    print(f"  Corrected (new description):  {corrected}")
    print(f"  Token not found in files:     {not_found}")
    print(f"  Still pending (blank rows):   {pending}")
    print(f"\n  Review file archived to: {archived_path}")

    if pending > 0:
        print(f"\n  {pending} token(s) still need review.")
        print("  Run generate-review-report.py again to create a fresh REVIEW-PENDING.md.")


def _count_pending_rows(review_path: Path) -> int:
    """
    Count rows in the review file where the user left both Accept? and
    New Description blank — these tokens remain unreviewed.
    """
    if not review_path.exists():
        return 0

    count = 0
    in_table = False

    with open(review_path, "r", encoding="utf-8") as fh:
        for line in fh:
            cells = parse_table_row(line)
            if not cells:
                in_table = False
                continue
            if is_separator_row(cells):
                in_table = True
                continue
            if cells and cells[0].strip().lower() == "token path":
                in_table = True
                continue
            if not in_table:
                continue
            if len(cells) < 6:
                continue
            accept_raw = cells[3].strip()
            new_desc = cells[4].strip()
            token_path = cells[0].strip()
            # Skip header echoes
            if token_path.lower() == "token path":
                continue
            if not accept_raw and not new_desc:
                count += 1

    return count


if __name__ == "__main__":
    main()
