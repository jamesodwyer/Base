---
name: figma-token-applicator
description: Apply design tokens to Figma components via Token Studio sharedPluginData only. Use when the user wants to bind tokens to Figma components, attach Token Studio metadata, or create missing component tokens for a Figma component. Triggers on "apply tokens to [component]", "bind tokens", "attach tokens", "Token Studio sharedPluginData", or "create component tokens for [name]".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, ToolSearch, mcp__plugin_figma_figma__use_figma, mcp__plugin_figma_figma__get_design_context, mcp__plugin_figma_figma__get_metadata, mcp__plugin_figma_figma__get_screenshot, mcp__jira__jira_create_issue
---

# Figma Token Applicator

Bind design tokens to Figma component variants using **Token Studio `sharedPluginData` only**. No Figma native variables, no variable collections, no `setBoundVariable`, no `setBoundVariableForPaint`.

---

## Critical Rules

1. **sharedPluginData ONLY.** The sole mechanism is `node.setSharedPluginData("tokens", key, value)`. Never create Figma variable collections. Never call `setBoundVariable` or `setBoundVariableForPaint`. Never call `figma.variables.createVariable` or `figma.variables.createVariableCollection`.
2. **Strip hardcoded fills AND clear variable bindings before applying tokens.** Set `node.fills = []` and `node.strokes = []` on every node before writing sharedPluginData. Also call `node.setBoundVariable(prop, null)` for every previously bound property — `fills`, `strokes`, `itemSpacing`, `paddingLeft/Right/Top/Bottom`, `topLeftRadius`/`topRightRadius`/`bottomLeftRadius`/`bottomRightRadius`, `strokeTopWeight`/`strokeBottomWeight`/`strokeLeftWeight`/`strokeRightWeight`. If you don't clear the variable binding, Figma keeps painting the previous variable value and Token Studio's sync gets overridden. Token Studio must be the sole source of every property — any residual hardcoded paint OR Figma variable binding will override token values after sync. Audit step before applying: `Object.keys(node.boundVariables || {})` should return `[]` after stripping.
3. **Correct file key.** Always extract the Figma file key from the user's URL. Never assume from memory.
4. **sharedPluginData format.** Each property is a separate key. Value is a JSON-stringified string of the dot-notation token path:
   ```javascript
   node.setSharedPluginData("tokens", "fill", JSON.stringify("color.interactive.primary.fill.hover"));
   node.setSharedPluginData("tokens", "borderColor", JSON.stringify("color.disabled.c"));
   // WRONG — single values key:
   // node.setSharedPluginData("tokens", "values", JSON.stringify({...}));
   ```
5. **State naming.** Use `default`/`hover`/`pressed`/`disabled`/`selected.default`/`selected.hover`/`selected.disabled`. Never `on`/`off`, never camelCase.
6. **No new semantic groups for components.** Component-specific tokens go in `tokens/component/{name}.json`, not in the semantic layer.
7. **Register new token sets.** When creating a new component token file, register it in Token Studio's `usedTokenSet` on the document root.
8. **Never apply tokens to — or strip fills from — child component instances.** If a parent component contains an instance of another GDS component (e.g. a Button or Icon inside an Alert Box), do not set any sharedPluginData on that instance or any of its children, and do not strip their fills or strokes. The child component owns its own token bindings — any overrides at the parent level create conflicts and drift. When writing strip + apply scripts, always exclude descendant nodes that are inside an INSTANCE whose name starts with 🟢. Pattern to exclude: `if (node.toString().includes("INSTANCE") || isInsideChildInstance(node)) continue;`. Only operate on nodes that are native to the component being worked on.
9. **Never use `verticalPadding` or `horizontalPadding` shorthand keys.** These shorthands cause Token Studio to display the resolved individual padding properties as "hexagon" (unresolved) entries in the Inspect panel, creating noise and confusion. Always use the four explicit keys: `paddingTop`, `paddingBottom`, `paddingLeft`, `paddingRight`. If you find these shorthands already applied to a component, replace them before moving on.
10. **Component token files contain colours only.** Named component files (e.g. `toast.json`, `stepper.json`) must only contain `$type: "color"` tokens. Spacing goes in `component/spacing/desktop.json`. borderRadius, borderWidth, shadow, typography, and icon sizes bind directly to semantic tokens in Figma — no component token needed for these.
11. **Always validate JSON after editing token files.** Run `python3 -c "import json; json.load(open('file.json'))"` after any edit. Removing a block can leave a trailing comma on the sibling above, making the file invalid. Token Studio reports this as "Failed to parse token file — invalid JSON format."
12. **Don't strip vector internals inside icon BOOLEAN_OPERATIONs.** Icon nodes in this design system are typed as `BOOLEAN_OPERATION` and their `sharedPluginData("tokens", "fill", ...)` is set on that boolean op itself. Their inner `Vector (Stroke)` / `Union` / `Exclude` children carry geometry-defining fills (often #000000, #121212, etc.) that are part of the vector path, not design system colour. Strip the fills/strokes on the BOOLEAN_OPERATION node only — leave its descendant vectors untouched. Pattern: `if (node.type === "BOOLEAN_OPERATION") { strip(node); /* do not recurse */ }`.
13. **Validation/feedback icon name varies by state.** Frames named `ErrorFilled` and `SuccessFilled` (and likely `WarningFilled`, `InfoFilled`) are sibling icons that swap by variant. When binding, look up by either name and pick the matching feedback token: `color.feedback.icon.error`, `color.feedback.icon.success`, `color.feedback.icon.warning`, `color.feedback.icon.info`. Don't hard-code one icon path across variants.
14. **When the geometry type must change, replace the node — don't mutate.** `node.type` is read-only; you cannot turn a `RECTANGLE` into an `ELLIPSE`. If the user wants a true circle (not a rectangle with `cornerRadius: 999`), create a fresh node with `figma.createEllipse()` (or the appropriate factory), copy width/height/x/y/constraints/strokeAlign, splice into the parent at the original index via `parent.insertChild(idx, newNode)`, set `fills = []` / `strokes = []` on the new node, apply the Token Studio bindings, then call `oldNode.remove()`. Replacement is cleaner than trying to clear every legacy variable binding off the old node.
15. **Match a borderRadius (or any primitive-resolving) token's resolved pixels to the node before binding.** Different semantic groups with the same suffix resolve to different values: `borderRadius.input.small` → 2px (via `core.border.radius.xSmall`), `borderRadius.container.small` → 4px (via `core.dimension.50`). Don't pick a group by category name — trace the alias chain end-to-end and confirm the pixel value matches `node.cornerRadius` / `node.strokeWeight` / etc. Same rule applies to `borderWidth`, `dimension`, and any other primitive-resolving token.

