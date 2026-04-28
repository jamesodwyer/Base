#!/usr/bin/env python3
"""
Generate $description fields for all design tokens based on pattern templates.
Processes all token files in the tokens/ directory.
"""

import json
import os
import sys
from pathlib import Path

# Allow importing run_tracker from the same scripts/ directory.
sys.path.insert(0, str(Path(__file__).parent))
from run_tracker import load_overrides, save_run_manifest


# ─── DESCRIPTION PATTERNS ───────────────────────────────────────────────────

CORE_DIMENSION = {
    "zero": "Zero spacing. Removes all space.",
    "50": "Minimal spacing. Use for tight gaps.",
    "100": "Base spacing unit. Foundation for scale.",
    "150": "1.5x base spacing.",
    "200": "Small spacing. Compact gaps.",
    "250": "Small-medium spacing.",
    "300": "Medium spacing.",
    "350": "Medium spacing.",
    "400": "Medium spacing.",
    "450": "Medium-large spacing.",
    "500": "Large spacing. Section gaps.",
    "550": "Large spacing. Section gaps.",
    "600": "Extra large spacing.",
    "650": "Extra large spacing.",
    "700": "2X large spacing.",
    "750": "2X large spacing.",
    "800": "2X large spacing.",
    "850": "2X large spacing.",
    "900": "3X large spacing.",
    "1000": "3X large spacing.",
    "1100": "3X large spacing.",
    "1200": "3X large spacing.",
    "1300": "4X large spacing.",
    "1400": "4X large spacing.",
    "1500": "4X large spacing.",
    "1600": "5X large spacing.",
    "1700": "5X large spacing.",
    "1800": "5X large spacing.",
    "1900": "6X large spacing.",
    "2000": "6X large spacing.",
}

CORE_FONT_WEIGHT = {
    "light": "Light weight (300). Use for subtle text.",
    "regular": "Regular weight (400). Default text.",
    "semibold": "Semibold weight (600). Use for emphasis.",
    "bold": "Bold weight (700). Use for emphasis.",
    "black": "Black weight (900). Use for headings.",
}

CORE_FONT_SIZE = {
    "25": "Font size. Scale: 0.63x.",
    "50": "Font size. Scale: 0.75x.",
    "75": "Font size. Scale: 0.88x.",
    "100": "Base font size. Foundation for scale.",
    "150": "Font size. Scale: 1.13x.",
    "175": "Font size. Scale: 1.25x.",
    "200": "Font size. Scale: 1.5x.",
    "250": "Font size. Scale: 1.75x.",
    "300": "Font size. Scale: 2x.",
    "350": "Font size. Scale: 2.13x.",
    "400": "Font size. Scale: 2.25x.",
    "450": "Font size. Scale: 2.5x.",
    "500": "Font size. Scale: 2.75x.",
    "550": "Font size. Scale: 3x.",
    "600": "Font size. Scale: 3.13x.",
    "650": "Font size. Scale: 3.5x.",
    "700": "Font size. Scale: 4x.",
    "750": "Font size. Scale: 4.5x.",
    "800": "Font size. Scale: 5x.",
    "850": "Font size. Scale: 5.5x.",
    "900": "Font size. Scale: 6x.",
}

CORE_LINE_HEIGHT = {
    "25": "Line height. Scale: 0.63x.",
    "50": "Line height. Scale: 0.75x.",
    "75": "Line height. Scale: 0.88x.",
    "100": "Base line height. Foundation for scale.",
    "150": "Line height. Scale: 1.13x.",
    "175": "Line height. Scale: 1.25x.",
    "200": "Line height. Scale: 1.5x.",
    "250": "Line height. Scale: 1.75x.",
    "300": "Line height. Scale: 2x.",
    "350": "Line height. Scale: 2.13x.",
    "400": "Line height. Scale: 2.25x.",
    "450": "Line height. Scale: 2.5x.",
    "500": "Line height. Scale: 2.75x.",
    "550": "Line height. Scale: 3x.",
    "600": "Line height. Scale: 3.13x.",
    "650": "Line height. Scale: 3.25x.",
    "700": "Line height. Scale: 3.38x.",
    "800": "Line height. Scale: 4x.",
    "full": "Full line height. 100%.",
}

CORE_LETTER_SPACING = {
    "100": "1% letter spacing.",
    "300": "3% letter spacing.",
    "800": "15% letter spacing. Wide text.",
    "neg100": "Negative letter spacing. Tighter text.",
    "neg200": "Negative letter spacing. Tighter text.",
    "neg300": "Negative letter spacing. Tightest text.",
}

CORE_BORDER_RADIUS = {
    "xSmall": "Extra small corner radius.",
    "small": "Small corner radius.",
    "medium": "Medium corner radius.",
    "large": "Large corner radius.",
    "xLarge": "Extra large corner radius.",
    "xxLarge": "2X large corner radius.",
    "full": "Full corner radius. Pill shape.",
}

CORE_BORDER_WIDTH = {
    "xSmall": "Extra small border width.",
    "small": "Small border width.",
    "medium": "Medium border width.",
    "large": "Large border width.",
    "xLarge": "Extra large border width.",
}

