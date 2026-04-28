# Description Templates Reference

This document provides ready-to-use description templates for all token types. Use these patterns to ensure consistency across your design token library.

---

## Core Principles

1. **Concise**: 20-50 characters target length
2. **Platform-agnostic**: Never mention units (px, pt, rem) or platforms
3. **Purpose-driven**: Focus on "what" and "where", not "how"
4. **Component-specific**: Mention actual Figma components when applicable

---

## Tier 1: Core Token Templates (global/ folder)

### Dimension Tokens

**Pattern**: `"{Size} spacing."`

```python
CORE_DIMENSION_PATTERNS = {
    "dimension.zero": "Zero spacing. Removes all space.",
    "dimension.50": "Minimal spacing. Use for tight gaps.",
    "dimension.100": "Base spacing unit. Foundation for scale.",
    "dimension.150": "1.5x base spacing.",
    "dimension.200": "Small spacing.",
    "dimension.250": "Small-medium spacing.",
    "dimension.300": "Medium spacing.",
    "dimension.350": "Medium spacing.",
    "dimension.400": "Medium spacing.",
    "dimension.450": "Medium-large spacing.",
    "dimension.500": "Large spacing.",
    "dimension.550": "Large spacing.",
    "dimension.600": "Extra large spacing.",
    "dimension.650": "Extra large spacing.",
    "dimension.700": "2X large spacing.",
    "dimension.750": "2X large spacing.",
    "dimension.800": "2X large spacing.",
    "dimension.850": "2X large spacing.",
    "dimension.900": "3X large spacing.",
    "dimension.1000": "3X large spacing.",
    "dimension.1100": "3X large spacing.",
    "dimension.1200": "3X large spacing.",
    "dimension.1300": "4X large spacing.",
    "dimension.1400": "4X large spacing.",
    "dimension.1500": "4X large spacing.",
    "dimension.1600": "5X large spacing.",
    "dimension.1700": "5X large spacing.",
    "dimension.1800": "5X large spacing.",
    "dimension.1900": "6X large spacing.",
    "dimension.2000": "6X large spacing."
}
```

---

### Typography Tokens

**Font Family Pattern**: `"{Family} font family."`
```python
"fontFamily.01": "Primary font family (Averta)."
"fontFamily.{key}": "{Name} font family."
```

**Font Weight Pattern**: `"{Weight} weight ({value}). Use for {purpose}."`
```python
CORE_FONT_WEIGHT_PATTERNS = {
    "fontWeight.light": "Light weight (300). Use for subtle text.",
    "fontWeight.regular": "Regular weight (400). Default text.",
    "fontWeight.semibold": "Semibold weight (600). Use for emphasis.",
    "fontWeight.bold": "Bold weight (700). Use for emphasis.",
    "fontWeight.black": "Black weight (900). Use for headings."
}
```

**Font Size Pattern**:
- Base: `"Base font size. Foundation for scale."`
- Others: `"Font size. Scale: {multiplier}x."`

```python
"fontSize.100": "Base font size. Foundation for scale."
"fontSize.200": "Font size. Scale: 1.13x."
"fontSize.300": "Font size. Scale: 1.25x."
# etc. — scale runs from fontSize.25 through fontSize.900
```

**Line Height Pattern**:
- Base: `"Base line height. Foundation for scale."`
- Others: `"Line height. Scale: {multiplier}x."`
- Scale runs from `lineHeight.25` through `lineHeight.800`, plus `lineHeight.full`

**Letter Spacing Pattern**: `"Letter spacing."` or `"Negative letter spacing."`
```python
"letterSpacing.100": "0% letter spacing."
"letterSpacing.300": "Letter spacing."
"letterSpacing.neg100": "Negative letter spacing. Tighter text."
"letterSpacing.neg200": "Negative letter spacing. Tighter text."
"letterSpacing.neg300": "Negative letter spacing. Tightest text."
```

---

### Color Tokens (Brand tier — core/ folder)

**Brand colors**: Keep existing descriptive text (usually already detailed)