---

## Before You Start

You need:
1. A **Figma file key** — extract from the user's URL (e.g. `dfLpxHSoyojN9805EQXqy6`)
2. A **component set node ID** — extract from the URL or discover via `use_figma`
3. The **token JSON files** in `tokens/` (source of truth)

---

## Phase 1: Analyse Component & Resolve Tokens

### Step 1: Get the Figma component structure

Use `get_design_context` for a screenshot + code context, then use `use_figma` to explore the component set:
- List all variants (name, id)
- For each variant, list children (name, type, id, existing sharedPluginData)
- Note fills, strokes, and visual colours already present on each node

### Step 2: Read the token files

Identify which tokens cover this component:

| Tier | Location | Contains |
|------|----------|----------|
| Core | `tokens/core/color.json` | Brand colours, accents, neutrals |
| Global | `tokens/global/modify.json` | HSL modifier scale (0.05–1.0) |
| Global | `tokens/global/dimension.json` | 4px spacing scale |
| Global | `tokens/global/border.json` | Border radius + width primitives |
| Semantic | `tokens/semantic/colorLight.json` | Interactive, disabled, text, icon, border, elevation colours |
| Semantic | `tokens/semantic/borderRadius.json`, `border.json` | Semantic border tokens |
| Semantic | `tokens/semantic/typography.json` | Composite typography tokens |
| Component | `tokens/component/{name}.json` | Component-specific colour/spacing |

Trace every `{reference}` in `$value` fields to understand the alias chain. Resolve HSL modifiers (`$extensions.studio.tokens.modify`) using Python `colorsys` to verify the resolved hex matches the Figma node's current colour.

### Step 3: Map Figma states to token paths

For each variant, decide which token path maps to each visual property. Build a mapping table:

| Variant State | Node | Property Key | Token Path |
|---------------|------|-------------|------------|
| Unselected | wrapper | — | (no fill) |
| Unselected | pill | borderColor | `color.brand.02` |
| Hover | wrapper | fill | `color.interactive.primary.fill.hover` |
| Disabled | wrapper | fill | `color.disabled.a` |
| ... | ... | ... | ... |

Compare the resolved token hex with the Figma node's actual colour to confirm the mapping is correct. If a token resolves to a different colour than what's on the node, investigate before binding.

### Step 4: Identify missing tokens

If the component needs token paths that don't exist in any token file, these are **missing tokens**. Do NOT invent token paths that don't exist in the JSON files. Instead, proceed to Phase 1b.

---

## Phase 1b: Create Missing Component Tokens (if needed)

When a component needs tokens that don't exist at the semantic level — for example, a segmented toggle bar that uses `color.brand.02` for its selected fill instead of `color.interactive.primary.fill.default` — you have two options:

### Option A: Use existing semantic tokens directly