# Modify tokens nested under core.color.modify
CORE_MODIFY = {
    "zero": "Zero modifier. No modification.",
    "50": "0.05 modifier. For lighten/darken/alpha.",
    "100": "0.1 modifier. For lighten/darken/alpha.",
    "150": "0.15 modifier. For lighten/darken/alpha.",
    "200": "0.2 modifier. For lighten/darken/alpha.",
    "250": "0.25 modifier. For lighten/darken/alpha.",
    "300": "0.3 modifier. For lighten/darken/alpha.",
    "350": "0.35 modifier. For lighten/darken/alpha.",
    "390": "0.39 modifier. For lighten/darken/alpha.",
    "400": "0.4 modifier. For lighten/darken/alpha.",
    "450": "0.45 modifier. For lighten/darken/alpha.",
    "500": "0.5 modifier. For lighten/darken/alpha.",
    "550": "0.55 modifier. For lighten/darken/alpha.",
    "600": "0.6 modifier. For lighten/darken/alpha.",
    "650": "0.65 modifier. For lighten/darken/alpha.",
    "700": "0.7 modifier. For lighten/darken/alpha.",
    "750": "0.75 modifier. For lighten/darken/alpha.",
    "800": "0.8 modifier. For lighten/darken/alpha.",
    "840": "0.84 modifier. For lighten/darken/alpha.",
    "850": "0.85 modifier. For lighten/darken/alpha.",
    "900": "0.9 modifier. For lighten/darken/alpha.",
    "920": "0.92 modifier. For lighten/darken/alpha.",
    "950": "0.95 modifier. For lighten/darken/alpha.",
    "960": "0.96 modifier. For lighten/darken/alpha.",
    "1000": "1.0 modifier. For lighten/darken/alpha.",
}

# ─── BRAND COLOR PATTERNS ───────────────────────────────────────────────────

BRAND_COLORS = {
    "brand.01": "Primary brand color. Main actions and links.",
    "brand.01-inverse": "Inverse brand color. For dark backgrounds.",
    "brand.02": "Secondary brand color. Headings and titles.",
    "brand.03": "Alternate brand color. Page backgrounds.",
    "accent.green": "Green accent. Success states.",
    "accent.red": "Red accent. Error states.",
    "accent.purple": "Purple accent. Decorative use.",
    "accent.orange": "Orange accent. Warning states.",
    "accent.turquoise": "Turquoise accent. Decorative use.",
    "accent.yellow": "Yellow accent. Highlight states.",
    "accent.blue": "Blue accent. Info states.",
    "accent.magenta": "Magenta accent. Decorative use.",
    "neutrals.grey.100": "Lightest neutral grey.",
    "neutrals.grey.200": "Light neutral grey.",
    "neutrals.grey.300": "Mid-light neutral grey.",
    "neutrals.grey.400": "Mid neutral grey.",
    "neutrals.grey.500": "Mid-tone neutral grey.",
    "neutrals.grey.600": "Dark neutral grey.",
    "common.white": "Pure white. Base light value.",
    "common.black": "Pure black. Base dark value.",
    "ism.blue": "ISM blue. Classification color.",
}

# ─── SEMANTIC INTERACTIVE PATTERNS ──────────────────────────────────────────

# Button type mapping: token name -> visual style for descriptions
BUTTON_TYPES = {
    "primary": "Solid button",
    "secondary": "Outline button",
    "ghost": "Ghost button",
    "tertiary": "Tertiary button",
    "inverse": "Inverse button",
    "transaction": "Transaction button",
}

INTERACTIVE_DEFAULT_DESCRIPTIONS = {
    "primary": {
        "fill": "Use for solid buttons. Primary CTAs.",
        "text": "Use for solid button text.",
        "icon": "Use for solid button icons.",
        "border": "Use for solid button borders.",
    },
    "secondary": {
        "fill": "Use for outline buttons. Secondary actions.",
        "text": "Use for outline button text.",
        "icon": "Use for outline button icons.",
        "border": "Use for outline button borders.",
    },
    "ghost": {
        "fill": "Use for ghost buttons. Minimal actions.",
        "text": "Use for ghost button text.",
        "icon": "Use for ghost button icons.",
        "border": "Use for ghost button borders.",
    },
    "tertiary": {
        "fill": "Use for tertiary buttons. Low emphasis.",
        "text": "Use for tertiary button text.",
        "icon": "Use for tertiary button icons.",
        "border": "Use for tertiary button borders.",
    },
    "inverse": {
        "fill": "Use for inverse buttons. Dark backgrounds.",
        "text": "Use for inverse button text.",
        "icon": "Use for inverse button icons.",
        "border": "Use for inverse button borders.",
    },
    "transaction": {
        "fill": "Use for transaction buttons. Purchase CTAs.",
        "text": "Use for transaction button text.",
        "icon": "Use for transaction button icons.",
        "border": "Use for transaction button borders.",
    },
}

STATE_PHRASES = {
    "hover": "on hover",
    "pressed": "when pressed",
    "disabled": "when disabled",
    "focus": "on focus",
    "active": "when active",
}

# ─── SEMANTIC TEXT PATTERNS ─────────────────────────────────────────────────

