# Design Tokens Project

## Overview

This project manages the design token pipeline for migrating from a legacy token structure to a new standardised structure. Tokens are authored in **Token Studio** (stored as JSON), transformed via **Style Dictionary** with the `@tokens-studio/sd-transforms` plugin, and output as Storybook-ready coded tokens (CSS, SCSS, JS).

## Architecture

```
Token Studio (Figma plugin)
    ↓ JSON tokens (synced via Git)
tokens/             ← canonical token source (new structure)
    ↓ Style Dictionary + sd-transforms
build/              ← generated outputs (CSS, SCSS, JS, JSON)
    ↓
Storybook / Application
```

## Directory Structure

- `tokens/` — New token structure (Token Studio JSON format). This is the source of truth.
- `resources/current-tokens/` — Snapshot of the current/legacy tokens for migration reference.
- `resources/definitions/` — Token definitions, naming conventions, and reference documentation.
- `resources/new-token-structure/` — Reference material for the target token structure.
- `build/` — Generated output from Style Dictionary (gitignored).
- `migration/` — Migration documentation: mapping old → new, decisions, progress tracking.
- `scripts/` — Custom build scripts, migration helpers, token validation.

## Key Commands

- `npm run build` — Build all platforms (CSS, SCSS, JS)
- `npm run clean` — Remove generated build output

## Current Token State

The tokens in `tokens/` are the **current Token Studio tokens** (not yet migrated). They are synced from Token Studio in Figma but **not yet attached to any Figma components**. The coded counterpart is being built separately.

### Token Sets (11 files, ~290+ tokens)

| Tier | Set | Tokens | Description |
|------|-----|--------|-------------|
| Core | `core/dimension` | 17 | 4px base spacing scale (50–3200 + zero) |
| Core | `core/typography` | 49 | Font family (Averta), weights, sizes, line-heights, letter-spacing |
| Core | `core/modify` | 21 | Color modification multipliers (0–1.0) for darken/lighten/alpha |
| Core | `core/border` | 12 | Border radius (xsmall–full) and width (xsmall–xlarge) |
| Brand | `brand/color` | 15 | Brand (#024ddf, #121212), 8 accents, 5 neutrals, black/white |
| Semantic | `semantic/color-light` | ~120+ | Interactive states, feedback, elevation, input, disabled, focus, text, icon, border |
| Semantic | `semantic/typography` | 17 | Composite typography: display, heading, title, label, body, caption |
| Semantic | `semantic/border-radius` | 16 | Interactive, input, container, popover radius tokens |
| Semantic | `semantic/border` | 2 | Interactive border widths |
| Semantic | `semantic/icon` | 4 | Shared icon sizes (small–xLarge) |
| Component | `component/spacing/desktop` | Spacing-only | Layout spacing, badge/selectionControl/button spacing (desktop) |
| Component | `component/spacing/mobile` | Spacing-only | Layout spacing, badge spacing (mobile, no button tokens) |

### Known Issues (see `migration/TOKEN-AUDIT.md` for full details)

- **Critical**: Zero-width Unicode characters in color-light token names (`primary​​`, `selected​`)
- **Critical**: Spaces in directory names (`component / spacing /`)
- **High**: Desktop/mobile naming inconsistency (camelCase vs kebab-case)
- **High**: Mobile tokens append `px` to references, causing double-unit output
- **High**: Mobile missing button spacing tokens
- **Medium**: No dark theme variant exists yet
- **Medium**: Disabled colors use opaque names (`a`, `b`, `c`)

## Migration Context

- **Source**: Current tokens in Token Studio (stored in GitHub, JSON format).
- **Target**: New token structure, moving to GitLab.
- **Toolchain**: Token Studio → Style Dictionary (with @tokens-studio/sd-transforms) → coded tokens.
- Tokens are NOT yet attached to Figma components — Token Studio only at this stage.
- The `resources/` folder contains reference material — current tokens and definitions uploaded by the team.

## Working Conventions

- Token files in `tokens/` use Token Studio JSON format (DTCG-compatible: `$type`, `$value`).
- Style Dictionary config lives at the project root: `style-dictionary.config.json`.
- All generated files go to `build/` and should never be manually edited.
- Migration decisions and mappings are documented in `migration/`.
- Color transforms use Token Studio's `$extensions.studio.tokens.modify` (darken, lighten, alpha, mix in HSL/LCH).
- **Component spacing files (`component/spacing/`) must only contain spacing tokens** (padding, gap, minHeight, layout dimension gaps). Non-spacing tokens (color, borderRadius, borderWidth, size) are handled by the semantic layer or dedicated component files — never in the spacing sets.
- **Use `gap` not `inBetween`** for spacing between elements. This applies everywhere: component tokens, framework docs, and tooling.
