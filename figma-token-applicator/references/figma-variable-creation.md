# Figma Variable Creation Patterns

All variable creation happens via `mcp__plugin_figma_figma__use_figma`. Each call executes JavaScript in the Figma plugin sandbox.

## Creating Collections

Create one collection per tier. Collections are created once and reused across components.

```javascript
// Check if collection exists first
const collections = await figma.variables.getLocalVariableCollectionsAsync();
let globalCollection = collections.find(c => c.name === "Global");
if (!globalCollection) {
  globalCollection = figma.variables.createVariableCollection("Global");
}
const modeId = globalCollection.modes[0].modeId;
```

Collections to create:
- **Global** -- core dimensions, border radius/width primitives
- **Brand** -- brand colors, accents, neutrals, common colors
- **Semantic** -- interactive colors, semantic borders, elevation, feedback, input, focus, text, icon, disabled
- **Component** -- per-component spacing (button, badge, etc.)

## Creating Variables

### Simple value (Global/Brand tier)

```javascript
const variable = figma.variables.createVariable(
  "core/dimension/100",  // name uses / separator
  globalCollection,
  "FLOAT"                // FLOAT for dimensions, COLOR for colors
);
variable.setValueForMode(modeId, 4); // raw numeric value
```

For colors:
```javascript
const variable = figma.variables.createVariable(
  "color/brand/01",
  brandCollection,
  "COLOR"
);
variable.setValueForMode(modeId, { r: 0.008, g: 0.302, b: 1.0, a: 1.0 });
```

Color values use 0-1 floats, not 0-255. Convert: `r = hexValue / 255`.

### Alias reference (Semantic/Component tier)

For tokens that are pure references (no modifier), maintain the alias chain:

```javascript
// First, find the parent variable
const allVars = await figma.variables.getLocalVariablesAsync();
const parentVar = allVars.find(v => v.name === "color/brand/01");

const semanticVar = figma.variables.createVariable(
  "color/interactive/primary/fill/default",
  semanticCollection,
  "COLOR"
);
semanticVar.setValueForMode(modeId, {
  type: "VARIABLE_ALIAS",
  id: parentVar.id
});
```

This is critical -- it preserves the design token hierarchy. When brand.01 changes, all semantic tokens update automatically.

### Computed value (tokens with HSL modifiers)

For tokens with `$extensions.studio.tokens.modify`, the value is precomputed in Python and stored as a flat RGB:

```javascript
// color.interactive.primary.fill.hover = darken(brand.01, 0.1)
// Precomputed: #024dff darkened 10% = #0245e6
const variable = figma.variables.createVariable(
  "color/interactive/primary/fill/hover",
  semanticCollection,
  "COLOR"
);
variable.setValueForMode(modeId, { r: 0.008, g: 0.271, b: 0.902, a: 1.0 });
```

These cannot use VARIABLE_ALIAS because Figma doesn't support runtime color transforms.

## Batch Pattern

Create variables in batches of ~20-30 per MCP call. Group by collection to minimize lookups.

```javascript
// Batch: create all Global dimension variables
const collections = await figma.variables.getLocalVariableCollectionsAsync();
let globalColl = collections.find(c => c.name === "Global");
if (!globalColl) {
  globalColl = figma.variables.createVariableCollection("Global");
}
const modeId = globalColl.modes[0].modeId;

const dims = [
  ["core/dimension/100", 4],
  ["core/dimension/200", 8],
  ["core/dimension/300", 12],
  // ... more
];

const created = [];
for (const [name, value] of dims) {
  const v = figma.variables.createVariable(name, globalColl, "FLOAT");
  v.setValueForMode(modeId, value);
  created.push(v.name);
}
return { created };
```

## Avoiding Duplicates

Before creating variables, check if they already exist:

```javascript
const existing = await figma.variables.getLocalVariablesAsync();
const existingNames = new Set(existing.map(v => v.name));

// Only create if not already present
if (!existingNames.has("core/dimension/100")) {
  // create it
}
```

This is especially important when running the skill on a second component -- many Global/Brand/Semantic variables will already exist from the first run.

## Typography Variables

Typography tokens are composite (`$type: "typography"`), but Figma only supports FLOAT variables for individual text properties. Create FLOAT variables for `fontSize` and `lineHeight`, then bind them individually. Font family and weight are set directly on the text node.

### Global tier (primitives)

```javascript
// Font size base
const fontSizeVar = figma.variables.createVariable(
  "core/typography/fontSize/100",
  globalColl,
  "FLOAT"
);
fontSizeVar.setValueForMode(modeId, 16); // base font size
fontSizeVar.scopes = ["FONT_SIZE"];

// Line height
const lineHeightVar = figma.variables.createVariable(
  "core/typography/lineHeight/200",
  globalColl,
  "FLOAT"
);
lineHeightVar.setValueForMode(modeId, 24); // 16 * 1.5
lineHeightVar.scopes = ["LINE_HEIGHT"];
```

### Semantic tier (composite sub-property aliases)

Name semantic typography variables as `typography/{category}/{size}/{property}`:

```javascript
// typography.label.medium → fontSize aliases to core/typography/fontSize/100
const labelFontSize = figma.variables.createVariable(
  "typography/label/medium/fontSize",
  semanticColl,
  "FLOAT"
);
labelFontSize.setValueForMode(semModeId, {
  type: "VARIABLE_ALIAS",
  id: fontSizeVar.id
});
labelFontSize.scopes = ["FONT_SIZE"];

// typography.label.medium → lineHeight aliases to core/typography/lineHeight/200
const labelLineHeight = figma.variables.createVariable(
  "typography/label/medium/lineHeight",
  semanticColl,
  "FLOAT"
);
labelLineHeight.setValueForMode(semModeId, {
  type: "VARIABLE_ALIAS",
  id: lineHeightVar.id
});
labelLineHeight.scopes = ["LINE_HEIGHT"];
```

### Resolving typography values from token JSON

Composite typography tokens reference global primitives with expressions:

| Token Reference | Resolution |
|----------------|------------|
| `{core.typography.fontSize.100}` | 16 (base) |
| `{core.typography.fontSize.100}*0.875` | 14 (fontSize.75) |
| `{core.typography.fontSize.100}*1.125` | 18 (fontSize.150) |
| `{core.typography.lineHeight.100}` | 16 (base) |
| `{core.typography.lineHeight.100}*1.5` | 24 (lineHeight.200) |

Evaluate expressions in Python before creating the Figma variable.

## Variable Scoping

After creating variables, set their scoping so they appear in the right Figma UI contexts:

```javascript
// Color variables: show in fill and stroke pickers
variable.scopes = ["FRAME_FILL", "SHAPE_FILL", "STROKE_COLOR", "TEXT_FILL"];

// Dimension variables: show in gap, padding, sizing
variable.scopes = ["GAP", "WIDTH_HEIGHT"];

// Border radius: show in corner radius
variable.scopes = ["CORNER_RADIUS"];

// Border width: show in stroke width
variable.scopes = ["STROKE_FLOAT"];

// Font size: show in font size picker
variable.scopes = ["FONT_SIZE"];

// Line height: show in line height picker
variable.scopes = ["LINE_HEIGHT"];
```