SEMANTIC_TEXT = {
    "primary": "Use for primary text. Main content.",
    "secondary": "Use for secondary text. Helper text.",
    "tertiary": "Use for tertiary text. Subtle content.",
    "disabled": "Use for disabled text. Inactive elements.",
    "placeholder": "Use for placeholder text. Inputs.",
    "inverse": "Use for text on dark backgrounds.",
    "onAccent": "Use for text on colored backgrounds.",
    "error": "Use for error text. Validation.",
    "success": "Use for success text. Confirmations.",
    "warning": "Use for warning text. Cautions.",
    "info": "Use for info text. Tips.",
    "brand": "Use for brand-colored text.",
    "link": "Use for link text.",
}

# ─── SEMANTIC INPUT PATTERNS ────────────────────────────────────────────────

SEMANTIC_INPUT_DEFAULTS = {
    "fill": "Use for input backgrounds. Text fields.",
    "border": "Use for input borders. Text fields.",
    "text": "Use for input text.",
    "icon": "Use for input icons.",
}

# ─── SEMANTIC FEEDBACK PATTERNS ─────────────────────────────────────────────

FEEDBACK_TYPES = {
    "error": "error",
    "success": "success",
    "warning": "warning",
    "info": "info",
}

FEEDBACK_PROPERTIES = {
    "fill": "{type} backgrounds. Banners.",
    "border": "{type} borders. Banners.",
    "text": "{type} text. Messages.",
    "icon": "{type} icons. Banners.",
}

# ─── SEMANTIC SURFACE PATTERNS ──────────────────────────────────────────────

SEMANTIC_SURFACE = {
    "primary": "Brand surface. Branded container backgrounds.",
    "light": "Light surface. Card or container backgrounds.",
    "neutralLighter": "Lightest neutral surface background.",
    "neutralLight": "Light neutral surface background.",
    "neutralDark": "Dark neutral surface background.",
    "neutralDarker": "Darker neutral surface background.",
    "neutralDarkest": "Darkest neutral surface background.",
    "inverse": "Inverse surface. Dark container backgrounds.",
}

# ─── SEMANTIC BORDER PATTERNS ───────────────────────────────────────────────

SEMANTIC_BORDER = {
    "default": "Use for standard borders. Default state.",
    "subtle": "Use for subtle borders. Low contrast.",
    "strong": "Use for strong borders. High contrast.",
    "hover": "Border color on hover.",
    "focus": "Border color on focus. Accessibility.",
    "disabled": "Border color when disabled.",
    "error": "Use for error borders.",
    "success": "Use for success borders.",
    "warning": "Use for warning borders.",
    "brand": "Use for brand-colored borders.",
    "primary": "Use for primary borders.",
    "secondary": "Use for secondary borders.",
    "inverse": "Use for borders on dark backgrounds.",
    "onAccent": "Use for borders on accent backgrounds.",
}

# ─── SEMANTIC ELEVATION PATTERNS ────────────────────────────────────────────

SEMANTIC_ELEVATION = {
    "shadow": {
        "xSmall": "Use for subtle shadows. Slight depth.",
        "small": "Use for small shadows. Cards.",
        "medium": "Use for medium shadows. Dialogs.",
        "large": "Use for large shadows. Modals.",
        "xLarge": "Use for extra large shadows. Popovers.",
    },
    "base": "Use for elevation base. Internal mixin.",
    "overlay": "Use for modal overlays. Backgrounds.",
}

# ─── SEMANTIC STATUS PATTERNS ───────────────────────────────────────────────

# Generic - will be composed from path segments

# ─── SEMANTIC TYPOGRAPHY PATTERNS ───────────────────────────────────────────

SEMANTIC_TYPOGRAPHY = {
    "display.large": "Use for hero text. Largest display.",
    "display.medium": "Use for featured text. Medium display.",
    "display.small": "Use for prominent text. Small display.",
    "heading.large": "Use for page titles. Large heading.",
    "heading.medium": "Use for section titles. Medium heading.",
    "heading.small": "Use for subsection titles. Small heading.",
    "title.large": "Use for large UI titles. Dialogs/panels.",
    "title.medium": "Use for medium UI titles. Cards/sections.",
    "title.small": "Use for small UI titles. Components.",
    "label.large": "Use for large action labels. Buttons.",
    "label.medium": "Use for medium action labels. Buttons.",
    "label.small": "Use for small action labels. Tags.",
    "body.regular.large": "Use for large body text. Feature content.",
    "body.regular.medium": "Use for standard body text. Main content.",
    "body.regular.small": "Use for small body text. Captions.",
    "body.bold.large": "Use for large bold body text. Emphasis.",
    "body.bold.medium": "Use for bold body text. Emphasis.",
    "body.bold.small": "Use for small bold body text. Emphasis.",
    "caption": "Use for caption text. Metadata.",
}

# ─── SEMANTIC BORDER RADIUS PATTERNS ────────────────────────────────────────

