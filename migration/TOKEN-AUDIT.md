# Token Audit

> Generated from review of Token Studio JSON files in `tokens/`

## Token Architecture

The tokens follow a **3-tier hierarchy**: Core → Semantic (Brand) → Component

```
┌─────────────────────────────────────────────────┐
│  Component Tokens                               │
│  component/spacing/desktop, component/spacing/mobile │
│  (icon sizes, layout spacing, button padding)   │
├─────────────────────────────────────────────────┤
│  Semantic Tokens                                │
│  semantic/color-light, semantic/typography,      │
│  semantic/border-radius, semantic/border         │
│  brand/color                                    │
├─────────────────────────────────────────────────┤
│  Core Tokens                                    │
│  core/dimension, core/typography, core/modify,  │
│  core/border                                    │
└─────────────────────────────────────────────────┘
```

## Token Set Inventory

### 1. `core/dimension` (17 tokens)
- Base unit: `4px` (`core.dimension.100`)
- Scale: 50, 100, 200, 300, 400, 500, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2400, 2800, 3200, zero
- Pattern: Math expressions against base (`{core.dimension.100}*N`)

### 2. `core/typography` (49 tokens)
- **Font family**: 1 token (Averta, sans-serif)
- **Font weight**: 5 tokens (light/300, regular/400, semibold/600, bold/700, black/900)
- **Font size**: 21 tokens (25–900 scale, base 16 at `100`)
- **Line height**: 19 tokens (25–800 scale + `full`, base 16 at `100`)
- **Letter spacing**: 6 tokens (100, 300, 800, neg-100, neg-200, neg-300)

### 3. `core/modify` (21 tokens)
- Opacity/modification multipliers for color transforms
- Base unit: `0.1` (`core.color.modify.100`)
- Scale: zero, 50–1000 in steps of 50
- Used by `$extensions.studio.tokens.modify` in semantic colors

### 4. `core/border` (12 tokens)
- **Radius**: 7 tokens (xsmall/2, small/4, medium/6, large/8, xlarge/12, xxlarge/20, full/999)
- **Width**: 5 tokens (xsmall/1, small/2, medium/3, large/4, xlarge/8)

