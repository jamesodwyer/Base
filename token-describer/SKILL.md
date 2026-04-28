---
name: token-describer
description: Use when generating, updating, or reviewing $description fields on design tokens. Trigger on any of these: "generate descriptions", "describe tokens", "add descriptions", "document tokens", "token descriptions", "$description fields", "description quality", "describe these tokens", "what should the descriptions say". Also trigger proactively when working with token JSON files that have missing or empty $description fields — even if the user hasn't explicitly asked for descriptions.
version: 2.0.0
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, ToolSearch, AskUserQuestion
---

# Token Description Generator

Generate concise, Figma-informed `$description` fields for design tokens. Descriptions must be grounded in **real component usage**, not just token naming conventions.

Token names can mislead. Example: `interactive.tertiary.*` sounds like "tertiary priority buttons" but is actually ghost buttons in cards and banner close buttons. Always verify against Figma or user knowledge before assuming.

---

## Quick Start

1. **Find the token files** — look for `tokens/` directory or ask the user for the path
2. **Analyse coverage** — count tokens with/without `$description`, report by tier
3. **Ask about Figma** — if the user has a Figma file URL, use it for component context (see `references/figma-integration.md`)
4. **Generate descriptions** — run the generator script or generate inline
5. **Review with user** — batch-present tokens that need human judgement
6. **Validate** — run the validation script
7. **Optionally offer** git branching, PR creation, or documentation generation

---

## Generating Descriptions

### Automated (preferred)

```bash
# Safe mode — only adds descriptions where missing
python3 token-describer/scripts/generate_descriptions.py

# Overwrite existing descriptions with generated ones
python3 token-describer/scripts/generate_descriptions.py --force

# Preview changes without modifying files
python3 token-describer/scripts/generate_descriptions.py --dry-run
```

### Manual / Inline

When generating descriptions directly (without the script), follow these rules:

**Match tone to the token's tier and stability:**

| Tone | When to use | Example |
|------|-------------|---------|
| **Declarative** | Core primitives with self-evident purpose | `"Medium corner radius."` |
| **Factual** | Stable semantic tokens, 1-2 component uses | `"Use for solid buttons. Primary CTAs."` |
| **Directive** | Tokens with a specific, constrained job | `"Use for placeholder text. Inputs."` |
| **Observational** | Tokens serving 3+ contexts or evolving | `"Commonly used for body text, small titles, and helper text."` |
| **Behavioral** | Mode-dependent or state-dependent tokens | `"Text that inverts with mode. Light on dark, dark on light."` |

Use "Commonly used for" only when a token genuinely serves 3+ distinct purposes. When the relationship is definitional (the token IS for that component), say so directly.

**Tier patterns:**
- **Core**: Declarative identity. `"Base spacing unit. Foundation for scale."`
- **Brand**: Keep existing brand descriptions or use factual identity. `"Primary brand color. Main actions and links."`
- **Semantic**: Choose tone by stability and breadth. Default states get directive ("Use for..."), interaction states get factual ("{Component} {property} {state}.")
- **Component**: Factual relationship. `"Block padding for medium buttons."`

**State language** (be consistent):
- Hover: "on hover"
- Pressed: "when pressed"
- Disabled: "when disabled"
- Focus: "on focus"
- Active: "when active"

**Hard rules:**
- 20-60 characters (target 20-50)
- Never mention units (px, pt, rem, dp)
- Never mention platforms (iOS, Android, Web) — "mobile"/"desktop" viewport contexts are fine
- Semantic/component tokens should mention actual components where known

See `references/description-templates.md` for the complete pattern library and `references/token-patterns.md` for tier identification.

---

## User Review (Batch Workflow)

Not every token needs human review. Use confidence tiers:

### Auto-approve (no review needed)
- **Core tokens**: Pattern-matched with high confidence (dimension, typography, border, modify)
- **Brand tokens**: Usually already have good descriptions or map cleanly from names
- **Tokens that already have a description** (unless `--force` is used)

### Batch review (present groups together)
- **Semantic tokens without Figma context**: Group by category (all `input.*` together, all `feedback.*` together, etc.) and present the group for approval
- **Component tokens**: Group by component

Present batch reviews like this:

```
## Input tokens (6 tokens)

| Token | Generated Description | OK? |
|-------|----------------------|-----|
| color.input.fill.default | Use for input backgrounds. Text fields. | |
| color.input.fill.hover | Input background on hover. | |
| color.input.border.default | Use for input borders. Text fields. | |
| ... | ... | |

Are these accurate? Any corrections?
```

### Flag individually (only for genuinely ambiguous tokens)
- Tokens where the name is misleading or the usage is unclear
- Tokens that serve multiple components and you're unsure which to mention
- New token categories not covered by existing patterns

When a user corrects a description, save the correction to `overrides.json` so it persists across regeneration runs. Document the reasoning — it captures domain knowledge.

---

## Validation

```bash
# Single file
python3 token-describer/scripts/validate_descriptions.py path/to/tokens.json

# All token files
python3 token-describer/scripts/validate_descriptions.py --dir tokens/

# With Figma mapping context
python3 token-describer/scripts/validate_descriptions.py --dir tokens/ \
  --figma-mapping FIGMA-TOKEN-USAGE-MAPPING.md
```

**Checks**: length (20-50 chars), no unit refs, no platform refs, component mentions for semantic/component tokens, duplicate description detection, Figma context documentation.

Fix all errors before committing. Warnings are worth reviewing but not blocking.

---

## Figma Integration

When a Figma file is available, use it to verify token usage before generating descriptions. This prevents misleading descriptions based on token names alone.

Read `references/figma-integration.md` for the full workflow: loading MCP tools, extracting variables, mapping to token paths, finding component bindings, and documenting findings.

The key output is a component-to-token mapping that feeds into description generation. Store this in `FIGMA-TOKEN-USAGE-MAPPING.md`.

---

## Documentation (Optional)

After generating descriptions, **ask the user** if they want supporting documentation. Don't generate it by default. Available docs:

| File | Content |
|------|---------|
| TOKEN-DESCRIPTIONS.md | Patterns by tier, decision-making process |
| TOKEN-USAGE.md | Decision tree for token selection, common scenarios |
| FIGMA-TOKEN-USAGE-MAPPING.md | Component-to-token mapping from Figma inspection |
| TOKEN-ARCHITECTURE.md | Tier architecture, naming conventions |

Only create what the user asks for.

---

## Key Design Decisions

1. **Figma-first**: Real component usage is the source of truth, not token names
2. **Override system**: User corrections in `overrides.json` always take priority over generated descriptions
3. **Batch review over one-by-one**: Group related tokens for efficient human review
4. **Validate before commit**: Always run validation before finalising changes
5. **Safe by default**: The generator never overwrites existing descriptions unless `--force` is passed

---

## Reference Files

- **references/description-templates.md**: Complete pattern library for all token types
- **references/token-patterns.md**: Tier identification, naming conventions, path patterns
- **references/figma-integration.md**: Figma MCP workflow for component inspection
- **examples/**: Sample token files with descriptions (core, semantic, component)
- **scripts/validate_descriptions.py**: Automated quality validation
- **scripts/generate_descriptions.py**: Pattern-based description generator