SEMANTIC_BORDER_RADIUS = {
    "interactive.small": "Use for small interactive corners.",
    "interactive.medium": "Use for medium button corners.",
    "interactive.large": "Use for large button corners.",
    "interactive.full": "Use for pill button corners.",
    "input.small": "Use for small input corners.",
    "input.medium": "Use for medium input corners.",
    "input.large": "Use for large input corners.",
    "input.full": "Use for pill input corners.",
    "container.none": "Use for sharp container corners.",
    "container.small": "Use for small container corners.",
    "container.medium": "Use for medium container corners.",
    "container.large": "Use for large container corners.",
    "popover.none": "Use for sharp popover corners.",
    "popover.small": "Use for small popover corners.",
    "popover.medium": "Use for medium popover corners.",
    "popover.large": "Use for large popover corners.",
}

# ─── SEMANTIC INTERACTIVE BORDER PATTERNS ───────────────────────────────────

SEMANTIC_INTERACTIVE_BORDER = {
    "xSmall": "Use for default interactive borders.",
    "small": "Use for emphasized interactive borders.",
}

# ─── COMPONENT PATTERNS ─────────────────────────────────────────────────────

SIZE_LABELS = {
    "small": "small",
    "medium": "medium",
    "large": "large",
    "xLarge": "Extra large",
    "xxLarge": "XXL",
}

# ─── COMPONENT: STEPPER PATTERNS ───────────────────────────────────────────

STEPPER_CONTAINER = {
    "fill": "Stepper container background.",
    "border": "Stepper container border.",
}

STEPPER_COUNTER_DEFAULTS = {
    "fill": "Counter display background.",
    "border": "Counter display border.",
    "text": "Counter display text.",
}

# ─── SEMANTIC: SELECTION CONTROL PATTERNS ──────────────────────────────────

SELECTION_CONTROL = {
    "fill": {
        "default": "Use for selection control background.",
        "hover": "Selection control background on hover.",
        "pressed": "Selection control background when pressed.",
        "disabled": "Selection control background when disabled.",
    },
    "border": {
        "default": "Use for selection control border.",
        "hover": "Selection control border on hover.",
        "pressed": "Selection control border when pressed.",
        "error": "Selection control border for error state.",
        "focus": "Selection control focus ring.",
        "disabled": "Selection control border when disabled.",
    },
    "select": {
        "default": "Use for selected control fill. Checkbox tick background.",
        "hover": "Selected control fill on hover.",
        "pressed": "Selected control fill when pressed.",
        "disabled": "Selected control fill when disabled.",
    },
}


# ─── HELPER FUNCTIONS ───────────────────────────────────────────────────────

def is_token(obj):
    """Check if a dict is a token (has $type and $value)."""
    return isinstance(obj, dict) and "$type" in obj and "$value" in obj


def build_path(keys):
    """Build a dot-separated path from a list of keys."""
    return ".".join(keys)


def generate_interactive_description(variant, prop, state):
    """Generate description for interactive color tokens."""
    btn_type = BUTTON_TYPES.get(variant, variant.capitalize() + " button")

    if state == "default":
        defaults = INTERACTIVE_DEFAULT_DESCRIPTIONS.get(variant, {})
        if prop in defaults:
            return defaults[prop]
        return f"Use for {btn_type.lower()} {prop}."

    state_phrase = STATE_PHRASES.get(state, state)
    return f"{btn_type} {prop} {state_phrase}."


def generate_input_description(prop, state):
    """Generate description for input tokens."""
    if state == "default":
        defaults = SEMANTIC_INPUT_DEFAULTS.get(prop)
        if defaults:
            return defaults
        return f"Use for input {prop}."

    prop_label = {
        "fill": "Input background",
        "border": "Input border",
        "text": "Input text",
        "icon": "Input icon",
    }.get(prop, f"Input {prop}")

    state_phrase = STATE_PHRASES.get(state, state)
    if state in ("error", "success", "warning"):
        return f"{prop_label} for {state} state."
    return f"{prop_label} {state_phrase}."


def generate_feedback_description(feedback_type, prop):
    """Generate description for feedback tokens."""
    label = feedback_type.capitalize()
    prop_map = {
        "fill": f"Use for {feedback_type} backgrounds. Banners.",
        "border": f"Use for {feedback_type} borders. Banners.",
        "text": f"Use for {feedback_type} text. Messages.",
        "icon": f"Use for {feedback_type} icons. Banners.",
    }
    return prop_map.get(prop, f"Use for {feedback_type} {prop}.")