If the component's colours match existing semantic tokens (even if the conceptual mapping is slightly different), bind to the semantic token. Most components can be covered this way.

### Option B: Create a new component token file

If the component genuinely needs its own token paths (unique colour relationships, states that don't map to any semantic token), create a component token file:

1. **Create the token JSON** at `tokens/component/{componentName}.json` following DTCG format:
   ```json
   {
     "componentName": {
       "color": {
         "container": {
           "fill": {
             "default": {
               "$type": "color",
               "$value": "{color.interactive.primary.fill.default}",
               "$description": "Container fill in default state."
             }
           }
         }
       }
     }
   }
   ```

2. **Reference semantic tokens** — component tokens should alias semantic tokens, not core/brand directly. The alias chain is: Core → Brand → Semantic → Component.

3. **Register the token set** in the Figma file:
   ```javascript
   const current = JSON.parse(figma.root.getSharedPluginData("tokens", "usedTokenSet"));
   current["component/componentName"] = "enabled";
   figma.root.setSharedPluginData("tokens", "usedTokenSet", JSON.stringify(current));
   ```

4. **Create a JIRA Story** for missing tokens using `mcp__jira__jira_create_issue`:
   - `project_key`: `GDS`
   - `issue_type`: `Story`
   - `summary`: `[Tokens] Create {component} component tokens`
   - `description`: List the missing token paths, which tier they belong to, and why
   - `additional_fields`: `{ "parent": "GDS-419", "labels": ["design", "gds", "tokens", "new-token-request"] }`

### Spacing tokens

Component spacing tokens live in `tokens/component/spacing/desktop.json` and `mobile.json`. If the component's spacing values (padding, gap, minHeight) aren't covered there, note the gap but bind what you can.

---

## Phase 2: Bind Token Studio sharedPluginData

### Step 1: Apply bindings

For each variant, set sharedPluginData on the appropriate nodes. **Only set the data key — do not modify the node's visual properties (fills, strokes, etc.).**

```javascript
// Wrapper fill
wrapper.setSharedPluginData("tokens", "fill", JSON.stringify("color.interactive.primary.fill.hover"));

// Pill border
pill.setSharedPluginData("tokens", "borderColor", JSON.stringify("color.brand.02"));

// Text fill (on the TEXT node)
textNode.setSharedPluginData("tokens", "fill", JSON.stringify("color.text.inverse"));

// Icon fill (on the icon INSTANCE node)
iconInstance.setSharedPluginData("tokens", "fill", JSON.stringify("color.icon.inverse"));

// Typography (on the TEXT node — composite token path)
textNode.setSharedPluginData("tokens", "typography", JSON.stringify("typography.label.medium"));

// Spacing
pill.setSharedPluginData("tokens", "itemSpacing", JSON.stringify("button.spacing.medium.gap"));
pill.setSharedPluginData("tokens", "paddingTop", JSON.stringify("button.spacing.medium.blockPadding"));
pill.setSharedPluginData("tokens", "paddingBottom", JSON.stringify("button.spacing.medium.blockPadding"));
pill.setSharedPluginData("tokens", "paddingLeft", JSON.stringify("button.spacing.medium.inlinePadding"));
pill.setSharedPluginData("tokens", "paddingRight", JSON.stringify("button.spacing.medium.inlinePadding"));

// Border radius
node.setSharedPluginData("tokens", "borderRadius", JSON.stringify("borderRadius.interactive.medium"));

// Border width
node.setSharedPluginData("tokens", "borderWidth", JSON.stringify("border.interactive.default"));
```

### Token Studio key reference

| Figma Property | sharedPluginData Key |
|----------------|---------------------|
| fills (background) | `fill` |
| strokes (border colour) | `borderColor` |
| strokeWeight | `borderWidth` |
| corner radius | `borderRadius` |
| paddingTop / paddingBottom | `paddingTop` / `paddingBottom` |
| paddingLeft / paddingRight | `paddingLeft` / `paddingRight` |
| itemSpacing | `itemSpacing` |
| text fills | `fill` (on TEXT node) |
| composite typography | `typography` (on TEXT node) |

### Composite typography path mapping

When binding a text node's `typography` key, match the resolved fontSize/lineHeight/weight to a composite token in `tokens/semantic/typography.json`. Common mappings observed across components:

| fontSize / lineHeight / weight | Token path |
|-----|-----|
| 16 / 24 / Regular | `typography.body.regular.large` |
| 14 / 20 / Regular | `typography.body.regular.medium` |
| 12 / 20 / Regular | `typography.body.regular.small` |
| 16 / 20 / Semibold | `typography.label.large` |
| 14 / 20 / Semibold | `typography.label.medium` |
| 12 / 16 / Semibold | `typography.label.small` |

If a node uses `Bold` or `Black` instead of `Semibold`/`Regular`, look in `typography.body.bold.*`, `typography.heading.*`, `typography.title.*`, or `typography.display.*`.

### Step 2: Register new token sets (if created in Phase 1b)

```javascript
const current = JSON.parse(figma.root.getSharedPluginData("tokens", "usedTokenSet"));
current["component/newComponentName"] = "enabled";
figma.root.setSharedPluginData("tokens", "usedTokenSet", JSON.stringify(current));
```

### Step 3: Verify bindings

Read back all sharedPluginData to confirm:
```javascript
const keys = node.getSharedPluginDataKeys("tokens");
for (const key of keys) {
  console.log(key, node.getSharedPluginData("tokens", key));
}
```

Take a screenshot to confirm the visual appearance is unchanged.

---

## Working in Batches

Figma MCP calls have size limits. Process ~10–15 variants per `use_figma` call. Verify between batches with `get_screenshot`.

---

## HSL Modifier Resolution

Some semantic colour tokens have `$extensions.studio.tokens.modify` entries. Compute these in Python to verify the mapping between token and Figma colour:

```python
import colorsys

def darken_hsl(hex_color, amount):
    r, g, b = tuple(int(hex_color.lstrip("#")[i:i+2], 16)/255.0 for i in (0,2,4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = l * (1 - amount)
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return r2, g2, b2

def lighten_hsl(hex_color, amount):
    r, g, b = tuple(int(hex_color.lstrip("#")[i:i+2], 16)/255.0 for i in (0,2,4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = l + (1 - l) * amount
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return r2, g2, b2
```

Modifier amounts from `tokens/global/modify.json`: `modify.100` = 0.1, `modify.200` = 0.2, etc.

Use this to confirm that a token like `color.interactive.primary.fill.hover` (darken brand01 by 0.1) resolves to the same hex as the Figma node's current fill. If they don't match, the token mapping is wrong.

---

## Completed Components

All in file `dfLpxHSoyojN9805EQXqy6` unless noted.

- **Button** — 72 variants, 571 bindings. File: `WU01oSRfSHpOxUn3ThcvC5`, node: `29422:3597`
- **Accordion** — 24 variants. File: `cfzFFRdygJ3eEoHuDplxHO`, node: `36820:4228`
- **Alert Box** — 16 variants. File: `cfzFFRdygJ3eEoHuDplxHO`, node: `10410:52042`
- **Checkbox** — 13 variants. File: `cfzFFRdygJ3eEoHuDplxHO`, node: `41163:1815`
- **Radio Button** — 14 variants. Node: `21:28156`
- **Toggle** — 12 variants. Node: `21:28235`
- **FilterBar (.Toggler Bar/Block)** — 18 variants, 75 bindings. Node: `30:20751`
- **Toast** — 7 nodes bound. Page: `38852:11802`, node: `38852:13585`. Stripped 2026-05-06.
- **Pagination Button** — 4 nodes bound. Page: `30:20730`, node: `355:36072`. Stripped 2026-05-06.
- **Loading Spinner** — 35 nodes bound (9 variants × arc/trail/label + 4 base variants). Page: `33145:4265`, node: `33145:3778`. Stripped 2026-05-06.
- **Badge** — 37 variants, fully bound. Node: `21:25864`. Stripped 2026-05-06. Uses individual `paddingTop/Bottom/Left/Right` + `minHeight`. ⚠️ Fill tokens reference brand-level paths — semantic wrappers needed.
- **Input Field** — 9 variants (Default/Filled/Active/Hover/Disabled/Error/Success/Read Only/Focused), fully bound. Node: `355:37218`. Stripped 2026-05-07. Required clearing pre-existing Figma variable bindings (`boundVariables`) on Input frame's padding/radius/strokeWeight/itemSpacing/fills/strokes — not just stripping paints. Icon vectors inside BOOLEAN_OPERATIONs left untouched. Validation icon swaps `ErrorFilled` / `SuccessFilled` per state, bound to `color.feedback.icon.error` / `color.feedback.icon.success` accordingly.
- **Double Range Input** — Handle (5 states) + Slider track partly bound. Handle node: `40968:893` — replaced 5 dial RECTANGLES + 1 focus RECTANGLE with true ELLIPSEs (`figma.createEllipse()`), bound `fill`/`borderColor`/`borderWidth` to `doubleRangeInput.color.handle.*` and `border.interactive.xSmall`/`border.interactive.small`. Slider node: `40968:905` — Inactive track stripped (cleared 6 bound Figma variables: fills, height, 4 corner radii) and bound to `doubleRangeInput.color.track.fill.inactive` + `borderRadius.input.small` (resolves 2px). Active track is an INSTANCE — skipped. Token file: `tokens/component/doubleRangeInput.json`.