Note: Brand color tokens have root key `color` (not `core`), so paths are `color.brand.*`, `color.accent.*`, etc.

```python
BRAND_COLOR_PATTERNS = {
    "color.brand.01": "Primary brand color. Use for main actions, links, or in any element that highlights the brand.",
    "color.brand.01-inverse": "Inverse primary brand color. Lighter variant for use on dark backgrounds.",
    "color.brand.02": "Secondary brand color. Also used as background for headings and titles in areas which represent brand's visual language.",
    "color.brand.03": "Alternate brand color. Also used as background for pages, or text on dark backgrounds."
}
```

---

### Modify Tokens

**Pattern**: `"{value} modifier. For lighten/darken/alpha."`

Note: Modify tokens are nested under `core.color.modify.*` in `global/modify.json`.

```python
CORE_MODIFY_PATTERNS = {
    "color.modify.zero": "Zero modifier. No modification.",
    "color.modify.50": "0.05 modifier. For lighten/darken/alpha.",
    "color.modify.100": "0.1 modifier. For lighten/darken/alpha.",
    "color.modify.150": "0.15 modifier. For lighten/darken/alpha.",
    "color.modify.200": "0.2 modifier. For lighten/darken/alpha.",
    "color.modify.300": "0.3 modifier. For lighten/darken/alpha.",
    "color.modify.400": "0.4 modifier. For lighten/darken/alpha.",
    "color.modify.500": "0.5 modifier. For lighten/darken/alpha.",
    "color.modify.600": "0.6 modifier. For lighten/darken/alpha.",
    "color.modify.700": "0.7 modifier. For lighten/darken/alpha.",
    "color.modify.800": "0.8 modifier. For lighten/darken/alpha.",
    "color.modify.900": "0.9 modifier. For lighten/darken/alpha.",
    "color.modify.950": "0.95 modifier. For lighten/darken/alpha.",
    "color.modify.1000": "1.0 modifier. For lighten/darken/alpha."
    # Also includes special steps: 250, 350, 390, 450, 550, 650, 750, 840, 850, 920, 960
}
```

---

### Border Tokens

**Border Radius Pattern**: `"{Size} corner radius."` or `"Full corner radius. Pill shape."`

```python
CORE_BORDER_RADIUS_PATTERNS = {
    "radius.xSmall": "Extra small corner radius.",
    "radius.small": "Small corner radius.",
    "radius.medium": "Medium corner radius.",
    "radius.large": "Large corner radius.",
    "radius.xLarge": "Extra large corner radius.",
    "radius.xxLarge": "2X large corner radius.",
    "radius.full": "Full corner radius. Pill shape."
}
```

**Border Width Pattern**: `"{Size} border width."`

```python
CORE_BORDER_WIDTH_PATTERNS = {
    "width.xSmall": "Extra small border width.",
    "width.small": "Small border width.",
    "width.medium": "Medium border width.",
    "width.large": "Large border width.",
    "width.xLarge": "Extra large border width."
}
```

---

## Tier 2: Semantic Token Templates

### Interactive Tokens

**Primary (Solid Buttons)**:

```python
SEMANTIC_INTERACTIVE_PRIMARY = {
    # Default states - provide context
    "interactive.primary.fill.default": "Use for solid buttons. Primary CTAs.",
    "interactive.primary.text.default": "Use for solid button text.",
    "interactive.primary.icon.default": "Use for solid button icons.",
    "interactive.primary.border.default": "Use for solid button borders.",

    # State variants - reference component + property + state
    "interactive.primary.fill.hover": "Solid button fill on hover.",
    "interactive.primary.fill.pressed": "Solid button fill when pressed.",
    "interactive.primary.fill.disabled": "Solid button fill when disabled.",
    "interactive.primary.text.hover": "Solid button text on hover.",
    "interactive.primary.text.pressed": "Solid button text when pressed.",
    "interactive.primary.text.disabled": "Solid button text when disabled.",
    "interactive.primary.icon.hover": "Solid button icon on hover.",
    "interactive.primary.icon.pressed": "Solid button icon when pressed.",
    "interactive.primary.icon.disabled": "Solid button icon when disabled.",
    "interactive.primary.border.hover": "Solid button border on hover.",
    "interactive.primary.border.pressed": "Solid button border when pressed.",
    "interactive.primary.border.disabled": "Solid button border when disabled."
}
```