def generate_description_for_path(path_parts, file_context):
    """
    Given a list of path parts (keys from JSON root to the token),
    generate an appropriate description.

    file_context indicates which file the token is from.
    """
    path = build_path(path_parts)

    # ── CORE TOKENS (global/ files) ──────────────────────────────────
    if path_parts[0] == "core":
        # core.dimension.*
        if len(path_parts) >= 3 and path_parts[1] == "dimension":
            key = path_parts[2]
            return CORE_DIMENSION.get(key)

        # core.typography.fontFamily.*
        if len(path_parts) >= 4 and path_parts[1] == "typography":
            category = path_parts[2]
            key = path_parts[3]

            if category == "fontFamily":
                if key == "01":
                    return "Primary font family (Averta)."
                return f"Font family {key}."

            if category == "fontWeight":
                return CORE_FONT_WEIGHT.get(key)

            if category == "fontSize":
                return CORE_FONT_SIZE.get(key)

            if category == "lineHeight":
                return CORE_LINE_HEIGHT.get(key)

            if category == "letterSpacing":
                return CORE_LETTER_SPACING.get(key)

        # core.border.radius.* / core.border.width.*
        if len(path_parts) >= 4 and path_parts[1] == "border":
            category = path_parts[2]
            key = path_parts[3]

            if category == "radius":
                return CORE_BORDER_RADIUS.get(key)
            if category == "width":
                return CORE_BORDER_WIDTH.get(key)

        # core.color.modify.*
        if len(path_parts) >= 4 and path_parts[1] == "color" and path_parts[2] == "modify":
            key = path_parts[3]
            return CORE_MODIFY.get(key)

    # ── BRAND COLOR TOKENS (core/color.json or brand/color.json) ──────
    if path_parts[0] == "color" and file_context in ("core/color", "brand/color"):
        sub_path = build_path(path_parts[1:])
        return BRAND_COLORS.get(sub_path)

    # ── BRAND SHADOW TOKENS ──────────────────────────────────────────
    if path_parts[0] == "brand" and file_context in ("core/color", "brand/color"):
        if len(path_parts) >= 4 and path_parts[1] == "shadow" and path_parts[2] == "shadow":
            key = path_parts[3]
            shadow_map = {
                "zero": "No shadow. Zero elevation.",
                "100": "Small brand shadow. Subtle depth.",
                "200": "Medium brand shadow. Cards.",
                "300": "Large brand shadow. Modals.",
                "400": "Extra large brand shadow. Popovers.",
            }
            return shadow_map.get(key, f"Brand shadow {key}.")
        if len(path_parts) >= 3 and path_parts[1] == "typography":
            key = path_parts[-1]
            typo_map = {
                "numeric": "Numeric font variant. Tabular figures.",
                "underline": "Underline text decoration.",
            }
            return typo_map.get(key, f"Brand typography {key}.")

    # ── SEMANTIC COLOR TOKENS (semantic/colorLight.json) ─────────────
    if path_parts[0] == "color" and file_context == "semantic/colorLight":
        # color.interactive.{variant}.{prop}.{state} — full 5-part
        if len(path_parts) >= 5 and path_parts[1] == "interactive":
            variant = path_parts[2]
            prop = path_parts[3]
            state = path_parts[4]
            return generate_interactive_description(variant, prop, state)

        # color.interactive.{prop}.{state} — neutral interactive (no variant)
        if len(path_parts) == 4 and path_parts[1] == "interactive":
            prop = path_parts[2]
            state = path_parts[3]
            if state == "default":
                return f"Neutral interactive {prop}. Links and cards."
            state_phrase = STATE_PHRASES.get(state, state)
            return f"Neutral interactive {prop} {state_phrase}."

        # color.text.*
        if len(path_parts) >= 3 and path_parts[1] == "text":
            key = path_parts[2]
            desc = SEMANTIC_TEXT.get(key)
            if desc:
                return desc
            # Handle compound names like inverseSecondary
            if "inverse" in key.lower():
                return "Use for inverse secondary text."
            return f"Use for {key} text."

        # color.icon.* — mirrors text patterns
        if len(path_parts) >= 3 and path_parts[1] == "icon":
            key = path_parts[2]
            text_desc = SEMANTIC_TEXT.get(key)
            if text_desc:
                return text_desc.replace("text", "icons").replace("Text", "Icons")
            return f"Use for {key} icons."

        # color.input.{prop}.{state}
        if len(path_parts) >= 4 and path_parts[1] == "input":
            prop = path_parts[2]
            state = path_parts[3]
            return generate_input_description(prop, state)

        # color.feedback.{prop}.{type} — e.g. feedback.fill.error
        if len(path_parts) >= 4 and path_parts[1] == "feedback":
            prop = path_parts[2]
            feedback_type = path_parts[3]
            return generate_feedback_description(feedback_type, prop)

        # color.border.*
        if len(path_parts) >= 3 and path_parts[1] == "border":
            key = path_parts[2]
            desc = SEMANTIC_BORDER.get(key)
            if desc:
                return desc
            return f"Use for {key} borders."

        # color.surface.*
        if len(path_parts) >= 3 and path_parts[1] == "surface":
            key = path_parts[2]
            return SEMANTIC_SURFACE.get(key)

        # color.elevation.*
        if len(path_parts) >= 3 and path_parts[1] == "elevation":
            if path_parts[2] == "shadow" and len(path_parts) >= 4:
                key = path_parts[3]
                shadows = SEMANTIC_ELEVATION.get("shadow", {})
                return shadows.get(key)
            key = path_parts[2]
            desc = SEMANTIC_ELEVATION.get(key)
            if desc:
                return desc
            # Handle additional elevation tokens
            elevation_map = {
                "canvas": "Canvas background. Base layer.",
                "undercanvas": "Under-canvas background. Behind content.",
                "relative1": "Relative elevation. Subtle lift.",
                "level1": "Level 1 elevation. Cards.",
                "level2": "Level 2 elevation. Raised cards.",
                "level3": "Level 3 elevation. Dropdowns.",
                "level4": "Level 4 elevation. Modals.",
                "level5": "Level 5 elevation. Top layer.",
                "inverse": "Inverse elevation. Dark surfaces.",
                "accentA": "Accent elevation A. Branded surface.",
                "accentB": "Accent elevation B. Branded surface.",
            }
            return elevation_map.get(key, f"Elevation {key}.")

        # color.disabled.*
        if len(path_parts) >= 3 and path_parts[1] == "disabled":
            key = path_parts[2]
            labels = {
                "a": "Disabled fill. Backgrounds and containers.",
                "b": "Disabled stroke. Borders, text, and icons.",
                "c": "Disabled checked fill. Selected controls.",
            }
            return labels.get(key)

        # color.focus.*
        if len(path_parts) >= 3 and path_parts[1] == "focus":
            key = path_parts[2]
            if key == "default":
                return "Focus ring color. Accessibility."
            return f"Focus {key} color."

        # color.selected.control.{prop}.{state} — selectionControl tokens
        if (len(path_parts) >= 5 and path_parts[1] == "selected"
                and path_parts[2] == "control"):
            prop = path_parts[3]
            state = path_parts[4]
            ctrl_prop = SELECTION_CONTROL.get(prop, {})
            if isinstance(ctrl_prop, dict):
                desc = ctrl_prop.get(state)
                if desc:
                    return desc

        # color.selected.{variant}.{prop}.{state} — e.g. selected.primary.fill.default
        if len(path_parts) >= 3 and path_parts[1] == "selected":
            remaining = path_parts[2:]
            # 3-part: variant.prop.state
            if len(remaining) == 3:
                variant, prop, state = remaining
                variant_label = {"primary": "primary", "secondary": "secondary", "tertiary": "tertiary"}.get(variant, variant)
                if state == "default":
                    return f"Use for {variant_label} selected {prop}."
                state_phrase = STATE_PHRASES.get(state, state)
                return f"{variant_label.capitalize()} selected {prop} {state_phrase}."
            # 2-part: prop.state
            if len(remaining) == 2:
                prop, state = remaining
                if state == "default":
                    return f"Use for selected {prop}."
                state_phrase = STATE_PHRASES.get(state, state)
                return f"Selected {prop} {state_phrase}."
            # 1-part
            if len(remaining) == 1:
                prop = remaining[0]
                return f"Use for selected {prop}."

        # color.active.*
        if len(path_parts) >= 3 and path_parts[1] == "active":
            remaining = path_parts[2:]
            if len(remaining) == 1:
                prop = remaining[0]
                return f"Use for active state {prop}."
            if len(remaining) == 2:
                prop, state = remaining
                if state == "default":
                    return f"Use for active state {prop}."
                return f"Active {prop} {state}."

        # color.status.*
        if len(path_parts) >= 3 and path_parts[1] == "status":
            remaining = path_parts[2:]
            if len(remaining) >= 2:
                status_name = remaining[0]
                prop = remaining[1]
                return f"Use for {status_name} status {prop}."
            return f"Use for status {remaining[0]}."

    # ── TOP-LEVEL ELEVATION (shadow composites in colorLight) ─────
    if path_parts[0] == "elevation" and file_context == "semantic/colorLight":
        key = path_parts[1] if len(path_parts) >= 2 else ""
        elevation_shadow_map = {
            "elevationLevel1": "Level 1 shadow. Cards and tiles.",
            "elevationLevel2": "Level 2 shadow. Raised elements.",
            "elevationLevel3": "Level 3 shadow. Dropdowns and menus.",
            "elevationLevel4": "Level 4 shadow. Modals and dialogs.",
        }
        return elevation_shadow_map.get(key, f"Elevation shadow {key}.")

    # ── SEMANTIC TYPOGRAPHY ──────────────────────────────────────────
    if path_parts[0] == "typography" and file_context == "semantic/typography":
        sub_path = build_path(path_parts[1:])
        return SEMANTIC_TYPOGRAPHY.get(sub_path)

    # ── SEMANTIC BORDER RADIUS ───────────────────────────────────────
    if path_parts[0] == "borderRadius" and file_context == "semantic/borderRadius":
        sub_path = build_path(path_parts[1:])
        return SEMANTIC_BORDER_RADIUS.get(sub_path)

    # ── SEMANTIC BORDER (interactive widths) ─────────────────────────
    if path_parts[0] == "border" and file_context == "semantic/border":
        if len(path_parts) >= 3 and path_parts[1] == "interactive":
            key = path_parts[2]
            return SEMANTIC_INTERACTIVE_BORDER.get(key)

    # ── COMPONENT TOKENS ─────────────────────────────────────────────
    if file_context.startswith("component/"):
        # stepper.color.container.{prop}
        if (path_parts[0] == "stepper" and len(path_parts) >= 4
                and path_parts[1] == "color" and path_parts[2] == "container"):
            prop = path_parts[3]
            return STEPPER_CONTAINER.get(prop)

        # stepper.color.counter.{prop}.{state}
        if (path_parts[0] == "stepper" and len(path_parts) >= 5
                and path_parts[1] == "color" and path_parts[2] == "counter"):
            prop = path_parts[3]
            state = path_parts[4]
            if state == "default":
                return STEPPER_COUNTER_DEFAULTS.get(prop)
            prop_label = {
                "fill": "Counter display background",
                "border": "Counter display border",
                "text": "Counter display text",
            }.get(prop, f"Counter {prop}")
            state_phrase = STATE_PHRASES.get(state, state)
            return f"{prop_label} {state_phrase}."

        # stepper.color.interactive.{variant}.{prop}.{state}
        if (path_parts[0] == "stepper" and len(path_parts) >= 6
                and path_parts[1] == "color" and path_parts[2] == "interactive"):
            variant = path_parts[3]  # primary/secondary
            prop = path_parts[4]     # fill/icon/border
            state = path_parts[5]
            variant_label = variant.capitalize()
            if state == "default":
                if prop == "icon":
                    return f"Icon on {variant} stepper button."
                return f"{variant_label} stepper button {prop}."
            if prop == "icon":
                state_phrase = STATE_PHRASES.get(state, state)
                return f"Icon on {variant} stepper button {state_phrase}."
            if state == "focus":
                return f"{variant_label} stepper button focus ring."
            state_phrase = STATE_PHRASES.get(state, state)
            return f"{variant_label} stepper button {prop} {state_phrase}."

        # badge.spacing.*
        if path_parts[0] == "badge" and len(path_parts) >= 3:
            prop = path_parts[-1]
            badge_descs = {
                "blockPadding": "Vertical padding for badge.",
                "inlinePadding": "Horizontal padding for badge.",
                "gap": "Gap between icon and label in badge.",
                "minHeight": "Minimum height for badge.",
            }
            return badge_descs.get(prop)

        # selectionControl.spacing.*
        if path_parts[0] == "selectionControl" and len(path_parts) >= 3:
            prop = path_parts[-1]
            sc_descs = {
                "gap": "Gap between control and label text.",
                "validationGap": "Gap between control row and validation message.",
                "errorGap": "Gap between error icon and error text.",
            }
            return sc_descs.get(prop)

        # icon.size.*
        if path_parts[0] == "icon" and len(path_parts) >= 3:
            size_key = path_parts[2]
            size_label = SIZE_LABELS.get(size_key, size_key)
            cap_label = size_label[0].upper() + size_label[1:] if size_label else size_label
            return f"{cap_label} icon size."

        # layout.spacing.*
        if path_parts[0] == "layout" and len(path_parts) >= 3:
            key = path_parts[2]
            layout_descs = {
                "cardGap": "Gap between card elements.",
                "interactiveGap": "Gap between interactive elements.",
                "contentToButton": "Gap from content to button.",
                "formGap": "Gap between form field elements.",
            }
            return layout_descs.get(key)

        # button.spacing.{size}.{prop}
        if path_parts[0] == "button" and len(path_parts) >= 4:
            size_key = path_parts[2]
            prop = path_parts[3]
            size_label = SIZE_LABELS.get(size_key, size_key)

            if prop == "blockPadding":
                return f"Block padding for {size_label} buttons."
            elif prop == "inlinePadding":
                return f"Inline padding for {size_label} buttons."
            elif prop == "gap":
                return f"Gap between icon and text. {size_label.capitalize()} buttons."

    return None


