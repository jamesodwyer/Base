---
name: figma-token-applicator
description: Apply W3C DTCG design tokens to Figma components via the Figma MCP. Use this skill whenever the user wants to apply tokens to Figma, bind variables to components, create Figma variables from token JSON, connect Token Studio tokens to Figma, or set up the variable alias chain in Figma. Also trigger when the user mentions "apply tokens to Badge/Checkbox/Stepper/etc", "create variables in Figma", "bind tokens to components", or "Token Studio sharedPluginData".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, ToolSearch, mcp__plugin_figma_figma__use_figma, mcp__plugin_figma_figma__get_design_context, mcp__plugin_figma_figma__get_metadata, mcp__plugin_figma_figma__get_screenshot
---

# Figma Token Applicator

Apply W3C DTCG design tokens to Figma components using the **Figma MCP `use_figma` tool** -- not a local Figma plugin.

The workflow sets Token Studio `sharedPluginData` on component variant layers with plain paint colours. It does **NOT** create Figma native variable collections or bind Figma variables -- Token Studio bindings are the only binding mechanism.

---

## Critical Rules

1. **Token Studio bindings only.** Set `sharedPluginData` with separate keys per property (`fill`, `borderColor`, etc.). Do NOT create Figma variable collections or use `setBoundVariableForPaint`.
2. **Correct file key.** Always extract the Figma file key from the user's URL. Never assume from memory -- the project has multiple files.
3. **State naming.** Use `default`/`hover`/`disabled`/`selected.default`/`selected.hover`/`selected.disabled` -- never `on`/`off`, never camelCase (`selectedHover`). In Token Studio JSON, dots become nested objects.
4. **No new semantic groups for components.** Component-specific tokens go in `tokens/component/{name}.json`. Only add to the semantic layer for genuinely cross-component concepts.
5. **Register new token sets.** When adding a new component token file, register it in Token Studio's `usedTokenSet` on the document root.
6. **sharedPluginData format.** Each property is a separate key (not a single `values` key). Value is a JSON-stringified string of the dot-notation token path.

---

## Before You Start