**Secondary (Outline Buttons)**:

```python
SEMANTIC_INTERACTIVE_SECONDARY = {
    "interactive.secondary.fill.default": "Use for outline buttons. Secondary actions.",
    "interactive.secondary.text.default": "Use for outline button text.",
    "interactive.secondary.icon.default": "Use for outline button icons.",
    "interactive.secondary.border.default": "Use for outline button borders.",

    "interactive.secondary.fill.hover": "Outline button fill on hover.",
    "interactive.secondary.fill.pressed": "Outline button fill when pressed.",
    "interactive.secondary.fill.disabled": "Outline button fill when disabled.",
    "interactive.secondary.text.hover": "Outline button text on hover.",
    "interactive.secondary.text.pressed": "Outline button text when pressed.",
    "interactive.secondary.text.disabled": "Outline button text when disabled.",
    "interactive.secondary.icon.hover": "Outline button icon on hover.",
    "interactive.secondary.icon.pressed": "Outline button icon when pressed.",
    "interactive.secondary.icon.disabled": "Outline button icon when disabled.",
    "interactive.secondary.border.hover": "Outline button border on hover.",
    "interactive.secondary.border.pressed": "Outline button border when pressed.",
    "interactive.secondary.border.disabled": "Outline button border when disabled."
}
```

**Ghost Buttons**:

```python
SEMANTIC_INTERACTIVE_GHOST = {
    "interactive.ghost.fill.default": "Use for ghost buttons. Minimal actions.",
    "interactive.ghost.text.default": "Use for ghost button text.",
    "interactive.ghost.icon.default": "Use for ghost button icons.",

    "interactive.ghost.fill.hover": "Ghost button fill on hover.",
    "interactive.ghost.fill.pressed": "Ghost button fill when pressed.",
    "interactive.ghost.text.hover": "Ghost button text on hover.",
    "interactive.ghost.text.pressed": "Ghost button text when pressed.",
    "interactive.ghost.icon.hover": "Ghost button icon on hover.",
    "interactive.ghost.icon.pressed": "Ghost button icon when pressed."
}
```

**Tertiary Buttons** (low-emphasis with border, distinct from ghost):

```python
SEMANTIC_INTERACTIVE_TERTIARY = {
    "interactive.tertiary.fill.default": "Use for tertiary buttons. Low emphasis.",
    "interactive.tertiary.text.default": "Use for tertiary button text.",
    "interactive.tertiary.icon.default": "Use for tertiary button icons.",

    "interactive.tertiary.fill.hover": "Tertiary button fill on hover.",
    "interactive.tertiary.fill.pressed": "Tertiary button fill when pressed.",
    "interactive.tertiary.text.hover": "Tertiary button text on hover.",
    "interactive.tertiary.text.pressed": "Tertiary button text when pressed.",
    "interactive.tertiary.icon.hover": "Tertiary button icon on hover.",
    "interactive.tertiary.icon.pressed": "Tertiary button icon when pressed."
}
```

**Pattern Template for All Interactive Types**:
```
Default state: "Use for {button_type}. {Context}."
Hover state: "{Button_type} {property} on hover."
Pressed state: "{Button_type} {property} when pressed."
Disabled state: "{Button_type} {property} when disabled."
Focus state: "{Button_type} {property} on focus."
```

---

### Text Tokens

**Pattern**: `"Use for {hierarchy/context} text. {Where}."`

