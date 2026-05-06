# GDS Token Framework Reference

> Extracted from the GDS Base Token Repository spreadsheet. This is the canonical naming and structural framework for all design tokens.

---

## Core Principle: Semantic-First Token Usage

**Always use a semantic token. Only create a component token when semantic can't express it.**

This is the single most important rule in the system. Every Figma node binding should point to the semantic layer (`color.*`, `typography.*`, `borderRadius.*`, `border.*`) unless there is a specific reason it can't.

### Why this matters: theme switching

The entire theming system — including light → dark mode — works by swapping the semantic layer. Core and Brand tokens don't change between themes. What changes is `semantic/colorLight.json` → `semantic/colorDark.json`. Because component tokens reference semantic tokens, and semantic tokens reference brand/core, the full cascade updates automatically when you switch themes.

```
Core (never changes)
  └── Brand (never changes)
        └── Semantic ← THIS IS WHAT CHANGES PER THEME
              └── Component (follows automatically)
                    └── Figma node binding (follows automatically)
```

If a component token skips the semantic layer and references `color.brand.01` directly, it will **not** respond to theme switching. That's a bug.

### Decision tree: when to use which tier

```
Q: Does a semantic token express this intent?
   → Yes → Use it directly. Don't create a component token.
   → No  → Does another semantic token express it close enough?
              → Yes → Use the closest semantic token. Document the mapping.
              → No  → Create a component token that references the semantic token.
                       Never reference core or brand directly from a component token.
```

### What "semantic-first" looks like in practice

**Good — binding directly to semantic:**
```
Button fill (primary, default)  →  color.interactive.primary.fill.default
Button text (disabled)          →  color.interactive.primary.text.disabled
Input border (error)            →  color.feedback.border.error
Modal overlay                   →  color.elevation.overlay
Badge fill (success)            →  color.status.positive.fill
```

**Good — component token that wraps semantic (used when the component has unique logic):**
```
toggle.color.container.fill.on  →  { $value: "{color.interactive.primary.fill.default}" }
toast.color.fill                →  { $value: "{color.elevation.inverse}" }
stepper.color.counter.fill.default → { $value: "{color.surface.neutral01}" }
```

**Bad — skipping the semantic layer:**
```
Button fill  →  color.brand.01          ← Hard-coded to TM brand, won't theme
Input text   →  core.typography.100     ← Raw primitive, no semantic meaning
Modal border →  #121212                 ← Hardcoded hex, completely outside the system
```

### When a component token IS the right choice

