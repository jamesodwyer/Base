#!/usr/bin/env python3
"""
Resolve design tokens: follow alias chains, compute HSL modifiers,
and output a flat JSON of Figma-ready variable definitions.

Usage:
    python3 resolve_tokens.py --tokens-dir tokens/ --component button
    python3 resolve_tokens.py --tokens-dir tokens/ --all
    python3 resolve_tokens.py --tokens-dir tokens/ --token-path color.interactive.primary.fill.hover

Output: JSON with resolved variables, ready for Figma MCP calls.
"""

import argparse
import colorsys
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional


def load_all_tokens(tokens_dir: str) -> dict[str, Any]:
    """Load all token JSON files into a unified flat dict keyed by dot-notation path."""
    flat: dict[str, Any] = {}
    tokens_path = Path(tokens_dir)

    for json_file in tokens_path.rglob("*.json"):
        if json_file.name.startswith("$"):
            continue  # skip $metadata.json, $themes.json

        with open(json_file) as f:
            data = json.load(f)

        _flatten_tokens(data, [], flat)

    return flat


def _flatten_tokens(
    obj: Any,
    path: list[str],
    flat: dict[str, Any],
) -> None:
    """Recursively flatten nested token JSON into dot-notation keyed entries."""
    if isinstance(obj, dict):
        if "$value" in obj:
            dot_path = ".".join(path)
            flat[dot_path] = obj
        else:
            for key, value in obj.items():
                if key.startswith("$"):
                    continue
                _flatten_tokens(value, path + [key], flat)


def resolve_modifier_amount(value_ref: str, flat_tokens: dict[str, Any]) -> float:
    """Resolve a modifier reference like {core.color.modify.100} to a float."""
    ref = value_ref.strip("{}")
    token = flat_tokens.get(ref)

    if not token:
        raise ValueError(f"Cannot resolve modifier reference: {value_ref}")

    raw = str(token["$value"])

    # Handle expressions like "{core.color.modify.100}*2"
    ref_match = re.match(r"\{([^}]+)\}\s*([*/+-])\s*([\d.]+)", raw)
    if ref_match:
        base_ref = ref_match.group(1)
        operator = ref_match.group(2)
        operand = float(ref_match.group(3))
        base_val = resolve_modifier_amount(f"{{{base_ref}}}", flat_tokens)
        if operator == "*":
            return base_val * operand
        elif operator == "/":
            return base_val / operand
        elif operator == "+":
            return base_val + operand
        elif operator == "-":
            return base_val - operand

    # Handle division: {ref}/2
    div_match = re.match(r"\{([^}]+)\}\s*/\s*([\d.]+)", raw)
    if div_match:
        base_ref = div_match.group(1)
        divisor = float(div_match.group(2))
        base_val = resolve_modifier_amount(f"{{{base_ref}}}", flat_tokens)
        return base_val / divisor

    # Direct numeric value
    try:
        return float(raw)
    except ValueError:
        pass

    # Another reference
    if raw.startswith("{") and raw.endswith("}"):
        return resolve_modifier_amount(raw, flat_tokens)

    raise ValueError(f"Cannot parse modifier value: {raw}")


def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    """Convert #RRGGBB to (r, g, b) floats 0-1."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return (r, g, b)


def rgb_to_hex(r: float, g: float, b: float) -> str:
    """Convert (r, g, b) floats 0-1 to #RRGGBB."""
    return f"#{int(round(r*255)):02x}{int(round(g*255)):02x}{int(round(b*255)):02x}"


def apply_modifier(
    base_hex: str,
    modifier_type: str,
    amount: float,
) -> tuple[str, float]:
    """
    Apply a Token Studio HSL modifier.

    Returns (hex_color, opacity).
    darken/lighten return modified hex with opacity 1.0.
    alpha returns original hex with the amount as opacity.
    """
    if modifier_type == "alpha":
        return (base_hex, amount)

    r, g, b = hex_to_rgb(base_hex)
    # Python colorsys: rgb_to_hls returns (h, l, s) -- L before S
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    if modifier_type == "darken":
        l = l * (1 - amount)
    elif modifier_type == "lighten":
        l = l + (1 - l) * amount
    else:
        raise ValueError(f"Unknown modifier type: {modifier_type}")

    l = max(0.0, min(1.0, l))
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return (rgb_to_hex(r2, g2, b2), 1.0)