```python
SEMANTIC_TEXT = {
    # Hierarchy
    "text.primary": "Use for primary text. Main content.",
    "text.secondary": "Use for secondary text. Helper text.",
    "text.tertiary": "Use for tertiary text. Subtle content.",
    "text.disabled": "Use for disabled text. Inactive elements.",

    # Context-specific
    "text.placeholder": "Use for placeholder text. Inputs.",
    "text.inverse": "Use for text on dark backgrounds.",
    "text.on-accent": "Use for text on colored backgrounds.",

    # Feedback
    "text.error": "Use for error messages. Validation.",
    "text.success": "Use for success messages. Confirmations.",
    "text.warning": "Use for warning messages. Cautions.",
    "text.info": "Use for info messages. Tips.",
    "text.brand": "Use for brand-colored text. Highlights."
}
```

---

### Input Tokens

**Pattern**: `"Use for input {property}. {Component}."` or `"Input {property} {state}."`

```python
SEMANTIC_INPUT = {
    # Fill states
    "input.fill.default": "Use for input backgrounds. Text fields.",
    "input.fill.hover": "Input background on hover.",
    "input.fill.focus": "Input background on focus.",
    "input.fill.active": "Input background when active.",
    "input.fill.disabled": "Input background when disabled.",
    "input.fill.readonly": "Input background when read-only.",

    # Border states
    "input.border.default": "Use for input borders. Text fields.",
    "input.border.hover": "Input border on hover.",
    "input.border.focus": "Input border on focus.",
    "input.border.active": "Input border when active.",
    "input.border.disabled": "Input border when disabled.",
    "input.border.error": "Input border for errors. Invalid state.",
    "input.border.success": "Input border for valid state.",

    # Icon states
    "input.icon.default": "Use for input icons. Search/clear.",
    "input.icon.hover": "Input icon on hover.",
    "input.icon.active": "Input icon when active.",

    # Text states
    "input.text.default": "Use for input text.",
    "input.text.hover": "Input text on hover.",
    "input.text.active": "Input text when active.",
    "input.text.placeholder": "Use for input placeholder text."
}
```

---

### Feedback Tokens

**Pattern**: `"Use for {state} {element}. {Component}."`

```python
SEMANTIC_FEEDBACK = {
    # Error
    "feedback.error.fill": "Use for error backgrounds. Banners.",
    "feedback.error.fill-subtle": "Use for subtle error backgrounds.",
    "feedback.error.border": "Use for error borders. Banners.",
    "feedback.error.text": "Use for error text. Validation messages.",
    "feedback.error.icon": "Use for error icons. Banners/inputs.",

    # Success
    "feedback.success.fill": "Use for success backgrounds. Banners.",
    "feedback.success.fill-subtle": "Use for subtle success backgrounds.",
    "feedback.success.border": "Use for success borders. Banners.",
    "feedback.success.text": "Use for success text. Confirmations.",
    "feedback.success.icon": "Use for success icons. Banners.",

    # Warning
    "feedback.warning.fill": "Use for warning backgrounds. Banners.",
    "feedback.warning.fill-subtle": "Use for subtle warning backgrounds.",
    "feedback.warning.border": "Use for warning borders. Banners.",
    "feedback.warning.text": "Use for warning text. Cautions.",
    "feedback.warning.icon": "Use for warning icons. Banners.",

    # Info
    "feedback.info.fill": "Use for info backgrounds. Banners.",
    "feedback.info.fill-subtle": "Use for subtle info backgrounds.",
    "feedback.info.border": "Use for info borders. Banners.",
    "feedback.info.text": "Use for info text. Tips.",
    "feedback.info.icon": "Use for info icons. Banners."
}
```

---

### Border Tokens

**Pattern**: `"Use for {quality} borders. {Context}."`

```python
SEMANTIC_BORDER = {
    # States
    "border.default": "Use for standard borders. Default state.",
    "border.subtle": "Use for subtle borders. Low contrast.",
    "border.strong": "Use for strong borders. High contrast.",
    "border.hover": "Border color on hover.",
    "border.focus": "Border color on focus. Accessibility.",
    "border.disabled": "Border color when disabled.",

    # Context-specific
    "border.error": "Use for error borders. Invalid.",
    "border.success": "Use for success borders. Valid.",
    "border.warning": "Use for warning borders. Cautions.",
    "border.brand": "Use for brand-colored borders.",
    "border.elevation": "Use for elevated surface borders. Cards.",
    "border.primary": "Use for primary borders. Cards.",
    "border.secondary": "Use for secondary borders. Medium emphasis.",
    "border.inverse": "Use for borders on dark backgrounds.",
    "border.on-accent": "Use for borders on accent backgrounds."
}
```