### 5. `brand/color` (15 tokens)
- **Brand**: 2 tokens (01: #024ddf blue, 02: #121212 near-black)
- **Accent**: 8 tokens (green, red, purple, orange, turquoise, yellow, blue, magenta)
- **Neutrals**: 5 tokens (gray-4 through gray-8)
- **Common**: 2 tokens (white, black)

### 6. `semantic/color-light` (~120+ tokens)
- **Interactive**: primary, secondary, ghost, tertiary, transaction — each with fill/text/icon/border + default/hover/pressed/disabled states
- **Interactive (shorthand)**: fill, text, icon — aliasing secondary variants
- **Disabled**: a, b, c
- **Focus**: border
- **Text**: primary, secondary, placeholder, inverse, on-accent
- **Icon**: primary, secondary
- **Border**: primary, secondary, elevation, inverse, on-accent
- **Input**: fill, border, text, icon — each with default/hover/active states + border success/error
- **Feedback**: fill, text, icon, border — each with error/success/warning/info
- **Active**: fill, border, text
- **Elevation**: canvas, base, undercanvas, relative-1, level-1 through level-5, inverse, overlay, accent-a, accent-b
- **Selected**: primary (fill/icon/text with default/hover/pressed)
- Heavy use of `$extensions.studio.tokens.modify` for darken/lighten/alpha/mix transforms

### 7. `semantic/typography` (17 composite tokens)
- **Display**: large, medium, small (font-weight: black, uppercase: no, textCase: none)
- **Heading**: large, medium, small (font-weight: black, textCase: uppercase)
- **Title**: large, medium, small (font-weight: black, textCase: uppercase)
- **Label**: large, medium, small (font-weight: semibold)
- **Body regular**: large, medium, small (font-weight: regular)
- **Body bold**: large, medium, small (font-weight: bold)
- **Caption**: 1 token (font-weight: regular, textCase: uppercase)

### 8. `semantic/border-radius` (16 tokens)
- **Interactive**: small, medium, large, full
- **Input**: small, medium, large, full
- **Container**: none, small, medium, large
- **Popover**: none, small, medium, large

### 9. `semantic/border` (2 tokens)
- **Interactive**: xsmall, small

### 10. `component / spacing / desktop` (14 tokens)
- **Icon size**: small (12), medium (16), large (24), xlarge (32)
- **Layout spacing**: cardGap (24), interactiveGap (16), contentToButton (24), formGap (24)
- **Button spacing**: large/medium/small — verticalPadding + horizontalPadding

### 11. `component / spacing / mobile` (8 tokens)
- **Icon size**: small (12), medium (16), large (24), xlarge (24)
- **Layout spacing**: in-between-cards (24px), in-between-interactive (24px), content-to-button (24px), form (24px)
- No button spacing tokens

---

## Themes Configuration

The `$themes.json` defines individual themes per token set (not composited):
- Core - Dimension
- Core - Typography
- Core - Colour
- (Others likely present in the full file)

Each theme maps to a **Figma Variable Collection** and **Mode**, with `$figmaVariableReferences` linking Token Studio token paths to Figma variable IDs.

---

## Issues Found

### Critical

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | **Zero-width characters in token names** | `semantic/color-light.json` — tokens like `primary​​`, `secondary​​`, `selected​` contain invisible Unicode characters (U+200B zero-width space) | Token references will break silently. CSS output will contain invisible characters in variable names. Cross-referencing between files will fail. |
| 2 | **Spaces in directory names** | `component / spacing / desktop.json` and `component / spacing / mobile.json` | Will cause issues with Style Dictionary glob patterns, shell scripts, and CI pipelines. Token Studio allows this but it's fragile outside that ecosystem. |

### High

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 3 | **Inconsistent naming convention between desktop and mobile** | Desktop uses camelCase (`cardGap`, `formGap`), mobile uses kebab-case (`in-between-cards`, `form`) | Tokens are not interchangeable between breakpoints. Cannot use theme switching for responsive tokens. |
| 4 | **Mobile tokens append `px` to reference values** | `component / spacing / mobile.json` — e.g. `"{core.dimension.600}px"` | Double unit in output (e.g. `24pxpx`). Style Dictionary will not resolve the reference correctly. |
| 5 | **Mobile missing button spacing tokens** | `component / spacing / mobile.json` has no `button.spacing` section | Incomplete responsive token coverage. Desktop buttons will have explicit padding, mobile will fall back to defaults or break. |
| 6 | **`display.medium` references dimension instead of font-size** | `semantic/typography.json` line 19 — `fontSize: "{core.dimension.1400}"` | Crosses concern boundaries. Should reference `{core.typography.font-size.*}` for consistency and correctness. The value resolves the same (56px) but the semantic intent is wrong. |

### Medium

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 7 | **Brand color namespace inconsistency** | `brand/color.json` stores tokens under `color.*` (no `core.` prefix), but `$themes.json` references them as `core.color.brand.*` | Potential confusion about which tier these belong to. The Figma variable references work because Token Studio resolves them, but it's semantically ambiguous. |
| 8 | **No dark theme** | Only `semantic/color-light.json` exists | No `color-dark` semantic set. Dark mode would need to be built from scratch. |
| 9 | **Disabled color naming** | `color.disabled.a`, `.b`, `.c` | Names don't communicate purpose. Should describe what they disable (e.g. `disabled.text`, `disabled.fill`, `disabled.border`). |
| 10 | **Icon size xlarge differs between breakpoints** | Desktop: `{core.dimension.800}` (32px), Mobile: `{core.dimension.600}` (24px, same as large) | May be intentional responsive behaviour, but mobile xlarge = mobile large is redundant. |

### Low

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 11 | **Line-height base value seems low** | `core.typography.line-height.100` = `16` (matches font-size base) | Results in `line-height: 16px` for a `16px` font, which is very tight (ratio 1.0). Typical body text needs ~1.4–1.5 ratio. The semantic typography tokens use `line-height.200` (24px) for body text, so it works in practice, but the naming is misleading — "100" implies a sensible default. |
| 12 | **Letter spacing as percentages** | Core letter-spacing uses `%` values (`"1%"`, `"-3%"`) | Token Studio handles this, but Style Dictionary's default transforms expect `em` or `px`. Will need a custom transform or the `sd-transforms` package to handle correctly. |

---

## Token Count Summary

| Tier | Set | Token Count |
|------|-----|-------------|
| Core | dimension | 17 |
| Core | typography | 49 |
| Core | modify | 21 |
| Core | border | 12 |
| Brand | color | 15 |
| Semantic | color-light | ~120+ |
| Semantic | typography | 17 |
| Semantic | border-radius | 16 |
| Semantic | border | 2 |
| Component | spacing/desktop | 14 |
| Component | spacing/mobile | 8 |
| **Total** | | **~290+** |