def resolve_color_value(
    token_path: str,
    flat_tokens: dict[str, Any],
    visited: Optional[set[str]] = None,
) -> tuple[str, float]:
    """
    Resolve a color token to its final hex value and opacity.
    Follows alias chains and applies modifiers.

    Returns (hex_color, opacity).
    """
    if visited is None:
        visited = set()

    if token_path in visited:
        raise ValueError(f"Circular reference detected: {token_path}")
    visited.add(token_path)

    token = flat_tokens.get(token_path)
    if not token:
        raise ValueError(f"Token not found: {token_path}")

    raw_value = str(token["$value"])

    # Check for modifier
    modifier = (
        token.get("$extensions", {})
        .get("studio.tokens", {})
        .get("modify")
    )

    # Resolve the base value
    if raw_value.startswith("{") and raw_value.endswith("}"):
        ref_path = raw_value.strip("{}")
        base_hex, base_opacity = resolve_color_value(ref_path, flat_tokens, visited)
    elif raw_value.startswith("#"):
        base_hex = raw_value
        base_opacity = 1.0
    else:
        raise ValueError(f"Unexpected color value format: {raw_value} in {token_path}")

    # Apply modifier if present
    if modifier:
        mod_type = modifier["type"]
        mod_value_ref = modifier["value"]
        mod_amount = resolve_modifier_amount(mod_value_ref, flat_tokens)
        return apply_modifier(base_hex, mod_type, mod_amount)

    return (base_hex, base_opacity)


def resolve_dimension_value(
    token_path: str,
    flat_tokens: dict[str, Any],
    visited: Optional[set[str]] = None,
) -> float:
    """Resolve a dimension/spacing/border token to a numeric value."""
    if visited is None:
        visited = set()

    if token_path in visited:
        raise ValueError(f"Circular reference detected: {token_path}")
    visited.add(token_path)

    token = flat_tokens.get(token_path)
    if not token:
        raise ValueError(f"Token not found: {token_path}")

    raw_value = str(token["$value"])

    # Handle expressions: "{core.dimension.100}*2"
    ref_match = re.match(r"\{([^}]+)\}\s*([*/+-])\s*([\d.]+)", raw_value)
    if ref_match:
        ref_path = ref_match.group(1)
        operator = ref_match.group(2)
        operand = float(ref_match.group(3))
        base = resolve_dimension_value(ref_path, flat_tokens, visited)
        if operator == "*":
            return base * operand
        elif operator == "/":
            return base / operand
        elif operator == "+":
            return base + operand
        elif operator == "-":
            return base - operand

    # Handle division: "{ref}/2"
    div_match = re.match(r"\{([^}]+)\}\s*/\s*([\d.]+)", raw_value)
    if div_match:
        ref_path = div_match.group(1)
        divisor = float(div_match.group(2))
        return resolve_dimension_value(ref_path, flat_tokens, visited) / divisor

    # Simple reference
    if raw_value.startswith("{") and raw_value.endswith("}"):
        ref_path = raw_value.strip("{}")
        return resolve_dimension_value(ref_path, flat_tokens, visited)

    # Numeric value (possibly with "px" suffix)
    numeric = raw_value.replace("px", "").strip()
    try:
        return float(numeric)
    except ValueError:
        raise ValueError(f"Cannot parse dimension value: {raw_value} in {token_path}")


def is_alias_only(token: dict[str, Any]) -> bool:
    """Check if a token is a pure alias (no modifier)."""
    raw_value = str(token["$value"])
    has_modifier = (
        token.get("$extensions", {})
        .get("studio.tokens", {})
        .get("modify")
    )
    is_reference = raw_value.startswith("{") and raw_value.endswith("}")
    return is_reference and not has_modifier


def get_alias_target(token: dict[str, Any]) -> Optional[str]:
    """Get the dot-notation path this token aliases, or None."""
    if is_alias_only(token):
        return str(token["$value"]).strip("{}")
    return None


def determine_figma_type(token: dict[str, Any]) -> str:
    """Map DTCG $type to Figma variable type."""
    t = token.get("$type", "")
    if t == "color":
        return "COLOR"
    elif t in ("dimension", "spacing", "borderRadius", "borderWidth", "sizing"):
        return "FLOAT"
    return "FLOAT"  # default


def determine_collection(token_path: str) -> str:
    """Determine which Figma collection a token belongs to."""
    if token_path.startswith("core."):
        return "Global"
    if token_path.startswith("color.brand.") or token_path.startswith("color.accent.") or token_path.startswith("color.neutrals.") or token_path.startswith("color.common."):
        return "Brand"
    if token_path.startswith("color.") or token_path.startswith("borderRadius.") or token_path.startswith("border."):
        return "Semantic"
    # Component tokens: anything else (button.*, badge.*, stepper.*, layout.*)
    return "Component"