---

### Selection Control Tokens

**Pattern**: `"Use for selection control {property}."` or `"Selection control {property} {state}."`

```python
SEMANTIC_SELECTION_CONTROL = {
    # Fill states
    "selected.control.fill.default": "Use for selection control background.",
    "selected.control.fill.hover": "Selection control background on hover.",
    "selected.control.fill.pressed": "Selection control background when pressed.",
    "selected.control.fill.disabled": "Selection control background when disabled.",

    # Border states
    "selected.control.border.default": "Use for selection control border.",
    "selected.control.border.hover": "Selection control border on hover.",
    "selected.control.border.pressed": "Selection control border when pressed.",
    "selected.control.border.error": "Selection control border for error state.",
    "selected.control.border.focus": "Selection control focus ring.",
    "selected.control.border.disabled": "Selection control border when disabled.",

    # Select states (checked/on fill)
    "selected.control.select.default": "Use for selected control fill. Checkbox tick background.",
    "selected.control.select.hover": "Selected control fill on hover.",
    "selected.control.select.pressed": "Selected control fill when pressed.",
    "selected.control.select.disabled": "Selected control fill when disabled."
}
```

Note: `color.disabled.a` = backgrounds/fills (lightest), `color.disabled.b` = borders/text/icons (medium), `color.disabled.c` = selected/checked fills (heaviest). The select.disabled uses `disabled.c` deliberately for contrast against the `disabled.a` fill background.

---

### Disabled Tokens

**Pattern**: `"Disabled {role}. {Usage context}."`

```python
SEMANTIC_DISABLED = {
    "disabled.a": "Disabled fill. Backgrounds and containers.",
    "disabled.b": "Disabled stroke. Borders, text, and icons.",
    "disabled.c": "Disabled checked fill. Selected controls."
}
```

---

### Status Tokens

**Pattern**: `"Use for {status} badges. {Optional context}."`

```python
SEMANTIC_STATUS = {
    "status.draft.fill": "Use for draft badges. Status indicators.",
    "status.draft.text": "Draft badge text.",
    "status.published.fill": "Use for published badges. Status indicators.",
    "status.published.text": "Published badge text.",
    "status.archived.fill": "Use for archived badges. Status indicators.",
    "status.archived.text": "Archived badge text."
}
```

---

### Surface & Elevation Tokens

```python
SEMANTIC_SURFACE = {
    "surface.primary": "Brand surface. Use for branded container backgrounds.",
    "surface.light": "Light surface. Use for card or container backgrounds.",
    "surface.neutralLighter": "Lightest neutral surface background.",
    "surface.neutralLight": "Light neutral surface background.",
    "surface.neutralDark": "Dark neutral surface background.",
    "surface.neutralDarker": "Darker neutral surface background.",
    "surface.neutralDarkest": "Darkest neutral surface background.",
    "surface.inverse": "Inverse surface. Use for dark container backgrounds."
}

SEMANTIC_ELEVATION = {
    "elevation.level-1": "Use for card surfaces. Level 1 depth.",
    "elevation.level-2": "Use for elevated cards. Level 2 depth.",
    "elevation.level-3": "Use for dropdowns. Level 3 depth.",
    "elevation.level-4": "Use for modals. Level 4 depth.",
    "elevation.level-5": "Use for top layer. Level 5 depth.",

    "elevation.shadow.xs": "Use for subtle shadows. Slight depth.",
    "elevation.shadow.s": "Use for small shadows. Cards.",
    "elevation.shadow.m": "Use for medium shadows. Dialogs.",
    "elevation.shadow.l": "Use for large shadows. Modals.",
    "elevation.shadow.xl": "Use for extra large shadows. Popovers.",

    "elevation.overlay": "Use for modal overlays. Backgrounds.",
    "elevation.base": "Use for elevation base. Internal mixin."
}
```

