# Token Patterns Reference

This document explains the four-tier token architecture, naming conventions, and pattern recognition for design token descriptions.

---

## Four-Tier Architecture

Design tokens are organized in four tiers, each serving a specific purpose:

```
Tier 4: Component (Implementation Layer)
    references
Tier 3: Semantic (Context Layer)
    references
Tier 2: Brand (core/) - Raw brand values
    references
Tier 1: Core (global/) - Foundation primitives
```

### Tier 1: Core Tokens (Foundation) — `global/` folder

**Purpose**: Raw, context-free values that serve as building blocks

**Categories**:
- `global/dimension` - Spacing scale (base-4 system)
- `global/typography` - Font primitives (families, weights, sizes, line-heights)
- `global/modify` - Opacity/modification values for color transforms
- `global/border` - Border radius and width primitives

**JSON root key**: `core` (the folder is `global/` but the JSON nesting starts with `core`)

**Naming convention**: `core.{category}.{value}`

**Example**:
- `core.dimension.100` = 4px (base spacing)
- `core.typography.fontWeight.bold` = 700
- `core.border.radius.medium` = 8
- `core.color.modify.500` = 0.5

---

### Tier 2: Brand Tokens — `core/` folder

**Purpose**: Brand-level color values (raw values, no semantic meaning)

**Categories**:
- `color.brand.*` - Brand colors (01, 01-inverse, 02, 03)
- `color.accent.*` - Accent colors (green, red, purple, orange, turquoise, yellow, blue, magenta)
- `color.neutrals.grey.*` - Neutral grey scale (100-600)
- `color.common.*` - Common colors (white, black)
- `color.ism.*` - ISM-specific colors

**JSON root key**: `color` (no `core` wrapper)

**Naming convention**: `color.{group}.{value}`

