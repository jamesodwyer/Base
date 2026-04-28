#!/usr/bin/env python3
"""
Validate token descriptions for quality and consistency.

Usage:
    Single file:  python validate-descriptions.py path/to/tokens.json
                  [--figma-mapping path/to/FIGMA-TOKEN-USAGE-MAPPING.md]
    Directory:    python validate-descriptions.py --dir path/to/tokens/
                  [--figma-mapping path/to/FIGMA-TOKEN-USAGE-MAPPING.md]

Checks:
- Description length (20-50 characters target)
- No unit references (px, pt, rem, dp)
- No platform references (iOS, Android — not "mobile"/"desktop" which are
  valid design-token viewport contexts)
- Component mentions for semantic/component tokens
- Figma context documentation for semantic/component tokens
"""

import json
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# Validation rules
TARGET_MIN_LENGTH = 20
TARGET_MAX_LENGTH = 50
UNIT_PATTERNS = [r'\bpx\b', r'\bpt\b', r'\brem\b', r'\bdp\b', r'\bem\b', r'\bvh\b', r'\bvw\b']
# "mobile" and "desktop" are valid design-token contexts (e.g. mobile layout
# spacing) and are intentionally excluded here. The intent is to prevent
# implementation-specific references like "use 16px on iOS" — not to ban
# descriptions that legitimately distinguish viewport contexts.
PLATFORM_PATTERNS = [r'\biOS\b', r'\bAndroid\b', r'\bWeb\b']

# Keys to skip when traversing the token tree (both old and DTCG formats)
SKIP_KEYS = {
    "description", "$description",
    "value", "$value",
    "type", "$type",
    "$extensions",
}