def to_figma_name(dot_path: str) -> str:
    """Convert dot-notation to Figma slash-notation."""
    return dot_path.replace(".", "/")


def resolve_token(
    token_path: str,
    flat_tokens: dict[str, Any],
) -> dict[str, Any]:
    """Resolve a single token to a Figma-ready variable definition."""
    token = flat_tokens[token_path]
    figma_type = determine_figma_type(token)
    collection = determine_collection(token_path)
    figma_name = to_figma_name(token_path)

    result: dict[str, Any] = {
        "token_path": token_path,
        "figma_name": figma_name,
        "figma_type": figma_type,
        "collection": collection,
    }

    alias_target = get_alias_target(token)
    if alias_target:
        result["alias_of"] = to_figma_name(alias_target)
        result["value_type"] = "alias"
    elif figma_type == "COLOR":
        hex_val, opacity = resolve_color_value(token_path, flat_tokens)
        r, g, b = hex_to_rgb(hex_val)
        result["value"] = {"r": round(r, 4), "g": round(g, 4), "b": round(b, 4), "a": round(opacity, 4)}
        result["hex"] = hex_val
        result["value_type"] = "computed" if token.get("$extensions", {}).get("studio.tokens", {}).get("modify") else "direct"
    else:
        resolved = resolve_dimension_value(token_path, flat_tokens)
        result["value"] = resolved
        result["value_type"] = "direct"

    return result


def find_component_tokens(
    component_name: str,
    flat_tokens: dict[str, Any],
) -> list[str]:
    """Find all token paths relevant to a component, including dependencies."""
    # Start with direct component tokens
    component_paths = [p for p in flat_tokens if p.startswith(f"{component_name}.")]

    # Also find semantic tokens that mention the component in their path
    # (e.g., color.interactive.* for buttons)
    semantic_color_paths = [p for p in flat_tokens if p.startswith("color.interactive.")]
    semantic_border_paths = [p for p in flat_tokens if p.startswith("borderRadius.") or p.startswith("border.")]

    # Collect all paths and their dependencies
    all_needed: set[str] = set()
    to_process = set(component_paths + semantic_color_paths + semantic_border_paths)

    while to_process:
        path = to_process.pop()
        if path in all_needed:
            continue
        all_needed.add(path)

        token = flat_tokens.get(path)
        if not token:
            continue

        # Find references in $value
        raw_value = str(token.get("$value", ""))
        refs = re.findall(r"\{([^}]+)\}", raw_value)
        for ref in refs:
            if ref in flat_tokens and ref not in all_needed:
                to_process.add(ref)

        # Find references in modifier
        modifier = token.get("$extensions", {}).get("studio.tokens", {}).get("modify", {})
        mod_value = modifier.get("value", "")
        mod_refs = re.findall(r"\{([^}]+)\}", str(mod_value))
        for ref in mod_refs:
            if ref in flat_tokens and ref not in all_needed:
                to_process.add(ref)

    return sorted(all_needed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve design tokens for Figma")
    parser.add_argument("--tokens-dir", default="tokens", help="Path to tokens directory")
    parser.add_argument("--component", help="Component name (e.g., button, badge, stepper)")
    parser.add_argument("--token-path", help="Single token path to resolve")
    parser.add_argument("--all", action="store_true", help="Resolve all tokens")
    args = parser.parse_args()

    flat_tokens = load_all_tokens(args.tokens_dir)

    if args.token_path:
        if args.token_path not in flat_tokens:
            print(f"Error: token '{args.token_path}' not found", file=sys.stderr)
            sys.exit(1)
        result = resolve_token(args.token_path, flat_tokens)
        print(json.dumps(result, indent=2))

    elif args.component:
        paths = find_component_tokens(args.component, flat_tokens)
        results = []
        errors = []
        for path in paths:
            try:
                results.append(resolve_token(path, flat_tokens))
            except ValueError as e:
                errors.append({"token_path": path, "error": str(e)})

        output = {
            "component": args.component,
            "total_variables": len(results),
            "by_collection": {},
            "variables": results,
        }
        if errors:
            output["errors"] = errors

        # Group counts by collection
        for var in results:
            coll = var["collection"]
            output["by_collection"][coll] = output["by_collection"].get(coll, 0) + 1

        print(json.dumps(output, indent=2))

    elif args.all:
        results = []
        errors = []
        for path in sorted(flat_tokens.keys()):
            try:
                results.append(resolve_token(path, flat_tokens))
            except ValueError as e:
                errors.append({"token_path": path, "error": str(e)})

        output = {
            "total_variables": len(results),
            "variables": results,
        }
        if errors:
            output["errors"] = errors

        print(json.dumps(output, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
