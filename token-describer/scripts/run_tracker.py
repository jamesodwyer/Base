#!/usr/bin/env python3
"""
Run tracking and feedback system for the token-describer tool.

Manages run history manifests in token-describer/runs/ and a persistent
overrides.json file that stores user-corrected descriptions.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


# Resolve paths relative to this script's location (scripts/ -> token-describer/)
TOOL_DIR = Path(__file__).parent.parent
RUNS_DIR = TOOL_DIR / "runs"
OVERRIDES_FILE = TOOL_DIR / "overrides.json"


def _ensure_runs_dir():
    """Create the runs/ directory if it does not exist."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)


def _current_run_path():
    """
    Return the path of the run manifest that was started in this process.

    Stores the path in a module-level variable so a single process always
    writes to the same manifest file.
    """
    if not hasattr(_current_run_path, "_path"):
        _current_run_path._path = None
    return _current_run_path._path


def _set_current_run_path(path):
    """Set the module-level current run path."""
    _current_run_path._path = path


def save_run_manifest(
    files_processed,
    tokens_total,
    descriptions_added,
    descriptions_updated,
    descriptions_unchanged,
    coverage_before_pct,
    coverage_after_pct,
    validation_errors,
    validation_warnings,
    user_corrections=None,
):
    """
    Write a run manifest to runs/run-YYYY-MM-DD-HHMMSS.json.

    Returns the Path of the created manifest file.
    """
    _ensure_runs_dir()

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d-%H%M%S")
    filename = f"run-{timestamp}.json"
    manifest_path = RUNS_DIR / filename

    manifest = {
        "date": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files_processed": files_processed,
        "tokens_total": tokens_total,
        "descriptions_added": descriptions_added,
        "descriptions_updated": descriptions_updated,
        "descriptions_unchanged": descriptions_unchanged,
        "coverage_before_pct": round(coverage_before_pct, 1),
        "coverage_after_pct": round(coverage_after_pct, 1),
        "validation_errors": validation_errors,
        "validation_warnings": validation_warnings,
        "user_corrections": user_corrections if user_corrections is not None else [],
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    _set_current_run_path(manifest_path)
    print(f"Run manifest saved: {manifest_path.name}")
    return manifest_path


def record_correction(token_path, old_desc, new_desc, reason):
    """
    Record a user correction for a token description.

    Appends to the current run manifest (if one exists in this process) and
    writes the correction to the persistent overrides.json file.

    Args:
        token_path: Dot-separated token path, e.g. "color.interactive.primary.fill.default"
        old_desc:   The description that was generated or previously set.
        new_desc:   The corrected description the user wants to use.
        reason:     Short explanation of why the correction was made.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Append to the current run manifest if one was created this session.
    current_manifest = _current_run_path()
    if current_manifest and Path(current_manifest).exists():
        with open(current_manifest, "r") as f:
            manifest = json.load(f)

        manifest["user_corrections"].append({
            "token_path": token_path,
            "old_desc": old_desc,
            "new_desc": new_desc,
            "reason": reason,
        })

        with open(current_manifest, "w") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")

    # Write to persistent overrides.json.
    overrides = load_overrides()
    overrides[token_path] = {
        "description": new_desc,
        "reason": reason,
        "date": today,
    }

    with open(OVERRIDES_FILE, "w") as f:
        json.dump(overrides, f, indent=2)
        f.write("\n")

    print(f"Correction recorded for: {token_path}")


def load_overrides():
    """
    Load user-corrected descriptions from overrides.json.

    Returns a dict mapping token_path -> {"description": ..., "reason": ..., "date": ...}.
    Returns an empty dict if the file does not exist or is empty.
    """
    if not OVERRIDES_FILE.exists():
        return {}

    with open(OVERRIDES_FILE, "r") as f:
        content = f.read().strip()

    if not content:
        return {}

    return json.loads(content)


def load_all_manifests():
    """
    Load every run manifest from the runs/ directory.

    Returns a list of manifest dicts sorted by date ascending.
    """
    _ensure_runs_dir()
    manifests = []

    for manifest_file in sorted(RUNS_DIR.glob("run-*.json")):
        with open(manifest_file, "r") as f:
            try:
                data = json.load(f)
                data["_filename"] = manifest_file.name
                manifests.append(data)
            except json.JSONDecodeError:
                # Skip malformed manifests rather than crashing.
                print(f"Warning: could not parse {manifest_file.name}, skipping.")

    return manifests