def process_token_tree(data, path_parts, file_context, stats, overrides=None):
    """
    Recursively traverse the token tree and add $description fields.
    Modifies data in place.

    Args:
        data:        Current node in the token tree.
        path_parts:  List of key segments from the root to this node.
        file_context: File path context string used by pattern matchers.
        stats:       Mutable dict accumulating run statistics.
        overrides:   Dict of token_path -> override entry loaded from overrides.json.
                     When a token path has an override its description is used
                     instead of the pattern-generated one.
    """
    if overrides is None:
        overrides = {}

    if not isinstance(data, dict):
        return

    # Skip metadata keys
    skip_keys = {"$type", "$value", "$description", "$extensions"}

    if is_token(data):
        token_path = build_path(path_parts)

        # User override takes priority over pattern-generated descriptions.
        if token_path in overrides:
            data["$description"] = overrides[token_path]["description"]
            stats["from_overrides"] += 1
            return

        # This is a leaf token — generate description
        desc = generate_description_for_path(path_parts, file_context)
        existing = data.get("$description")
        if desc:
            if existing:
                # Never overwrite an existing description unless --force is set.
                # Existing descriptions may be intentionally long or customised.
                if stats.get("force"):
                    data["$description"] = desc
                    stats["updated"] += 1
                else:
                    stats["kept_existing"] += 1
            else:
                data["$description"] = desc
                stats["added"] += 1
        else:
            stats["no_match"] += 1
            if "$description" not in data:
                stats["missing_paths"].append(build_path(path_parts))
        return

    for key in data:
        if key in skip_keys:
            continue
        child = data[key]
        if isinstance(child, dict):
            process_token_tree(child, path_parts + [key], file_context, stats, overrides)