---

### Typography Tokens

**Pattern**: `"Use for {element type}. Applied to {context}."`

```python
SEMANTIC_TYPOGRAPHY = {
    # Heading
    "typography.heading.xl": "Use for page titles. Applied to H1.",
    "typography.heading.l": "Use for section titles. Applied to H2.",
    "typography.heading.m": "Use for subsection titles. Applied to H3.",
    "typography.heading.s": "Use for minor headings. Applied to H4.",
    "typography.heading.xs": "Use for small headings. Applied to H5/H6.",

    # Title
    "typography.title.l": "Use for large UI titles. Dialogs/panels.",
    "typography.title.m": "Use for medium UI titles. Cards/sections.",
    "typography.title.s": "Use for small UI titles. Components.",

    # Label
    "typography.label.l": "Use for large size action labels.",
    "typography.label.m": "Use for medium size action labels.",
    "typography.label.s": "Use for small size action labels.",
    "typography.label.xs": "Use for tiny labels. Dense layouts.",

    # Body
    "typography.body.l": "Use for large body text. Feature content.",
    "typography.body.m": "Use for standard body text. Main content.",
    "typography.body.s": "Use for small body text. Captions.",
    "typography.body.xs": "Use for tiny text. Legal/metadata.",

    # Data
    "typography.data.l": "Use for large data display. Metrics.",
    "typography.data.m": "Use for medium data display. Tables.",
    "typography.data.s": "Use for small data display. Dense data."
}
```

---

### Border Radius Tokens

**Pattern**: `"Use for {component} corners."`

```python
SEMANTIC_BORDER_RADIUS = {
    # Interactive
    "borderRadius.interactive.small": "Use for small interactive corners.",
    "borderRadius.interactive.medium": "Use for medium button corners.",
    "borderRadius.interactive.large": "Use for large button corners.",
    "borderRadius.interactive.full": "Use for pill button corners.",

    # Input
    "borderRadius.input.small": "Use for small input corners.",
    "borderRadius.input.medium": "Use for medium input corners.",
    "borderRadius.input.large": "Use for large input corners.",
    "borderRadius.input.full": "Use for pill input corners.",

    # Container
    "borderRadius.container.none": "Use for sharp container corners.",
    "borderRadius.container.small": "Use for small container corners.",
    "borderRadius.container.medium": "Use for medium container corners. Cards/banners.",
    "borderRadius.container.large": "Use for large container corners.",

    # Popover
    "borderRadius.popover.none": "Use for sharp popover corners.",
    "borderRadius.popover.small": "Use for small popover corners.",
    "borderRadius.popover.medium": "Use for medium popover corners.",
    "borderRadius.popover.large": "Use for large popover corners."
}
```

---

## Tier 3: Component Token Templates

### Stepper Component Tokens

**Container Pattern**: `"Stepper container {property}."`

```python
COMPONENT_STEPPER_CONTAINER = {
    "stepper.color.container.fill": "Stepper container background.",
    "stepper.color.container.border": "Stepper container border."
}
```

**Counter Pattern**: `"Counter display {property}."` or `"Counter display {property} {state}."`

```python
COMPONENT_STEPPER_COUNTER = {
    "stepper.color.counter.fill.default": "Counter display background.",
    "stepper.color.counter.fill.disabled": "Counter display background when disabled.",
    "stepper.color.counter.border.default": "Counter display border.",
    "stepper.color.counter.border.hover": "Counter display border on hover.",
    "stepper.color.counter.border.pressed": "Counter display border when pressed.",
    "stepper.color.counter.border.focus": "Counter display border on focus.",
    "stepper.color.counter.border.disabled": "Counter display border when disabled.",
    "stepper.color.counter.text.default": "Counter display text.",
    "stepper.color.counter.text.disabled": "Counter display text when disabled."
}
```