You need:
1. A **Figma file key** -- always extract from the user's URL (e.g. `dfLpxHSoyojN9805EQXqy6` from `figma.com/design/dfLpxHSoyojN9805EQXqy6/...`)
2. A **component set node ID** (e.g. `21:28235` for Toggle)
3. The **token JSON files** in `tokens/` (this project's source of truth)

If you don't have the file key, ask the user for the Figma URL. If you don't have the node ID, use `use_figma` to search for the component by name.

---

## The 3-Phase Workflow

### Phase 1: Resolve Tokens and Create Figma Variables

**Step 1: Identify which tokens the component needs.**

Read the component's token files. Components use tokens from multiple tiers:
- **Component tier**: `tokens/component/` -- spacing, layout (e.g. `button.spacing.medium.blockPadding`)
- **Semantic tier**: `tokens/semantic/colorLight.json` -- colors by variant/state (e.g. `color.interactive.primary.fill.default`)
- **Semantic tier**: `tokens/semantic/borderRadius.json`, `tokens/semantic/border.json` -- structural tokens
- **Semantic tier**: `tokens/semantic/typography.json` -- composite typography tokens (e.g. `typography.label.medium`)
- **Global tier**: `tokens/global/dimension.json`, `tokens/global/border.json` -- primitives referenced by semantic/component
- **Global tier**: `tokens/global/typography.json` -- font sizes, line heights, weights, letter spacing, font families
- **Core tier**: `tokens/core/color.json` -- brand colors, accents, neutrals

Trace every `{reference}` in `$value` fields to build the full dependency tree. A component token like `{core.dimension.200}` means you need the `core.dimension.200` global variable too.

**Step 1b: Resolve composite typography tokens.**

Typography tokens (`$type: "typography"`) are composite -- they bundle multiple sub-properties into one token. Figma has no composite typography variable type, so you must decompose them into individual variables.

For each typography token the component uses (e.g. `typography.label.medium` for button text):

1. Read `tokens/semantic/typography.json` to get the composite `$value` object
2. Resolve each sub-property reference against `tokens/global/typography.json`
3. Create **FLOAT variables** for `fontSize` and `lineHeight` (these can be variable-bound in Figma)
4. Note the `fontFamily`, `fontWeight`, `letterSpacing`, and `textCase` values -- these are set directly on the TEXT node, not via variables

**Typography variable naming convention:**
```
typography/{category}/{size}/fontSize    → aliases core/typography/fontSize/{scale}
typography/{category}/{size}/lineHeight  → aliases core/typography/lineHeight/{scale}
```

**Example: `typography.label.medium`**

| Sub-property | Token reference | Resolved value |
|---|---|---|
| fontFamily | `{core.typography.fontFamily.01}` | "Averta, sans-serif" |
| fontWeight | `{core.typography.fontWeight.semibold}` | 600 → Figma style "Semibold" |
| fontSize | `{core.typography.fontSize.100}` | 16 |
| lineHeight | `{core.typography.lineHeight.200}` | 24 |

**Global typography variables to create (in the Global collection):**
```
core/typography/fontSize/100  = 16  (FLOAT, base)
core/typography/fontSize/75   = 14  (FLOAT, 16 * 0.875)
core/typography/fontSize/150  = 18  (FLOAT, 16 * 1.125)
core/typography/lineHeight/100 = 16 (FLOAT, base)
core/typography/lineHeight/150 = 18 (FLOAT, 16 * 1.125)
core/typography/lineHeight/200 = 24 (FLOAT, 16 * 1.5)
core/typography/lineHeight/250 = 28 (FLOAT, 16 * 1.75)
```

Only create the specific scale values that your component's typography tokens reference -- you don't need every size in the scale.

**Semantic typography variables (in the Semantic collection):**
```
typography/label/medium/fontSize    → VARIABLE_ALIAS to core/typography/fontSize/100
typography/label/medium/lineHeight  → VARIABLE_ALIAS to core/typography/lineHeight/200
```

**Mapping fontWeight numbers to Figma font styles:**

| Token weight value | Figma fontName style |
|---|---|
| 300 | "Light" |
| 400 | "Regular" |
| 600 | "Semibold" |
| 700 | "Bold" |
| 900 | "Black" |

Note: Figma font style names are font-dependent. Averta uses "Semibold" (one word), but some fonts use "Semi Bold" (two words, e.g. Inter). Always check the font's available styles.

**Step 2: Compute HSL modifier values in Python.**

Some semantic color tokens have `$extensions.studio.tokens.modify` entries (darken, lighten, alpha). Figma can't do runtime HSL transforms, so you must precompute them.

Run the resolver script:

```bash
python3 figma-token-applicator/scripts/resolve_tokens.py --component button
```

Or compute inline. The algorithm is documented in `references/hsl-modifiers.md`. The key rules:
- Use Python's `colorsys.rgb_to_hls` / `colorsys.hls_to_rgb` (note: Python uses HLS order, not HSL)
- **darken**: `L = L * (1 - amount)`
- **lighten**: `L = L + (1 - L) * amount`
- **alpha**: set RGBA alpha to `amount` (no hue/saturation change)
- Modifier amounts come from `tokens/global/modify.json`: `modify.100` = 0.1, `modify.200` = 0.2, etc.

**Step 3: Create Figma Variables via MCP.**

Use `mcp__plugin_figma_figma__use_figma` to create variables. Critical rules:

**Maintain the alias chain.** Pure reference tokens (no modifier) must use `VARIABLE_ALIAS`:
```javascript
variable.setValueForMode(modeId, {
  type: "VARIABLE_ALIAS",
  id: parentVariable.id
});
```

Only tokens with HSL modifiers get flat computed RGB values. This is essential -- it means when `color.brand.01` changes, every semantic token referencing it updates automatically.

**Variable naming uses `/` separators** (Figma convention), not `.` (Token Studio convention):
- Figma: `color/brand/01`
- Token Studio: `color.brand.01`

**Organize variables into collections** matching the tier:
- `Global` collection: core dimensions, border primitives
- `Brand` collection: brand colors, accents, neutrals
- `Semantic` collection: interactive colors, border radius, border width
- `Component` collection: button spacing, badge spacing, etc.

**Create variables bottom-up** (Global first, then Brand, then Semantic, then Component) so parent variables exist before children reference them.

See `references/figma-variable-creation.md` for the full MCP code patterns and collection setup.

### Phase 2: Bind Variables to Component Variants

**Step 1: Get the component structure.**

Use `get_design_context` or `use_figma` to read the component set and understand its variant structure. Key things to identify:
- Variant property names (e.g. `Variant`, `State`, `IconPosition`, `isLoading`)
- Variant values (e.g. `Primary`, `Default`, `None`, `False`)
- Child node types and structure (TEXT nodes, INSTANCE nodes containing VECTORs)

**Step 2: Map token paths to variant properties.**

Build a mapping from variant combinations to token paths. For example, for Button:
- `Variant=Primary, State=Default` --> `color.interactive.primary.fill.default` (fill), `color.interactive.primary.text.default` (text)
- `Variant=Primary, State=Hover` --> `color.interactive.primary.fill.hover` (fill), `color.interactive.primary.text.hover` (text)

The semantic color tokens follow a consistent pattern: `color.interactive.{variant}.{property}.{state}` where:
- `{variant}` maps to the Figma variant name (primary, secondary, ghost, tertiary, inverse, transactional)
- `{property}` is fill, text, or border (icon color is handled at the icon component level -- see note below)
- `{state}` is default, hover, pressed, or disabled

**Step 3: Apply bindings to each variant node.**

For each variant, bind these properties (where tokens exist):

| Property | Figma API | Token Category |
|----------|-----------|----------------|
| **Fill** (background) | `setBoundVariableForPaint(fills[0], "color", variable)` | `color.interactive.{variant}.fill.{state}` |
| **Text color** | On TEXT child: `setBoundVariableForPaint(fills[0], "color", variable)` | `color.interactive.{variant}.text.{state}` |
| **Border color** | `setBoundVariableForPaint(strokes[0], "color", variable)` | `color.interactive.{variant}.border.{state}` |
| **Border radius** | `setBoundVariable("topLeftRadius", variable)` (all 4 corners) | `borderRadius.interactive.{size}` |
| **Border width** | `setBoundVariable("strokeWeight", variable)` | `border.interactive.{size}` |
| **Padding** | `setBoundVariable("paddingTop", variable)` etc. | `button.spacing.{size}.blockPadding` etc. |
| **Item spacing** | `setBoundVariable("itemSpacing", variable)` | `button.spacing.{size}.gap` |
| **Font** | On TEXT child: `loadFontAsync` + set `fontName` directly | `typography.{category}.{size}` → fontFamily + fontWeight |
| **Font size** | On TEXT child: `setBoundVariable("fontSize", variable)` | `typography/{category}/{size}/fontSize` |
| **Line height** | On TEXT child: `setBoundVariable("lineHeight", variable)` | `typography/{category}/{size}/lineHeight` |
| **Letter spacing** | On TEXT child: set `letterSpacing` directly | `typography.{category}.{size}` → letterSpacing (if present) |
| **Text case** | On TEXT child: set `textCase` directly | `typography.{category}.{size}` → textCase (if present) |

**Icons are tokenized at the icon component level, not the consuming component.** Icon components (e.g. ErrorFilled, ChevronLeft) own their color tokens on their vector/SVG nodes. When an icon instance is placed inside a component like Button or Alert Box, it carries its token with it. Do NOT override icon fills at the consuming component level — the icon color is controlled by the icon component itself, even when the color changes per variant or state. When processing a consuming component, skip all INSTANCE nodes that are icons; they are a separate component with their own token workflow.

**Plain paints only -- no variable binding.** Set fills and strokes as plain SolidPaint with the actual resolved hex colour. Do NOT use `setBoundVariableForPaint` or create Figma variable collections. Token Studio `sharedPluginData` is the only binding.

```javascript
// CORRECT: plain paint with actual resolved colour
node.fills = [figma.util.solidPaint(
  { r: 0.008, g: 0.302, b: 1.0 }, // actual #024dff
  { opacity: 1, visible: true }
)];
// Then set Token Studio data
node.setSharedPluginData("tokens", "fill", JSON.stringify("toggle.color.container.fill.selected.default"));

// WRONG: Figma variable binding (overrides Token Studio inspect)
// node.fills = [figma.variables.setBoundVariableForPaint(paint, "color", variable)];
```

**State naming convention.** Token states must follow the system-wide pattern:
- Default (unselected): `default`, `hover`, `disabled`
- Selected (active/on): `selected.default`, `selected.hover`, `selected.disabled`
- In Token Studio JSON, compound states use nested objects (dots become nesting):
```json
{
  "selected": {
    "default": { "$type": "color", "$value": "..." },
    "hover": { "$type": "color", "$value": "..." },
    "disabled": { "$type": "color", "$value": "..." }
  }
}
```
- Never use `on`/`off`, never use camelCase (`selectedHover`)

**Typography binding:** Typography tokens are composite (`$type: "typography"`) with sub-properties that must be applied individually to TEXT nodes. Figma doesn't support composite typography variables, so each sub-property is handled differently:

**Important: Clear existing Figma Text Styles first.** Components often have Figma Text Styles (e.g. "Desktop/Body - Rainier") applied to TEXT nodes. These are non-token references that conflict with token-driven typography. Before binding typography variables, clear any text style on the node:

```javascript
// Remove Figma Text Style so typography is purely token-driven
if (textNode.textStyleId && textNode.textStyleId !== "") {
  textNode.textStyleId = "";
}
```

Do this for every TEXT node in the component (excluding text inside nested component instances like Buttons — those have their own tokens). A good pattern is to sweep all text nodes after binding is complete:

```javascript
function clearTextStyles(node, skipInstances) {
  if (skipInstances && node.type === "INSTANCE") return;
  if (node.type === "TEXT" && node.textStyleId && node.textStyleId !== "") {
    node.textStyleId = "";
  }
  if ("children" in node && node.children) {
    for (const child of node.children) {
      clearTextStyles(child, skipInstances);
    }
  }
}
// Call on each variant, skipping nested component instances
clearTextStyles(variant, true);
```

**Step-by-step for each TEXT node:**

1. **Load the font** before changing any text properties:
```javascript
await figma.loadFontAsync({ family: "Averta", style: "Semibold" });
```

2. **Set fontName directly** (not a variable -- Figma has no font variable type):
```javascript
textNode.fontName = { family: "Averta", style: "Semibold" };
```

3. **Bind fontSize variable:**
```javascript
const fontSizeVar = variablesByName["typography/label/medium/fontSize"];
textNode.setBoundVariable("fontSize", fontSizeVar);
```

4. **Bind lineHeight variable:**
```javascript
const lineHeightVar = variablesByName["typography/label/medium/lineHeight"];
textNode.setBoundVariable("lineHeight", lineHeightVar);
```

5. **Set letterSpacing directly** (if the typography token includes it). Figma uses `{ value: number, unit: "PERCENT" | "PIXELS" }`:
```javascript
// Token value "-1.20%" → { value: -1.2, unit: "PERCENT" }
textNode.letterSpacing = { value: -1.2, unit: "PERCENT" };
```
Note: label typography tokens (used by buttons) have no letterSpacing, so skip this for buttons.

6. **Set textCase directly** (if the typography token includes it):
```javascript
// Token value "uppercase" → "UPPER"
textNode.textCase = "UPPER";
```
Mapping: `"uppercase"` → `"UPPER"`, `"lowercase"` → `"LOWER"`, `"capitalize"` → `"TITLE"`, `none` → `"ORIGINAL"`.
Note: label tokens don't have textCase; heading/title/caption tokens do.

**Complete typography binding example (button medium label):**
```javascript
const textNode = button.findOne(n => n.type === "TEXT");
await figma.loadFontAsync({ family: "Averta", style: "Semibold" });
textNode.fontName = { family: "Averta", style: "Semibold" };
textNode.setBoundVariable("fontSize", variablesByName["typography/label/medium/fontSize"]);
textNode.setBoundVariable("lineHeight", variablesByName["typography/label/medium/lineHeight"]);
```

**Common typography-to-component mapping:**

| Component | Size | Typography token | Font | Weight | Size | Line height |
|---|---|---|---|---|---|---|
| Button | large | `typography.label.large` | Averta | Semibold | 18 | 28 |
| Button | medium | `typography.label.medium` | Averta | Semibold | 16 | 24 |
| Button | small | `typography.label.small` | Averta | Semibold | 14 | 18 |
| Badge | -- | `typography.label.small` | Averta | Semibold | 14 | 18 |

**Typography sharedPluginData:** Set a single `typography` key on the TEXT node pointing to the composite token path. This tells Token Studio the node uses the full composite token, even though individual sub-properties are bound separately:
```javascript
textNode.setSharedPluginData("tokens", "typography", JSON.stringify("typography.label.medium"));
```
This is in addition to any `fill` sharedPluginData already set on the TEXT node for text color.

**Finding child nodes:**
- **Text**: find child with `type === "TEXT"`
- **Skip `isLoading=True` variants** entirely -- they have a spinner, not standard content
- **Exclude nested component instances** (icons, buttons, etc.): these are separate components with their own tokens. Only bind tokens to nodes that belong directly to this component. When traversing children to find TEXT nodes or apply bindings, skip INSTANCE nodes. Icons carry their own color tokens from the icon component level; buttons carry their own fill/text/spacing tokens.

See `references/figma-component-binding.md` for complete binding code patterns.

### Phase 3: Set Token Studio sharedPluginData

**This is the primary binding mechanism.** Token Studio metadata tells Token Studio which token path is applied to each layer.

**Step 1: Set sharedPluginData on each layer.**

Each property is a **separate key** on the node. The value is a JSON-stringified string of the dot-notation token path:

```javascript
// CORRECT: separate keys per property
node.setSharedPluginData("tokens", "fill", JSON.stringify("toggle.color.container.fill.default"));
node.setSharedPluginData("tokens", "borderColor", JSON.stringify("toggle.color.container.border.default"));

// WRONG: single values key (Token Studio won't read this)
node.setSharedPluginData("tokens", "values", JSON.stringify({ fill: "...", borderColor: "..." }));
```

When updating bindings, always clear existing keys first to avoid stale data:
```javascript
const existingKeys = node.getSharedPluginDataKeys("tokens");
for (const key of existingKeys) node.setSharedPluginData("tokens", key, "");
// Then set new keys
```

**Token Studio key mapping:**

| Figma Property | Token Studio Key |
|----------------|-----------------|
| fills (background) | `fill` |
| strokes (border color) | `borderColor` |
| strokeWeight | `borderWidth` |
| topLeftRadius etc. | `borderRadius` |
| paddingTop/Bottom | `verticalPadding` or `spacing` |
| paddingLeft/Right | `horizontalPadding` or `spacing` |
| itemSpacing | `itemSpacing` |
| text fills | `fill` (on the TEXT node) |
| fontSize | `fontSize` (on the TEXT node, via variable) |
| lineHeight | `lineHeight` (on the TEXT node, via variable) |
| typography composite | `typography` (on the TEXT node, covers fontFamily + fontWeight + fontSize + lineHeight) |

**Step 2: Register the token set in usedTokenSet.**

Token Studio only resolves paths for registered token sets. When adding a new component token file, register it:

```javascript
const current = JSON.parse(figma.root.getSharedPluginData("tokens", "usedTokenSet"));
current["component/toggle"] = "enabled";
figma.root.setSharedPluginData("tokens", "usedTokenSet", JSON.stringify(current));
```

**Step 3: Verify by reading back the data.**

Always verify bindings after applying by reading `getSharedPluginDataKeys` and checking the values match expectations. Inspect a sample of nodes from different variant states.

---

## Working in Batches

Figma MCP calls have size limits. Work in batches:

1. **Variables**: Create ~20-30 variables per `use_figma` call. Group by collection.
2. **Bindings**: Process ~5-10 variants per call. Each variant may need 6-8 bindings.
3. **Verify between batches**: Use `get_screenshot` to visually confirm bindings are rendering correctly before moving to the next batch.

---

## Component-Specific Notes

Each component has a unique variant structure. When starting a new component:

1. **Screenshot first**: Use `get_screenshot` to see the current component layout
2. **Read the variant structure**: Use `use_figma` with `figma.currentPage.findAll(n => n.type === "COMPONENT")` scoped to the component set
3. **Identify the token mapping pattern**: Check `tokens/semantic/colorLight.json` for the component's color tokens and `tokens/component/` for spacing
4. **Check for component-specific tokens**: Some components (Stepper, Badge) have their own token file in `tokens/component/`

### Completed Components
- **Button** -- 72 variants bound, 96 variables, 571 bindings. File: `WU01oSRfSHpOxUn3ThcvC5`, node: `29422:3597`
- **Accordion** -- 24 variants bound, 27 variables. File: `cfzFFRdygJ3eEoHuDplxHO`, node: `36820:4228`
- **Alert Box** -- 16 variants bound (4 statuses × 2 devices × nested/non-nested), 28 new variables. File: `cfzFFRdygJ3eEoHuDplxHO`, node: `10410:52042`
- **Checkbox (_CheckboxControl)** -- 13 variants bound, 22 new variables, 20 nodes with sharedPluginData. File: `cfzFFRdygJ3eEoHuDplxHO`, node: `41163:1815`
- **Radio Button** -- 14 variants bound, 53 variables (3 collections), 60 sharedPluginData entries. File: `dfLpxHSoyojN9805EQXqy6`, node: `21:28156`
- **Toggle** -- 12 variants (On/Off × Default/Hover/Disabled × Resale?), 26 layers bound via Token Studio sharedPluginData only (no Figma variables). Includes `presale` variant for Resale?=Yes using `color.interactive.presale`. File: `dfLpxHSoyojN9805EQXqy6`, node: `21:28235`

---

## Reference Files

- **references/hsl-modifiers.md** -- HSL modifier algorithm, Python implementation, edge cases
- **references/figma-variable-creation.md** -- MCP code patterns for creating variables and collections
- **references/figma-component-binding.md** -- MCP code patterns for binding variables to component properties
- **scripts/resolve_tokens.py** -- Python script to resolve full alias chain and compute modifier values