def determine_file_context(file_path):
    """Determine the file context from the file path for pattern matching."""
    path = Path(file_path)
    parts = path.parts

    # Find 'tokens' in path and build context from there
    try:
        tokens_idx = parts.index("tokens")
    except ValueError:
        return "unknown"

    remaining = parts[tokens_idx + 1:]
    # Remove .json extension from last part
    last = remaining[-1].replace(".json", "")
    remaining = list(remaining[:-1]) + [last]
    return "/".join(remaining)


def process_file(file_path, stats, overrides=None, dry_run=False):
    """Process a single token file."""
    if overrides is None:
        overrides = {}

    file_context = determine_file_context(file_path)
    print(f"\n{'='*60}")
    print(f"Processing: {file_path}")
    print(f"Context: {file_context}")

    with open(file_path, "r") as f:
        data = json.load(f)

    file_stats = {
        "added": 0,
        "updated": 0,
        "kept_existing": 0,
        "no_match": 0,
        "from_overrides": 0,
        "missing_paths": [],
        # Propagate --force flag so process_token_tree can check it.
        "force": stats.get("force", False),
    }

    process_token_tree(data, [], file_context, file_stats, overrides)

    # Write back (skip in dry-run mode)
    if not dry_run:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    print(f"  Added: {file_stats['added']}")
    print(f"  Overwritten (--force): {file_stats['updated']}")
    print(f"  Kept existing: {file_stats['kept_existing']}")
    print(f"  From overrides: {file_stats['from_overrides']}")
    print(f"  No pattern match: {file_stats['no_match']}")
    if file_stats["missing_paths"]:
        print(f"  Unmatched paths:")
        for p in file_stats["missing_paths"]:
            print(f"    - {p}")

    # Accumulate into global stats
    for key in ("added", "updated", "kept_existing", "no_match", "from_overrides"):
        stats[key] += file_stats[key]
    stats["missing_paths"].extend(file_stats["missing_paths"])