**Interactive Pattern**: `"{Variant} stepper button {property}."` or `"Icon on {variant} stepper button."`

```python
COMPONENT_STEPPER_INTERACTIVE = {
    "stepper.color.interactive.primary.fill.default": "Primary stepper button fill.",
    "stepper.color.interactive.primary.fill.hover": "Primary stepper button fill on hover.",
    "stepper.color.interactive.primary.icon.default": "Icon on primary stepper button.",
    "stepper.color.interactive.primary.border.focus": "Primary stepper button focus ring."
    # ... same pattern for secondary variant
}
```

---

### Badge Component Tokens

```python
COMPONENT_BADGE = {
    "badge.spacing.blockPadding": "Vertical padding for badge.",
    "badge.spacing.inlinePadding": "Horizontal padding for badge.",
    "badge.spacing.gap": "Gap between icon and label in badge.",
    "badge.spacing.minHeight": "Minimum height for badge."
}
```

---

### Selection Control Component Tokens

```python
COMPONENT_SELECTION_CONTROL = {
    "selectionControl.spacing.gap": "Gap between control and label text.",
    "selectionControl.spacing.validationGap": "Gap between control row and validation message.",
    "selectionControl.spacing.errorGap": "Gap between error icon and error text."
}
```

---

### Spacing Tokens

**Padding Pattern**: `"{Property} for {size} {component}."`

```python
COMPONENT_PADDING = {
    "button.spacing.{size}.blockPadding": "Block padding for {size} buttons.",
    "button.spacing.{size}.inlinePadding": "Inline padding for {size} buttons."
}
```

**Gap Pattern**: `"Gap {between what}. {Size} {component}."`

```python
COMPONENT_GAP = {
    "button.spacing.{size}.gap": "Gap between icon and text. {Size} buttons.",
    "layout.spacing.cardGap": "Gap between card elements.",
    "layout.spacing.interactiveGap": "Gap between interactive elements.",
    "layout.spacing.contentToButton": "Gap from content to button elements.",
    "layout.spacing.formGap": "Gap between form field elements."
}
```

**Size Pattern**: `"{Size} {component} size."`

```python
COMPONENT_SIZE = {
    "icon.size.{size}": "{Size} icon size."
}
```

---

### Color Tokens

**Pattern**: `"Use for {component} {property}. {Context}."` or `"{Component} {property} {state}."`

```python
COMPONENT_COLOR = {
    # Table columns
    "column-header.color.fill.default": "Use for column header fills. Tables.",
    "column-header.color.fill.hover": "Column header fill on hover.",
    "column-header.color.fill.pressed": "Column header fill when pressed.",
    "column-header.color.highlighted.fill.default": "Use for highlighted column headers.",

    "column.color.fill.default": "Use for column fills. Tables.",
    "column.color.highlighted.fill.default": "Use for highlighted columns."
}
```

---

## Size Qualifier Mapping

Token names use full camelCase words for sizes:

```python
SIZE_MAPPING = {
    "xSmall": "extra small",
    "small": "small",
    "medium": "medium",
    "large": "large",
    "xLarge": "XL",
    "xxLarge": "XXL"
}
```

**Usage**:
- `button.spacing.medium.blockPadding` → "Block padding for **medium** buttons."
- `icon.size.xLarge` → "**XL** icon size."
- `button.spacing.small.inlinePadding` → "Inline padding for **small** buttons."

---

## Pattern Selection Logic