Create a component-level token file when:
- The component uses a colour relationship that no existing semantic token captures (e.g. the Toggle's container fill differs depending on on/off state in a way that `color.interactive.primary.*` alone can't represent)
- The component needs a unique combination of tokens per visual state that benefits from being named explicitly (e.g. stepper's counter display, which has its own fill/text/border triad)
- You need to document the intent clearly — a component token is self-describing in a way that a raw semantic reference isn't

Even then, the component token's `$value` must always be a reference to a semantic token, never to core or brand directly.

### The dark mode contract

When `semantic/colorDark.json` is created, it will mirror the exact same token paths as `semantic/colorLight.json`, but with dark-appropriate resolved values. For example:

| Token path | Light | Dark |
|-----------|-------|------|
| `color.elevation.base` | `#FFFFFF` | `#1A1A1A` |
| `color.text.primary` | `#121212` | `#F5F5F5` |
| `color.interactive.primary.fill.default` | `#024DDF` | `#4D8AFF` |
| `color.elevation.overlay` | `rgba(18,18,18,0.7)` | `rgba(0,0,0,0.85)` |

Any Figma binding that points to a semantic token will automatically resolve to the dark value when the dark theme is active — zero additional work required at the component level.

---

## Architecture: 4-Tier Token Hierarchy

```
Global (Core)  -->  Global (Brand)  -->  Semantic  -->  Component
     g                   g                  s              c
```

| Tier | Sentiment | Prefix | Purpose |
|------|-----------|--------|---------|
| Global Core | `g` | `core.*` | Raw primitive values (dimensions, typography scales, color modifiers, border) |
| Global Brand | `g` | `brand.*` / `core.color.brand.*` | Brand identity values (colors, shadows, brand typography) |
| Semantic | `s` | `color.*`, `typography.*`, `spacing.*`, `elevation.*`, `borderRadius.*` | Contextual meaning (interactive, feedback, elevation, etc.) |
| Component | `c` | `{component}.*` | Component-specific tokens (button, inputBox, accordion, etc.) |

### Design System Scoping

| Prefix | Scope | Used At |
|--------|-------|---------|
| `gds` | Global Design System (shared across all products) | Core tokens |
| `gdsm` | GDS Marketplace (product-specific) | Brand, Semantic, Component tokens |
| `--gds` / `--gdsm` | CSS custom property output prefix | Semantic and Component tiers |

---

## File Structure (Token Studio + Figma)

This is the required directory layout for Token Studio to sync with Figma. Each JSON file maps to a Token Set in Token Studio.

```
tokens/
  $metadata.json            ← Token set resolution order
  $themes.json              ← Theme definitions (maps sets to Figma collections/modes)
  core/
    dimension.json          ← core.dimension.*        (4px base spacing scale)
    typography.json         ← core.typography.*        (font families, weights, sizes, lineHeights, letterSpacing)
    modify.json             ← core.color.modify.*      (0-1.0 color modification multipliers)
    border.json             ← core.border.*            (border radius + border width primitives)
  brand/
    color.json              ← color.brand.*, color.accent.*, color.neutrals.*, color.common.*
  semantic/
    colorLight.json         ← color.* semantic tokens  (interactive, feedback, elevation, etc.) + elevation box shadows
    typography.json         ← typography.*             (composite typography tokens: display, heading, title, label, body, caption)
    borderRadius.json       ← borderRadius.*           (interactive, input, container, popover)
    border.json             ← border.*                 (interactive border widths)
  component/
    spacing/
      desktop.json          ← Component spacing/sizing for desktop breakpoint
      mobile.json           ← Component spacing/sizing for mobile breakpoint
```

### Key structural rules

1. **`$metadata.json`** defines the `tokenSetOrder` array — this controls the resolution order when Token Studio resolves references. Core sets must come before Brand, Brand before Semantic, Semantic before Component.

2. **`$themes.json`** defines theme objects that:
   - Map token sets to `enabled`/`disabled`/`source` status via `selectedTokenSets`
   - Link to Figma Variable Collections via `$figmaCollectionId`
   - Link to Figma Variable Modes via `$figmaStyleReferences` and `$figmaVariableReferences`
   - Group themes (e.g., `Light` and `Dark` under group `GDS-M - Theme`)

3. **Each JSON file's top-level keys** become the token group namespace. For example, `core/dimension.json` wraps everything under `{ "core": { "dimension": { ... } } }`, and `brand/color.json` wraps under `{ "color": { ... } }`.

4. **Cross-file references** use curly brace syntax: `{core.dimension.100}` can be referenced from any file that is `enabled` in the same theme. The full dot-path is resolved across all enabled token sets.

5. **The `semantic/colorLight.json` file is the largest** — it contains all semantic color tokens AND the elevation box shadow tokens. The box shadows sit at the root `elevation` key (sibling to `color`), not nested inside `color`.

### Resolution order (from `$metadata.json`)

```
1. core/dimension
2. core/typography
3. core/modify
4. core/border
5. brand/color
6. semantic/colorLight
7. semantic/typography
8. semantic/borderRadius
9. semantic/border
10. component/spacing/desktop
11. component/spacing/mobile
```

---

## Token Studio Extensions: Color Modifiers

Token Studio supports color modification through the `$extensions.studio.tokens.modify` property. These are critical for the semantic color system — **89 tokens** in `colorLight.json` use them. They MUST be preserved when rebuilding tokens.

### Modifier Structure

```json
{
  "$extensions": {
    "studio.tokens": {
      "modify": {
        "type": "darken",
        "value": "{core.color.modify.100}",
        "space": "hsl"
      }
    }
  },
  "$type": "color",
  "$value": "{color.interactive.primary.fill.default}"
}
```

The modifier transforms the `$value` color using the specified operation.

### 4 Modifier Types

| Type | Effect | Usage Count | Purpose |
|------|--------|-------------|---------|
| `darken` | Darkens the base color | ~45 | Hover/pressed states, text on accent backgrounds |
| `lighten` | Lightens the base color | ~25 | Disabled states, secondary text, feedback fills, status fills, border colors |
| `alpha` | Applies transparency | ~15 | Secondary/ghost fills, transparent overlays, ghost hover/pressed |
| `mix` | Mixes two colors together | 1 | Elevation accentA (mix brand with neutral) |

### Color Spaces

| Space | Usage | Notes |
|-------|-------|-------|
| `hsl` | ~87 of 89 | Primary space used for nearly all modifications |
| `lch` | 2 | Only used for `color.disabled.b` and `color.disabled.c` |

### Modifier Patterns by Token Category

#### Interactive states (darken for depth)
```
default:  no modifier (base color reference)
hover:    darken by modify.50 to modify.100
pressed:  darken by modify.100 to modify.200
disabled: reference to color.disabled.b (no modifier, just alias)
```

#### Ghost/Secondary fills (alpha for transparency)
```
default:  alpha by modify.zero (fully transparent)
hover:    alpha by modify.50 (barely visible)
pressed:  alpha by modify.100 (slightly visible)
```

#### Text hierarchy (lighten for de-emphasis)
```
primary:    no modifier (brand.02 direct)
secondary:  lighten by modify.450
placeholder: lighten by modify.600
```

#### Disabled tokens (lighten from brand dark)
```
disabled.a: lighten brand.02 by modify.550 (hsl) — background disabled
disabled.b: lighten brand.02 by modify.750 (lch) — text/fill disabled
disabled.c: lighten brand.02 by modify.300 (lch) — heavy disabled
```

#### Border tokens (lighten for subtlety)
```
border.primary:   lighten brand.02 by modify.550
border.secondary: lighten brand.02 by modify.800
border.elevation: lighten brand.02 by modify.900
```

#### Elevation tokens
```
undercanvas:  darken elevation.base by modify.50
relative1:   darken elevation.base by modify.50
overlay:      alpha brand.02 by modify.700
accentA:     mix brand.02 with core.color.brand.02 by modify.700
```

#### Feedback fills (lighten accent colors heavily)
```
feedback.fill.error:   lighten accent.red   by modify.950
feedback.fill.success: lighten accent.green by modify.950
feedback.fill.warning: lighten accent.orange by modify.950
feedback.fill.info:    lighten accent.blue  by modify.950
```

#### Status fills (lighten for badge backgrounds)
```
status.draft.fill:     lighten brand.02     by modify.900
status.active.fill:    lighten brand.01     by modify.900
status.positive.fill:  lighten accent.green by modify.900
status.critical.fill:  lighten accent.red   by modify.900
status.attention.fill: lighten accent.orange by modify.900
```

### The `mix` modifier (special case)

Only one token uses `mix` — it requires an additional `color` property:

```json
"accentA": {
  "$extensions": {
    "studio.tokens": {
      "modify": {
        "type": "mix",
        "value": "{core.color.modify.700}",
        "space": "hsl",
        "color": "{core.color.brand.02}"
      }
    }
  },
  "$type": "color",
  "$value": "{color.brand.02}"
}
```

This mixes `{color.brand.02}` with `{core.color.brand.02}` at 70% strength in HSL space.

---

## Cross-File Reference (Alias) Chain

Tokens form a reference chain across files. Understanding these chains is essential for building tokens correctly.

### Reference direction (always flows downward)

```
core/dimension.json ─────────────────────────────────────────────┐
core/typography.json ────────────────────────────────────────────┐│
core/modify.json ───────────────────────────────────────────────┐││
core/border.json ──────────────────────────────────────────────┐│││
                                                               ││││
brand/color.json ──────────────────────────────────────────────┤│││
  (references nothing — all raw hex values)                    ││││
                                                               ││││
semantic/colorLight.json ─────────────────────────────────────┤│││
  references: brand/color.json (color.brand.*, color.accent.*) │││├─>
  references: core/modify.json (core.color.modify.*)           │││
  references: itself (internal aliases within semantic layer)   ││
                                                               ││
semantic/typography.json ──────────────────────────────────────┤│
  references: core/typography.json (fontFamily, weight, size) ││
  references: core/dimension.json (display.medium/small sizes) │
                                                               │
semantic/borderRadius.json ───────────────────────────────────┤
  references: core/border.json (core.border.radius.*)          │
  references: core/dimension.json (core.dimension.*)           │
                                                               │
semantic/border.json ──────────────────────────────────────────┤
  references: core/border.json (core.border.width.*)           │
                                                               │
component/spacing/desktop.json ────────────────────────────────┘
  references: core/dimension.json (core.dimension.*)
```

### Common alias patterns

**Direct alias** (no transformation):
```json
{ "$type": "color", "$value": "{color.brand.01}" }
```

**Alias + modifier** (transformed reference):
```json
{
  "$extensions": { "studio.tokens": { "modify": { "type": "darken", "value": "{core.color.modify.100}", "space": "hsl" } } },
  "$type": "color",
  "$value": "{color.interactive.primary.fill.default}"
}
```

**Self-referencing alias** (semantic token referencing another semantic token):
```json
"color.active.fill.default": "{color.interactive.secondary.fill.default}"
"color.active.border.default": "{color.interactive.primary.fill.default}"
```

**Math expression alias** (core tokens):
```json
{ "$type": "dimension", "$value": "{core.dimension.100}*2" }
```

### Box Shadow tokens (special structure)

The elevation box shadows in `colorLight.json` use a different structure — array of shadow objects, not references:

```json
{
  "$type": "boxShadow",
  "$value": [
    {
      "x": "0",
      "y": "1",
      "blur": "4",
      "spread": "0",
      "color": "rgba(18,18,18,0.15)",
      "type": "dropShadow"
    }
  ]
}
```

Current shadow values:
| Token | y | blur | color opacity |
|-------|---|------|---------------|
| `elevationLevel1` | 1 | 4 | 0.15 |
| `elevationLevel2` | 2 | 8 | 0.15 |
| `elevationLevel3` | 3 | 12 | 0.18 |
| `elevationLevel4` | 8 | 20 | 0.35 |

---

## Spreadsheet Column Definitions

Each tier uses a structured set of columns that concatenate to form the final token name.

### Global Tokens (Core)

| Column | Description | Examples |
|--------|-------------|----------|
| Design system | System scope | `gds` |
| Sentiment | Tier indicator | `g` (global) |
| Grouping | Always `core` | `core` |
| Type | Token category | `dimension`, `typography` |
| Property | Sub-property (typography only) | `fontFamily`, `fontWeight`, `fontSize`, `lineHeight`, `letterSpacing` |
| Scale | Numeric or named scale step | `zero`, `50`, `100`, `150`... `2000` / `base`, `light`, `regular` |
| Token | Resulting token path | `core.dimension.100`, `core.typography.fontWeight.bold` |
| Value | Raw value | `4`, `Averta`, `600` |

### Global Tokens (Brand)

| Column | Description | Examples |
|--------|-------------|----------|
| Design system | System scope | `gds` (core colors), `gdsm` (brand/accent) |
| Sentiment | Tier indicator | `g` (global) |
| Grouping | `core` or `brand` | `core` for brand base colors, `brand` for accents/neutrals/shadows |
| Type | Token category | `color`, `shadow`, `typography` |
| Name | Named identifier | `brand`, `accent`, `neutrals`, `common`, `shadow` |
| Scale | Numeric or named | `01`, `02`, `03` / `100`-`500` / `zero`-`400` |
| Token | Resulting token path | `core.color.brand.01`, `brand.accent.green.`, `brand.neutrals.grey.300` |
| Value | Raw value | `#024dff`, `#050505`, `#FFFFFF` |
| Type (col I) | Token Studio type | `color`, `shadow`, `typography` |

### Semantic Tokens

| Column | Description | Examples |
|--------|-------------|----------|
| Design system | System scope | `--gdsm` |
| Sentiment | Tier indicator | `.s.` (semantic) |
| Type | Token category | `color`, `typography`, `spacing`, `elevation`, `borderRadius` |
| Grouping | Functional context | `.interactive`, `.feedback`, `.input`, `.elevation`, `.selected`, `.status` |
| Scale | Variant/priority | `.primary`, `.secondary`, `.tertiary`, `.critical`, `.level1` |
| Role | Target property | `.fill`, `.text`, `.icon`, `.border`, `.placeholder` |
| State | Interaction state | `.default`, `.hover`, `.pressed`, `.error`, `.success` |
| Token | Resulting token path | `color.interactive.primary.fill.default` |

### Component Tokens

| Column | Description | Examples |
|--------|-------------|----------|
| Design system | System scope | `--gds` |
| Sentiment | Tier indicator | `.c.` (component) |
| Component | Target component | `button`, `inputBox`, `accordion`, `tableCell` |
| Type | Token category | `.spacing`, `.size`, `.color` |
| Scale | Size variant | `.s`, `.m`, `.l` |
| Role | Target property | `.blockPadding`, `.inlinePadding`, `.gap`, `.minHeight`, `.fill` |
| State | Interaction state | `.default`, `.hover`, `.pressed` |
| Token | Resulting token path | `button.spacing.s.blockPadding`, `columnHeader.color.fill.default` |

---

## Token Naming Formula

### Semantic tokens
```
{type}.{grouping}.{scale?}.{role}.{state?}
```

Examples:
- `color.interactive.primary.fill.default`
- `color.feedback.fill.error`
- `color.elevation.level1`
- `color.input.border.active`
- `color.selected.primary.text.hover`

### Component tokens
```
{component}.{type}.{scale?}.{role}.{state?}
```

Examples:
- `button.spacing.small.blockPadding`
- `button.spacing.medium.inlinePadding`
- `iconButton.size.xLarge`
- `iconButton.size.s`
- `columnHeader.color.fill.default`
- `columnHeader.color.highlighted.fill.hover`
- `tableCell.spacing.comfortable.minHeight`

### Core tokens
```
core.{type}.{property?}.{scale}
```

Examples:
- `core.dimension.100`
- `core.typography.fontSize.base`
- `core.typography.fontWeight.bold`
- `core.color.modify.500`
- `core.border.radius.medium`

### Brand tokens
```
core.color.brand.{scale}         (for base brand colors)
brand.{name}.{color}.             (for accent/common colors)
brand.neutrals.grey.{scale}       (for neutral greys)
brand.shadow.shadow.{scale}       (for shadows)
brand.typography.{property}.{name} (for brand typography)
```

---

## Allowed Values (Semantic Properties Vocabulary)

These are the valid values for each segment of a semantic token name.

### Type
`color`, `typography`, `spacing`, `elevation`, `borderRadius`

### Grouping (Semantic Color Categories)

| Category | Subtypes / Tokens | Elements to Target | Used In Components |
|----------|-------------------|--------------------|--------------------|
| `.interactive` | primary, secondary, tertiary | Fill, Text, Icon | Button, Circle Button |
| `.disabled` | text (muted), background (greyed) | Fill, Text, Icon | Button, Circle Button, Checkbox, Radio Button |
| `.focus` | focus border color | Border | Button, Input Field, Text area, Radio Button |
| `.text` | primary, secondary, placeholder, inverse, onAccent | Text | Button, Country Picker, Date of Birth |
| `.icon` | primary, secondary | Icon | Button |
| `.border` | default, onAccent, inverse | Border | Button, Accordion |
| `.input` | border, fill, text | Fill, Text, Icon | Text Input, Text area, Double Range Input |
| `.feedback` | error, success, warning, info (fill, border, text) | Fill, Text, Icon | Alert |
| `.active` / `.selected` | fill, border, text | Fill, Text, Icon | RadioButton, Checkbox |
| `.status` | draft, active, positive, critical, attention, neutral, etc | Fill, Text, Icon | Badge |
| `.surface` | primary, neutral, inverse | Fill | Sections, promotional areas, bespoke backgrounds |
| `.elevation` | level0, level1 to level4 (overlay) | boxShadow | Card, Modal, Tooltip |

### Grouping (Other Types)

| Value | Purpose |
|-------|---------|
| `.display` | Display typography |
| `.heading` | Heading typography |
| `.title` | Title typography |
| `.body` | Body text typography |
| `.label` | Label typography |
| `.labelUnderline` | Underlined label typography |
| `.data` | Data/tabular typography |
| `.list` | List content |
| `.container` | Container/layout |
| `.action` | Action areas |
| `.inverse` | Inverted context (dark bg in light mode) |

### Scale
| Value | Purpose |
|-------|---------|
| `.primary` | Primary variant |
| `.secondary` | Secondary variant |
| `.tertiary` | Tertiary variant |
| `.critical` | Critical/destructive |
| `.inverse` | Inverted context |
| `.onPrimary` | Content on primary background |
| `.elevation` | Elevation context |
| `.overlay` | Overlay context |
| `.accentA` | First accent variant |
| `.accentB` | Second accent variant |
| `.onAccent` | Content on accent background |
| `.xxSmall` | Size: xxSmall |
| `.xSmall` | Size: xSmall |
| `.small` | Size: small |
| `.medium` | Size: medium |
| `.large` | Size: large |
| `.xLarge` | Size: xLarge |
| `.xxLarge` | Size: xxLarge |
| `.full` | Full/maximum |
| `.a`, `.b`, `.c` | Named variants (use sparingly) |
| `.base` | Base/default level |
| `.undercanvas` | Below canvas level |
| `.canvas` | Canvas level (Level 0) |
| `.level1` through `.level5` | Elevation levels |
| `.draft` | Draft status |
| `.positive` | Positive status |
| `.attention` | Attention/caution status |
| `.neutral` | Neutral status |
| `.update` | Update status |
| `.general` | General status |
| `.active` | Active status |
| `.none` | No value |
| `.relative1` | Relative elevation offset |
| `.highlighted` | Highlighted variant |
| `.default` | Default size variant |
| `.comfortable` | Comfortable density |

### Role
| Value | Purpose |
|-------|---------|
| `.fill` | Background/surface fill |
| `.text` | Text content |
| `.icon` | Icon content |
| `.border` | Border/stroke |
| `.inlinePadding` | Inline (left/right / start/end) padding |
| `.blockPadding` | Block (top/bottom) padding |
| `.gap` | Gap between elements |
| `.minHeight` | Minimum height constraint |
| `.maxWidth` | Maximum width constraint |
| `.height` | Fixed height |
| `.placeholder` | Placeholder text |
| `.onPrimary` | Content on primary fill |
| `.horizontal` | Horizontal direction |
| `.vertical` | Vertical direction |
| `.between` | Between/gap direction |

### State
| Value | Purpose |
|-------|---------|
| `.default` | Default/resting state |
| `.hover` | Hover state |
| `.pressed` | Pressed/active state |
| `.error` | Error state |
| `.success` | Success state |
| `.info` | Informational state |
| `.warning` | Warning state |
| `.focus` | Focused state |
| `.active` | Active/toggled state |
| `.selected` | Selected state |

---

## Allowed Values (Component Properties Vocabulary)

### Components
`button`, `iconButton`, `inputBox`, `badge`, `icon`, `banner`, `selectionControl`, `listItem`, `selection`, `container`, `tooltip`, `segmentedControl`, `segment`, `objectListCell`, `objectList`, `columnHeader`, `column`, `tableCell`, `accordion`, `form`

### Type
`.color`, `.typography`, `.spacing`, `.elevation`, `.borderRadius`, `.size`

### Scale (t-shirt sizes for components)
`.xxSmall`, `.xSmall`, `.small`, `.medium`, `.large`, `.xLarge`, `.xxLarge`

### Role
`.fill`, `.text`, `.icon`, `.border`, `.inlinePadding`, `.blockPadding`, `.gap`, `.minHeight`, `.maxWidth`, `.height`

### State
`.default`, `.hover`, `.pressed`, `.error`, `.success`, `.info`, `.warning`, `.focus`, `.active`, `.selected`

---

## Core Token Scales

### Dimension Scale (4px base unit)

| Scale | Value (px) | Calculation |
|-------|-----------|-------------|
| `zero` | 0 | — |
| `50` | 2 | base / 2 |
| `100` | 4 | **base** |
| `150` | 6 | base * 1.5 |
| `200` | 8 | base * 2 |
| `250` | 10 | base * 2.5 |
| `300` | 12 | base * 3 |
| `350` | 14 | base * 3.5 |
| `400` | 16 | base * 4 |
| `450` | 18 | base * 4.5 |
| `500` | 20 | base * 5 |
| `550` | 22 | base * 5.5 |
| `600` | 24 | base * 6 |
| `650` | 26 | base * 6.5 |
| `700` | 28 | base * 7 |
| `750` | 30 | base * 7.5 |
| `800` | 32 | base * 8 |
| `850` | 34 | base * 8.5 |
| `900` | 36 | base * 9 |
| `1000` | 40 | base * 10 |
| `1100` | 44 | base * 11 |
| `1200` | 48 | base * 12 |
| `1300` | 52 | base * 13 |
| `1400` | 56 | base * 14 |
| `1500` | 60 | base * 15 |
| `1600` | 64 | base * 16 |
| `1700` | 68 | base * 17 |
| `1800` | 72 | base * 18 |
| `1900` | 76 | base * 19 |
| `2000` | 80 | base * 20 |

**Rule**: Steps of 50 from `zero` to `900`, then steps of 100 from `1000` to `2000`. Every 50-step = 2px increment.

### Brand Color Scale

| Token | Value | Purpose |
|-------|-------|---------|
| `core.color.brand.01` | `#024dff` | Primary brand blue |
| `core.color.brand.02` | `#050505` | Primary brand dark |
| `core.color.brand.03` | `#FFFFFF` | Primary brand white |

### Brand Accent Colors
`brand.accent.{name}.` where name = `green`, `red`, `purple`, `orange`, `turquoise`, `yellow`, `blue`, `magenta`

> Note: Accent colors are surface tokens created from these base above by adding a 3rd color modifier.

### Brand Neutrals (Grey Scale)

| Token | Scale |
|-------|-------|
| `brand.neutrals.grey.100` | Lightest |
| `brand.neutrals.grey.200` | |
| `brand.neutrals.grey.300` | |
| `brand.neutrals.grey.400` | |
| `brand.neutrals.grey.500` | Darkest |

### Brand Shadows

| Token | Scale |
|-------|-------|
| `brand.shadow.shadow.zero` | No shadow |
| `brand.shadow.shadow.100` | Level 1 |
| `brand.shadow.shadow.200` | Level 2 |
| `brand.shadow.shadow.300` | Level 3 |
| `brand.shadow.shadow.400` | Level 4 |

### Brand Typography
- `brand.typography.fontVariant.numeric` — for data-style typography
- `brand.typography.textDecoration.underline` — for underline text decoration

### Color Modify Scale (0.0 to 1.0)

Base unit: `0.1` at scale `100`. Range: `zero` (0) to `1000` (1.0) in steps of 50.

Used as inputs to Token Studio's `darken`, `lighten`, `alpha`, and `mix` color modifiers.

---

## Elevation System

### Levels

| Level | Name | Purpose |
|-------|------|---------|
| Level 0 | `canvas` | Default canvas level to build screens on (Body) |
| Level 1 | `level1` | Hierarchy within content on Level 0 (basic cards) |
| Level 2 | `level2` | Sticky elements (header, footer), extra lift on cards |
| Level 3 | `level3` | Multiple sticky elements, panels floating over content |
| Level 4 | `level4` | Overlay background (modals, sidepanels) |
| Level 5 | `level5` | Reserved for future use |

### Visual Elements
- **Shadows** (v2.0): `brand.shadow.shadow.{100-400}` mapped to elevation levels
- **Surface fill colour** (v2.0): `color.elevation.{level}` tokens
- **Border colour** (v2.0): `color.border.elevation`

### Additional Elevation Tokens
| Token | Purpose |
|-------|---------|
| `color.elevation.base` | Base surface (white in light mode) |
| `color.elevation.undercanvas` | Below canvas level |
| `color.elevation.inverse` | Inverted elevation (dark surface in light mode) |
| `color.elevation.overlay` | Semi-transparent overlay |
| `color.elevation.accentA` | Accent surface variant A |
| `color.elevation.accentB` | Accent surface variant B |
| `color.elevation.relative1` | Relative offset from current level |

---

## Component Token Patterns

### Standard spacing pattern for sized components

Most components follow this pattern per size variant:

```
{component}.spacing.{xxSmall..xxLarge}.blockPadding
{component}.spacing.{xxSmall..xxLarge}.inlinePadding
{component}.spacing.{xxSmall..xxLarge}.gap
{component}.spacing.{xxSmall..xxLarge}.minHeight
```

### Components with color tokens

Color tokens at the component level use the pattern:
```
{component}.color.{scale?}.{role}.{state}
```

Example: `columnHeader.color.highlighted.fill.hover`

### Components without size variants

Some components omit the scale segment:
```
{component}.spacing.blockPadding
{component}.spacing.inlinePadding
{component}.spacing.gap
```

Examples: `tooltip`, `accordion`, `segmentedControl`, `objectList`

### Special component tokens

| Component | Special Tokens |
|-----------|---------------|
| `icon` | `icon.size.{small|medium}` (not spacing, but size) |
| `iconButton` | `iconButton.size.{xxSmall..xxLarge}` + spacing |
| `objectListCell` | `.size.height` (fixed height, not padding) |
| `badge` | Only `.spacing.{medium|large}` (not all sizes) |
| `tableCell` | Uses `.default` and `.comfortable` density scales instead of s/m/l |
| `columnHeader` | Has `.highlighted` sub-variant for color tokens |

---

## Key Differences: Spreadsheet Framework vs Current Token Files

| Aspect | Current Tokens | Spreadsheet Framework |
|--------|---------------|----------------------|
| Dimension scale | Gaps (no 150, 250, 350, etc.) | Complete 50-2000 range, every 50-step |
| Brand colors | 2 (`01`, `02`) | 3 (`01`, `02`, `03` = white) |
| Brand neutrals | `gray-4` to `gray-8` (inverted) | `grey.100` to `grey.500` (ascending) |
| Brand shadows | Not defined | `shadow.zero` to `shadow.400` |
| Component token structure | Flat (icon/layout/button) | Proper `{component}.{type}.{scale}.{role}` |
| Component list | Only icon, layout, button | 20 components defined |
| Naming convention | Mixed camelCase/kebab-case | Consistent camelCase everywhere, no hyphens |
| Mobile/Desktop | Separate files with inconsistencies | Not yet defined (likely via themes/modes) |

---

## Rules for Creating New Tokens

1. **Always reference the vocabulary**: Check the Semantic Properties or Component Properties vocabulary before inventing new segment values.

2. **Follow the tier**: Never skip tiers. Core defines primitives, Brand applies identity, Semantic gives meaning, Component targets usage.

3. **Semantic tokens reference Brand/Core**: Semantic token values should be references to `brand.*` or `core.*` tokens, potentially with Token Studio color modifiers (`darken`, `lighten`, `alpha`, `mix`).

4. **Component tokens reference Semantic**: Component token values should reference `color.*` (semantic) or `core.dimension.*` tokens.

5. **Use the naming formula**: Always construct names by concatenating the column segments with dots.

6. **Scale is optional**: Not every token needs a scale segment. Only include it when there are multiple variants (e.g., primary/secondary, s/m/l).

7. **State is optional**: Only include state when the token varies by interaction (e.g., hover, pressed). Static tokens omit state.

8. **camelCase for role properties**: Padding/spacing roles use camelCase (`inlinePadding`, `blockPadding`, `gap`, `minHeight`).

9. **camelCase for everything**: All token name segments use camelCase. No hyphens in token names (`inputBox`, `borderRadius`, `onAccent`, `iconButton`, `columnHeader`).

10. **Numeric scales use the established steps**: Dimensions use 50-step increments. Typography uses its own scale. Don't invent new numeric steps.

11. **Shadows live in Brand tier**: Shadow values are defined at `brand.shadow.shadow.{scale}`, not at the semantic level.

12. **Elevation surfaces live in Semantic tier**: Surface colors for elevation levels are semantic tokens (`color.elevation.level1`), while shadow values come from brand.

13. **Component spacing files contain only spacing tokens**: The `component/spacing/` files (desktop.json, mobile.json) must only contain spacing-related tokens (`spacing`, `gap`, `padding`, `minHeight`, dimension tokens used for layout gaps). Non-spacing tokens (color, borderRadius, borderWidth, size) belong in the semantic layer or dedicated component token files, not in the spacing sets.