def main():
    # Parse flags
    force = "--force" in sys.argv
    dry_run = "--dry-run" in sys.argv

    tokens_dir = Path(__file__).parent.parent.parent / "tokens"
    if not tokens_dir.exists():
        print(f"Error: tokens directory not found at {tokens_dir}")
        sys.exit(1)

    print(f"Token directory: {tokens_dir}")
    if dry_run:
        print("Mode: --dry-run — preview only, no files will be modified")
    elif force:
        print("Mode: --force — existing descriptions will be overwritten")
    else:
        print("Mode: safe — existing descriptions will be preserved (use --force to overwrite)")

    # Load user-corrected overrides so they take priority over generated descriptions.
    overrides = load_overrides()
    if overrides:
        print(f"Overrides loaded: {len(overrides)} token(s) will use user-corrected descriptions")

    # Find all JSON files (excluding $ prefixed metadata files)
    token_files = []
    for root, dirs, files in os.walk(tokens_dir):
        for f in sorted(files):
            if f.endswith(".json") and not f.startswith("$"):
                token_files.append(os.path.join(root, f))

    print(f"Found {len(token_files)} token files")

    # Count tokens and pre-existing coverage before making any changes.
    tokens_before = 0
    covered_before = 0

    def _count_tokens(node):
        nonlocal tokens_before, covered_before
        if not isinstance(node, dict):
            return
        if "$type" in node and "$value" in node:
            tokens_before += 1
            if node.get("$description"):
                covered_before += 1
            return
        for k, v in node.items():
            if k not in {"$type", "$value", "$description", "$extensions"}:
                _count_tokens(v)

    for fp in token_files:
        with open(fp, "r") as fh:
            _count_tokens(json.load(fh))

    coverage_before_pct = (covered_before / tokens_before * 100) if tokens_before > 0 else 0.0

    stats = {
        "added": 0,
        "updated": 0,
        "kept_existing": 0,
        "no_match": 0,
        "from_overrides": 0,
        "missing_paths": [],
        "force": force,
    }

    for fp in token_files:
        process_file(fp, stats, overrides, dry_run=dry_run)

    print(f"\n{'='*60}")
    if dry_run:
        print("DRY RUN SUMMARY (no files modified)")
    else:
        print("SUMMARY")
    print(f"{'='*60}")
    print(f"Descriptions added:    {stats['added']}")
    print(f"Descriptions overwritten (--force): {stats['updated']}")
    print(f"Kept existing:         {stats['kept_existing']}")
    print(f"From overrides:        {stats['from_overrides']}")
    print(f"No pattern match:      {stats['no_match']}")
    total = (
        stats["added"]
        + stats["updated"]
        + stats["kept_existing"]
        + stats["no_match"]
        + stats["from_overrides"]
    )
    covered = stats["added"] + stats["updated"] + stats["kept_existing"] + stats["from_overrides"]
    pct = (covered / total * 100) if total > 0 else 0
    print(f"Coverage:              {covered}/{total} ({pct:.1f}%)")

    if stats["missing_paths"]:
        print(f"\nUnmatched token paths ({len(stats['missing_paths'])}):")
        for p in stats["missing_paths"]:
            print(f"  - {p}")

    # Save a run manifest so quality-dashboard.py can track progress over time.
    # Skip in dry-run mode since no actual changes were made.
    if dry_run:
        return

    save_run_manifest(
        files_processed=len(token_files),
        tokens_total=total,
        descriptions_added=stats["added"],
        descriptions_updated=stats["updated"],
        descriptions_unchanged=stats["kept_existing"],
        coverage_before_pct=coverage_before_pct,
        coverage_after_pct=pct,
        validation_errors=0,
        validation_warnings=len(stats["missing_paths"]),
    )


if __name__ == "__main__":
    main()