```python
def select_pattern(token_path):
    """
    Select appropriate description pattern based on token path.
    """
    parts = token_path.split('.')

    # TIER 1: Core tokens (global/ folder, JSON root is "core")
    if parts[0] == 'core':
        if 'dimension' in parts:
            return CORE_DIMENSION_PATTERNS
        elif 'typography' in parts:
            return CORE_TYPOGRAPHY_PATTERNS
        elif 'modify' in parts:
            return CORE_MODIFY_PATTERNS
        elif 'border' in parts:
            return CORE_BORDER_PATTERNS

    # TIER 2: Brand tokens (core/ folder, JSON root is "color")
    elif parts[0] == 'color':
        if len(parts) > 1 and parts[1] in ('brand', 'accent', 'neutrals', 'common', 'ism'):
            return BRAND_COLOR_PATTERNS

        # TIER 3: Semantic color tokens
        elif 'interactive' in parts:
            if 'primary' in parts:
                return SEMANTIC_INTERACTIVE_PRIMARY
            elif 'secondary' in parts:
                return SEMANTIC_INTERACTIVE_SECONDARY
            elif 'ghost' in parts:
                return SEMANTIC_INTERACTIVE_TERTIARY
            elif 'tertiary' in parts:
                return SEMANTIC_INTERACTIVE_TERTIARY
            elif 'inverse' in parts:
                return SEMANTIC_INTERACTIVE_INVERSE
        elif 'input' in parts:
            return SEMANTIC_INPUT
        elif 'feedback' in parts:
            return SEMANTIC_FEEDBACK
        elif 'text' in parts:
            return SEMANTIC_TEXT
        elif 'surface' in parts:
            return SEMANTIC_SURFACE
        elif 'elevation' in parts:
            return SEMANTIC_ELEVATION
        elif 'border' in parts:
            return SEMANTIC_BORDER
        elif 'status' in parts:
            return SEMANTIC_STATUS

    # Semantic non-color tokens
    elif 'typography' in parts:
        return SEMANTIC_TYPOGRAPHY
    elif 'borderRadius' in parts:
        return SEMANTIC_BORDER_RADIUS

    # TIER 4: Component tokens
    elif parts[0] in ['button', 'icon', 'layout', 'badge', 'selectionControl', 'stepper']:
        if parts[0] == 'stepper':
            return COMPONENT_STEPPER
        elif parts[0] == 'badge':
            return COMPONENT_BADGE
        elif parts[0] == 'selectionControl':
            return COMPONENT_SELECTION_CONTROL
        elif 'spacing' in parts:
            if 'Padding' in parts[-1]:
                return COMPONENT_PADDING
            elif 'gap' in parts or parts[-1] in ('cardGap', 'interactiveGap', 'contentToButton', 'formGap'):
                return COMPONENT_GAP
            else:
                return COMPONENT_SIZE
        elif 'size' in parts:
            return COMPONENT_SIZE

    return None
```

---

## Usage Examples

### Example 1: Core Dimension Token

**Token path**: `core.dimension.300`

**Pattern lookup**: CORE_DIMENSION_PATTERNS

**Description**: `"Medium spacing."`

---

### Example 2: Semantic Interactive Token

**Token path**: `color.interactive.primary.fill.hover`

**Pattern lookup**: SEMANTIC_INTERACTIVE_PRIMARY

**Description**: `"Solid button fill on hover."`

---

### Example 3: Component Spacing Token

**Token path**: `component.button.spacing.m.verticalPadding`

**Pattern lookup**: COMPONENT_PADDING

**Size mapping**: `m` → `"medium"`

**Description**: `"Vertical padding for medium buttons."`

---

## Validation Checklist

After generating a description, verify:

- [ ] Length is 20-50 characters (target range)
- [ ] No unit references (px, pt, rem, dp, etc.)
- [ ] No platform references (iOS, Android, Web)
- [ ] Component names are from actual Figma library (if semantic/component token)
- [ ] State language is consistent ("on hover", "when pressed")
- [ ] Pattern matches tier (technical for core, purpose for semantic, implementation for component)

---

## Quick Template Finder

**Need a template for**:
- **Spacing values?** → Use CORE_DIMENSION_PATTERNS
- **Font properties?** → Use CORE_TYPOGRAPHY_PATTERNS
- **Button colors?** → Use SEMANTIC_INTERACTIVE_* patterns
- **Input fields?** → Use SEMANTIC_INPUT patterns
- **Error/success states?** → Use SEMANTIC_FEEDBACK patterns
- **Component measurements?** → Use COMPONENT_SPACING/SIZE patterns

Always start with the token path, identify the tier, then select the appropriate pattern category.