class TokenValidator:
    def __init__(self, tokens_path: str, figma_mapping_path: Optional[str] = None):
        self.tokens_path = tokens_path
        self.figma_mapping_path = figma_mapping_path
        self.issues = []
        self.stats = {
            "total_tokens": 0,
            "tokens_with_descriptions": 0,
            "tokens_without_descriptions": 0,
            "core_tokens": 0,
            "brand_tokens": 0,
            "semantic_tokens": 0,
            "component_tokens": 0,
            "unknown_tokens": 0,
            "length_ok": 0,
            "length_warnings": 0,
            "unit_references": 0,
            "platform_references": 0,
            "missing_components": 0,
            "missing_figma_context": 0
        }
        self.figma_documented_tokens = set()
        # Track descriptions seen in this file for duplicate detection.
        # Maps description text -> list of token paths that use it.
        self._seen_descriptions: Dict[str, List[str]] = {}

        # Load Figma mapping if provided
        if figma_mapping_path and os.path.exists(figma_mapping_path):
            self._load_figma_mapping()

    def _load_figma_mapping(self):
        """Load tokens documented in FIGMA-TOKEN-USAGE-MAPPING.md"""
        try:
            with open(self.figma_mapping_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract token paths from markdown (simple pattern matching)
                # Tokens are usually in format: `color/interactive/primary/fill/default`
                token_pattern = r'`([a-z0-9\-/\.]+)`'
                matches = re.findall(token_pattern, content)
                for match in matches:
                    # Convert to dot notation
                    self.figma_documented_tokens.add(match.replace('/', '.'))
        except Exception as e:
            print(f"Warning: Could not load Figma mapping file: {e}")

    def validate(self) -> bool:
        """Main validation entry point. Returns True if validation passes."""
        print(f"Validating token descriptions in: {self.tokens_path}")
        print("-" * 70)

        try:
            with open(self.tokens_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading tokens file: {e}")
            return False

        # Traverse token tree
        self._traverse(data, [])

        # Print results
        self._print_results()

        # Pass if no critical issues
        return len([i for i in self.issues if i['severity'] == 'error']) == 0

    def _traverse(self, obj, path_parts: List[str]):
        """Recursively traverse token tree and validate descriptions"""
        if isinstance(obj, dict):
            # Check if this is a leaf token node (has $type/$value or type/value)
            is_token = (
                ("$type" in obj and "$value" in obj) or
                ("type" in obj and "value" in obj)
            )

            if is_token:
                self.stats["total_tokens"] += 1
                token_path = ".".join(path_parts)

                # Identify tier
                tier = self._identify_tier(path_parts)

                if tier == "core":
                    self.stats["core_tokens"] += 1
                elif tier == "brand":
                    self.stats["brand_tokens"] += 1
                elif tier == "semantic":
                    self.stats["semantic_tokens"] += 1
                elif tier == "component":
                    self.stats["component_tokens"] += 1
                else:
                    self.stats["unknown_tokens"] += 1

                # Check for description
                has_description = "description" in obj or "$description" in obj

                if has_description:
                    desc_key = "$description" if "$description" in obj else "description"
                    description = obj[desc_key]

                    if description and description.strip():
                        self.stats["tokens_with_descriptions"] += 1
                        self._validate_description(token_path, description, tier)
                    else:
                        self.stats["tokens_without_descriptions"] += 1
                        self._add_issue(
                            token_path,
                            "Empty description",
                            "warning",
                            "Token has empty or null description"
                        )
                else:
                    self.stats["tokens_without_descriptions"] += 1

                # Don't recurse into token leaf nodes
                return

            # Recursively process children (skip known non-token keys)
            for key, value in obj.items():
                if key not in SKIP_KEYS:
                    self._traverse(value, path_parts + [key])

    def _identify_tier(self, path_parts: List[str]) -> str:
        """Identify token tier from path parts.

        Our 4-tier hierarchy:
        - Core (global): core.dimension.*, core.typography.*, core.border.*, core.color.modify.*
        - Brand (core): color.brand.*, color.accent.*, color.neutrals.*, color.common.*, color.ism.*
        - Semantic: color.interactive.*, color.text.*, color.input.*, color.feedback.*,
                    color.surface.*, color.elevation.*, color.status.*, color.border.*,
                    color.selected.*, color.active.*, color.disabled.*, color.focus.*,
                    typography.*, borderRadius.*, border.interactive.*
        - Component: icon.*, layout.*, button.*
        """
        if len(path_parts) == 0:
            return "unknown"

        first = path_parts[0].lower()

        # Core tier: foundation primitives (in global/ folder, JSON root is "core")
        if first == "core":
            return "core"

        # Brand tier: brand colors (in core/ folder, JSON root is "color")
        if first == "color":
            if len(path_parts) > 1:
                second = path_parts[1].lower()
                # Brand-level color groups (raw values, no semantic meaning)
                if second in ("brand", "accent", "neutrals", "common", "ism"):
                    return "brand"
            # Otherwise it's a semantic color token
            return "semantic"

        # Semantic tier keywords
        semantic_keywords = {
            "interactive", "text", "input", "feedback", "border", "surface",
            "elevation", "status", "disabled", "focus", "typography",
            "borderradius", "selected", "active"
        }
        for part in path_parts:
            if part.lower() in semantic_keywords:
                return "semantic"

        # Component tier keywords
        component_keywords = {
            "button", "icon", "layout", "container", "badge", "column",
            "tabs", "tooltip", "accordion", "segment", "stepper",
            "selectioncontrol",
        }
        for part in path_parts:
            if part.lower() in component_keywords:
                return "component"

        return "unknown"

    def _validate_description(self, token_path: str, description: str, tier: str):
        """Validate a single token description"""
        # Track for duplicate detection
        desc_lower = description.strip().lower()
        if desc_lower not in self._seen_descriptions:
            self._seen_descriptions[desc_lower] = []
        self._seen_descriptions[desc_lower].append(token_path)

        desc_length = len(description)

        # Check length
        if desc_length < TARGET_MIN_LENGTH or desc_length > TARGET_MAX_LENGTH:
            self.stats["length_warnings"] += 1
            severity = "warning" if (desc_length >= 15 and desc_length <= 60) else "error"
            self._add_issue(
                token_path,
                f"Description length: {desc_length} chars",
                severity,
                f"Target: {TARGET_MIN_LENGTH}-{TARGET_MAX_LENGTH} chars. Current: '{description}'"
            )
        else:
            self.stats["length_ok"] += 1

        # Check for unit references
        for pattern in UNIT_PATTERNS:
            if re.search(pattern, description, re.IGNORECASE):
                self.stats["unit_references"] += 1
                self._add_issue(
                    token_path,
                    "Unit reference found",
                    "error",
                    f"Description contains unit reference: '{description}'"
                )
                break

        # Check for platform references
        for pattern in PLATFORM_PATTERNS:
            if re.search(pattern, description, re.IGNORECASE):
                self.stats["platform_references"] += 1
                self._add_issue(
                    token_path,
                    "Platform reference found",
                    "error",
                    f"Description contains platform reference: '{description}'"
                )
                break

        # Check for component mentions (semantic/component tokens)
        if tier in ["semantic", "component"]:
            # Specific component/context keywords — intentionally excludes
            # overly broad words like "text" and "surface" that match almost
            # anything and dilute the check.
            component_keywords = [
                "button", "input", "card", "banner", "modal", "dialog", "table",
                "badge", "tooltip", "icon", "field", "tab", "stepper", "toggle",
                "checkbox", "radio", "switch", "dropdown", "popover", "menu",
                "accordion", "slider", "counter", "control",
            ]
            # Context keywords that indicate the description mentions a usage
            # context even if it's not a specific component name.
            context_keywords = [
                "heading", "body", "caption", "label", "cta", "action",
                "overlay", "elevation", "shadow", "canvas",
            ]
            has_component = any(kw in description.lower() for kw in component_keywords)
            has_context = any(kw in description.lower() for kw in context_keywords)

            if not has_component and not has_context:
                self.stats["missing_components"] += 1
                self._add_issue(
                    token_path,
                    "No component mentioned",
                    "warning",
                    f"Semantic/component token should mention actual components: '{description}'"
                )

        # Check Figma context documentation
        if tier in ["semantic", "component"] and self.figma_documented_tokens:
            if token_path not in self.figma_documented_tokens:
                self.stats["missing_figma_context"] += 1
                self._add_issue(
                    token_path,
                    "Missing Figma context",
                    "info",
                    "Token not documented in FIGMA-TOKEN-USAGE-MAPPING.md"
                )

    def _add_issue(self, token_path: str, issue_type: str, severity: str, detail: str):
        """Add a validation issue"""
        self.issues.append({
            "token": token_path,
            "type": issue_type,
            "severity": severity,
            "detail": detail
        })

    def _print_results(self):
        """Print validation results"""
        print("\n" + "=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)

        # Statistics
        print("\nToken Statistics:")
        print(f"   Total tokens: {self.stats['total_tokens']}")
        print(f"   Tokens with descriptions: {self.stats['tokens_with_descriptions']}")
        print(f"   Tokens without descriptions: {self.stats['tokens_without_descriptions']}")
        print(f"\n   By tier:")
        print(f"   - Core (global): {self.stats['core_tokens']}")
        print(f"   - Brand (core): {self.stats['brand_tokens']}")
        print(f"   - Semantic: {self.stats['semantic_tokens']}")
        print(f"   - Component: {self.stats['component_tokens']}")
        if self.stats['unknown_tokens'] > 0:
            print(f"   - Unknown: {self.stats['unknown_tokens']}")

        # Description quality
        coverage_pct = (self.stats['tokens_with_descriptions'] / self.stats['total_tokens'] * 100) if self.stats['total_tokens'] > 0 else 0
        print(f"\n   Description Coverage: {coverage_pct:.1f}%")

        if self.stats['tokens_with_descriptions'] > 0:
            length_ok_pct = (self.stats['length_ok'] / self.stats['tokens_with_descriptions'] * 100)
            print(f"\n   Length Quality:")
            print(f"   - Within target ({TARGET_MIN_LENGTH}-{TARGET_MAX_LENGTH} chars): {self.stats['length_ok']} ({length_ok_pct:.1f}%)")
            print(f"   - Outside target: {self.stats['length_warnings']}")

        # Issues summary
        errors = [i for i in self.issues if i['severity'] == 'error']
        warnings = [i for i in self.issues if i['severity'] == 'warning']
        infos = [i for i in self.issues if i['severity'] == 'info']

        print(f"\n   Issues Found:")
        print(f"   - Errors: {len(errors)}")
        print(f"   - Warnings: {len(warnings)}")
        print(f"   - Info: {len(infos)}")

        if self.stats['unit_references'] > 0:
            print(f"\n   - Unit references: {self.stats['unit_references']}")

        if self.stats['platform_references'] > 0:
            print(f"   - Platform references: {self.stats['platform_references']}")

        if self.stats['missing_components'] > 0:
            print(f"   - Missing component mentions: {self.stats['missing_components']}")

        if self.stats['missing_figma_context'] > 0:
            print(f"   - Missing Figma context: {self.stats['missing_figma_context']}")

        # Duplicate description detection
        duplicates = {desc: paths for desc, paths in self._seen_descriptions.items()
                      if len(paths) > 1}
        if duplicates:
            # Filter out core tokens where duplicates are expected (e.g. "Medium spacing.")
            non_core_duplicates = {}
            for desc, paths in duplicates.items():
                non_core = [p for p in paths if not p.startswith("core.")]
                if len(non_core) > 1:
                    non_core_duplicates[desc] = non_core

            if non_core_duplicates:
                print(f"\n   Duplicate descriptions (non-core): {len(non_core_duplicates)}")
                for desc, paths in list(non_core_duplicates.items())[:5]:
                    print(f"      \"{desc}\" used by {len(paths)} tokens:")
                    for p in paths[:3]:
                        print(f"         - {p}")
                    if len(paths) > 3:
                        print(f"         ... and {len(paths) - 3} more")

        # Show sample issues
        if errors:
            print(f"\n   Sample Errors (showing first 10):")
            for issue in errors[:10]:
                print(f"   {issue['token']}")
                print(f"      {issue['type']}: {issue['detail']}")

        if warnings and not errors:
            print(f"\n   Sample Warnings (showing first 10):")
            for issue in warnings[:10]:
                print(f"   {issue['token']}")
                print(f"      {issue['type']}: {issue['detail']}")

        # Final verdict
        print("\n" + "=" * 70)
        if len(errors) == 0:
            print("VALIDATION PASSED")
            if warnings:
                print(f"   ({len(warnings)} warnings - review recommended)")
        else:
            print("VALIDATION FAILED")
            print(f"   Fix {len(errors)} errors before proceeding")
        print("=" * 70 + "\n")


def collect_token_files(directory: str) -> List[str]:
    """Walk a directory and return all token JSON files (excluding $-prefixed metadata)."""
    token_files = []
    for root, _dirs, files in os.walk(directory):
        for filename in sorted(files):
            if filename.endswith(".json") and not filename.startswith("$"):
                token_files.append(os.path.join(root, filename))
    return token_files


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  Single file:  python validate-descriptions.py path/to/tokens.json"
            " [--figma-mapping path/to/mapping.md]\n"
            "  Directory:    python validate-descriptions.py --dir path/to/tokens/"
            " [--figma-mapping path/to/mapping.md]"
        )
        sys.exit(1)

    figma_mapping_path = None

    # Parse optional --figma-mapping argument
    if "--figma-mapping" in sys.argv:
        idx = sys.argv.index("--figma-mapping")
        if idx + 1 < len(sys.argv):
            figma_mapping_path = sys.argv[idx + 1]

    # ── Directory mode ────────────────────────────────────────────────────────
    if "--dir" in sys.argv:
        idx = sys.argv.index("--dir")
        if idx + 1 >= len(sys.argv):
            print("Error: --dir requires a directory path argument")
            sys.exit(1)
        dir_path = sys.argv[idx + 1]

        if not os.path.isdir(dir_path):
            print(f"Error: Directory not found: {dir_path}")
            sys.exit(1)

        token_files = collect_token_files(dir_path)
        if not token_files:
            print(f"No token JSON files found in: {dir_path}")
            sys.exit(1)

        print(f"Validating {len(token_files)} token file(s) in: {dir_path}")
        print("=" * 70)

        all_passed = True
        aggregate_issues: List[Dict] = []
        aggregate_stats: Dict = {
            "total_tokens": 0,
            "tokens_with_descriptions": 0,
            "tokens_without_descriptions": 0,
            "core_tokens": 0,
            "brand_tokens": 0,
            "semantic_tokens": 0,
            "component_tokens": 0,
            "unknown_tokens": 0,
            "length_ok": 0,
            "length_warnings": 0,
            "unit_references": 0,
            "platform_references": 0,
            "missing_components": 0,
            "missing_figma_context": 0,
        }

        for tokens_path in token_files:
            validator = TokenValidator(tokens_path, figma_mapping_path)
            passed = validator.validate()
            if not passed:
                all_passed = False
            # Accumulate aggregate stats
            for key in aggregate_stats:
                aggregate_stats[key] += validator.stats.get(key, 0)
            aggregate_issues.extend(validator.issues)

        # Print aggregate summary
        total_files = len(token_files)
        errors = [i for i in aggregate_issues if i["severity"] == "error"]
        warnings = [i for i in aggregate_issues if i["severity"] == "warning"]
        print("\n" + "=" * 70)
        print(f"AGGREGATE SUMMARY ({total_files} files)")
        print("=" * 70)
        print(f"  Total tokens:            {aggregate_stats['total_tokens']}")
        total = aggregate_stats["total_tokens"]
        with_desc = aggregate_stats["tokens_with_descriptions"]
        coverage = (with_desc / total * 100) if total > 0 else 0
        print(f"  Description coverage:    {with_desc}/{total} ({coverage:.1f}%)")
        print(f"  Errors:                  {len(errors)}")
        print(f"  Warnings:                {len(warnings)}")
        if aggregate_stats["unit_references"] > 0:
            print(f"  Unit references:         {aggregate_stats['unit_references']}")
        if aggregate_stats["platform_references"] > 0:
            print(f"  Platform references:     {aggregate_stats['platform_references']}")
        print("=" * 70)
        if all_passed:
            print("ALL FILES PASSED")
        else:
            print("VALIDATION FAILED — see per-file output above")
        print("=" * 70 + "\n")

        sys.exit(0 if all_passed else 1)

    # ── Single-file mode ──────────────────────────────────────────────────────
    tokens_path = sys.argv[1]

    if not os.path.exists(tokens_path):
        print(f"Error: Tokens file not found: {tokens_path}")
        sys.exit(1)

    validator = TokenValidator(tokens_path, figma_mapping_path)
    passed = validator.validate()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