**Example**:
- `color.brand.01` = Primary brand color (#024ddf)
- `color.accent.green` = Green accent (#048851)
- `color.neutrals.grey.300` = Mid-light grey (#D6D6D6)
- `color.common.white` = White (#ffffff)

---

### Tier 3: Semantic Tokens (Context) — `semantic/` folder

**Purpose**: Context-aware tokens that describe usage intent

**Categories**:
- `color.interactive.*` - Button states (primary, secondary, ghost, tertiary, inverse, transaction)
- `color.text.*` - Text hierarchy (primary, secondary, placeholder, inverse, onAccent)
- `color.input.*` - Form control states
- `color.feedback.*` - Validation/alert states (error, success, warning, info)
- `color.border.*` - Border colors
- `color.surface.*` - Background surfaces (primary, light, neutral variants, inverse)
- `color.elevation.*` - Depth and shadows
- `color.status.*` - Badge/tag colors
- `color.selected.*` - Selection states
- `color.active.*` - Active states
- `typography.*` - Composite text styles (display, heading, title, label, body, caption)
- `borderRadius.*` - Corner styles (interactive, input, container, popover)
- `border.interactive.*` - Border widths for interactive elements

**Naming convention**: `{category}.{subcategory}.{property}.{state}`

**Example**:
- `color.interactive.primary.fill.default` = Solid button background
- `color.input.border.error` = Input border for error state
- `typography.heading.large` = Large heading text style
- `color.surface.inverse` = Dark container background

---

### Tier 4: Component Tokens (Implementation) — `component/` folder

**Purpose**: Component-specific tokens for implementation details

**Categories**:
- `icon.size.*` - Icon dimensions (small, medium, large, xLarge)
- `layout.spacing.*` - Layout gaps (inBetweenCards, inBetweenInteractive, contentToButton, formGap)
- `button.spacing.*` - Button padding and gaps per size (blockPadding, inlinePadding, gap)

**Separate sets for desktop and mobile** (`component/spacing/desktop`, `component/spacing/mobile`)

**Naming convention**: `{component}.{category}.{size}.{property}`

**Example**:
- `button.spacing.large.blockPadding` = Block (vertical) padding for large buttons
- `button.spacing.medium.inlinePadding` = Inline (horizontal) padding for medium buttons
- `icon.size.medium` = Medium icon dimensions
- `layout.spacing.formGap` = Gap between form elements

---

## Token Path Pattern Recognition

### How to Identify Token Tier from Path

```
Path starts with "core."
  -> CORE TOKEN (Tier 1) — foundation primitives

Path starts with "color." and second segment is "brand", "accent", "neutrals", "common", or "ism"
  -> BRAND TOKEN (Tier 2) — raw brand values

Path contains "interactive", "text", "input", "feedback", "surface", "elevation", "status",
  "selected", "active", "disabled", "focus", "borderRadius", "typography", "border.interactive"
  -> SEMANTIC TOKEN (Tier 3)

Path starts with "button", "icon", "layout"
  -> COMPONENT TOKEN (Tier 4)
```

### Common Path Patterns

**Core dimension tokens**:
```
core.dimension.{value}
  value: zero, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600,
         650, 700, 750, 800, 850, 900, 1000, 1100, 1200, 1300, 1400, 1500,
         1600, 1700, 1800, 1900, 2000
```

**Core typography tokens**:
```
core.typography.fontFamily.{key}
core.typography.fontWeight.{weight}
core.typography.fontSize.{value}
core.typography.lineHeight.{value}
core.typography.letterSpacing.{value}
```

**Interactive semantic tokens**:
```
color.interactive.{variant}.{property}.{state}
  variant: primary, secondary, ghost, tertiary, inverse, transaction
  property: fill, text, icon, border
  state: default, hover, pressed, disabled
```

**Input semantic tokens**:
```
color.input.{property}.{state}
  property: fill, border, text, icon
  state: default, hover, active, success, error
```

**Typography semantic tokens**:
```
typography.{style}.{size}
  style: display, heading, title, label, body, caption
  size: large, medium, small (full words, camelCase)
  body has sub-groups: body.regular.{size}, body.bold.{size}
  caption has no sub-sizes
```

**Component spacing tokens**:
```
button.spacing.{size}.{property}
  size: large, medium, small (full words)
  property: blockPadding, inlinePadding, gap

icon.size.{size}
  size: small, medium, large, xLarge

layout.spacing.{name}
  name: inBetweenCards, inBetweenInteractive, contentToButton, formGap
```

---

## Token Naming Conventions

### Size Qualifiers

**Full camelCase words** (used throughout):
- `xSmall` -> "extra small" / "XS"
- `small` -> "small"
- `medium` -> "medium"
- `large` -> "large"
- `xLarge` -> "extra large" / "XL"
- `xxLarge` -> "2X large" / "XXL"

**Usage in descriptions**: Use full descriptive words

Examples:
- `button.spacing.medium.blockPadding` -> "Block padding for medium buttons."
- `icon.size.xLarge` -> "XL icon size."

### State Names

**Common states**:
- `default` - Base/resting state (often omitted in short descriptions)
- `hover` - Mouse hover or touch highlight
- `pressed` - Active/clicked state
- `focus` - Keyboard focus (accessibility)
- `disabled` - Inactive/unavailable state
- `active` - Currently selected/in-use

**State language patterns**:
- Hover: "on hover" (not "when hovering", "hover state")
- Pressed: "when pressed" (not "on press", "pressed state")
- Disabled: "when disabled" (not "disabled state")
- Focus: "on focus" (not "when focused")

Examples:
- `fill.hover` -> "Primary button fill on hover."
- `border.pressed` -> "Outline button border when pressed."
- `text.disabled` -> "Solid button text when disabled."

### Property Names

**Common properties**:
- `fill` - Background colors
- `text` - Text/label colors
- `icon` - Icon colors
- `border` - Border/outline colors
- `blockPadding` - Block-axis (vertical in LTR) padding
- `inlinePadding` - Inline-axis (horizontal in LTR) padding
- `gap` - Gap between child elements
- `size` - Overall dimensions

---

## Button Type Mapping

**Critical distinction**: Token names use hierarchy (primary/secondary) or style names (ghost/tertiary), but descriptions should use **visual style** names based on actual Figma usage.

| Token Name | Visual Style | Description Term |
|------------|--------------|------------------|
| `interactive.primary` | Solid filled buttons | "solid buttons" |
| `interactive.secondary` | Outline/stroked buttons | "outline buttons" |
| `interactive.ghost` | Ghost/minimal buttons | "ghost buttons" |
| `interactive.tertiary` | Low-emphasis buttons with border | "tertiary buttons" |
| `interactive.inverse` | Buttons on dark backgrounds | "inverse buttons" |
| `interactive.transaction` | Transaction/purchase buttons | "transaction buttons" |

**Why this matters**: "Primary button" is ambiguous (importance level), but "Solid button" is precise (visual appearance).

---

## Real-World Examples

### Core Token Paths
```
core.dimension.100 -> "Base spacing unit. Foundation for scale."
core.typography.fontWeight.black -> "Black weight (900). Use for headings."
core.border.radius.medium -> "Medium corner radius."
core.color.modify.500 -> "0.5 modifier. For lighten/darken/alpha."
```

### Brand Token Paths
```
color.brand.01 -> "Primary brand color. Use for main actions, links, or in any element that highlights the brand."
color.brand.01-inverse -> "Inverse primary brand color. Lighter variant for use on dark backgrounds."
color.neutrals.grey.300 -> "Mid-tone neutral grey."
color.common.white -> "Pure white."
```

### Semantic Token Paths
```
color.interactive.primary.fill.default -> "High-emphasis fills for buttons, icon buttons, and toggle buttons."
color.input.border.error -> "Input border for errors. Invalid state."
color.surface.inverse -> "Inverse surface. Use for dark container backgrounds."
typography.heading.large -> "Use for page titles. Applied to H1."
borderRadius.interactive.medium -> "Use for medium button corners."
```

### Component Token Paths
```
button.spacing.medium.blockPadding -> "Block padding for medium buttons."
icon.size.large -> "Large icon size."
layout.spacing.formGap -> "Gap between form field elements."
```

---

## Decision Tree: Determining Token Tier

```
START: You have a token path

-- Does the path start with "core."?
|  YES -> CORE TOKEN (Tier 1)
|      -- Is it dimension? -> Use "{Size} spacing" pattern
|      -- Is it typography? -> Use technical descriptor pattern
|      -- Is it color.modify? -> Use "{value} modifier" pattern
|      -- Is it border? -> Use "{Size} {type}" pattern

-- Does the path start with "color." and the second segment is brand/accent/neutrals/common/ism?
|  YES -> BRAND TOKEN (Tier 2)
|      -> Keep existing brand descriptions

-- Does it contain semantic keywords (interactive, text, input, feedback, surface, etc.)?
|  YES -> SEMANTIC TOKEN (Tier 3)
|      -- Has "default" state? -> "Use for {purpose}. {Component}."
|      -- Has other state? -> "{Component} {property} {state}."
|      -- Is typography? -> "Use for {element}. Applied to {context}."

-- Does it start with button, icon, layout?
   YES -> COMPONENT TOKEN (Tier 4)
       -- Is spacing? -> "{Property} for {size} {component}."
       -- Is gap? -> "Gap {between what}. {Size} {component}."
       -- Is size? -> "{Size} {component} size."
```

---

## Summary

- **Tier 1 (Core / `global/`)**: Technical, minimal, platform-agnostic values
- **Tier 2 (Brand / `core/`)**: Raw brand/accent/neutral color values
- **Tier 3 (Semantic / `semantic/`)**: Purpose-driven, component-specific usage contexts
- **Tier 4 (Component / `component/`)**: Implementation-specific, size-specific measurements

Always identify the tier first, then apply the appropriate description pattern from `description-templates.md`.
