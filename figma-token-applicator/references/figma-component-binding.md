# Figma Component Binding Patterns

After creating variables, bind them to component variants. All binding happens via `mcp__plugin_figma_figma__use_figma`.

## Reading the Component Structure

First, understand the component set:

```javascript
const componentSet = await figma.getNodeByIdAsync("29422:3597");
// componentSet.type === "COMPONENT_SET"

const variants = componentSet.children; // array of COMPONENT nodes
// Each variant has a name like:
// "Variant=Primary, State=Default, IconPosition=None, isLoading=False"

// Parse variant properties
for (const variant of variants) {
  const props = {};
  variant.name.split(", ").forEach(pair => {
    const [key, value] = pair.split("=");
    props[key] = value;
  });
  // props = { Variant: "Primary", State: "Default", IconPosition: "None", isLoading: "False" }
}
```

## Binding Fill (Background Color)

```javascript
const allVars = await figma.variables.getLocalVariablesAsync();
const fillVar = allVars.find(v => v.name === "color/interactive/primary/fill/default");

// Use the actual resolved color in the base paint
const paint = {
  type: "SOLID",
  color: { r: 0.008, g: 0.302, b: 1.0 }, // actual hex of the variable
  opacity: 1.0,
  visible: true
};

const boundPaint = figma.variables.setBoundVariableForPaint(paint, "color", fillVar);
variant.fills = [boundPaint];
```

Never use `{r:0, g:0, b:0}` as the base paint color. Always use the actual resolved hex. Figma sometimes renders the base color instead of the variable value.

## Binding Text Color

Find the TEXT child node and bind its fill:

```javascript
const textNode = variant.children.find(c => c.type === "TEXT");
if (textNode) {
  const textVar = allVars.find(v => v.name === "color/interactive/primary/text/default");
  const paint = {
    type: "SOLID",
    color: { r: 1.0, g: 1.0, b: 1.0 }, // actual resolved color
    opacity: 1.0,
    visible: true
  };
  const boundPaint = figma.variables.setBoundVariableForPaint(paint, "color", textVar);
  textNode.fills = [boundPaint];
}
```

## Binding Icon Color

Icons are nested inside INSTANCE nodes. Drill through the hierarchy:

```javascript
function findIconVector(node) {
  // Look for INSTANCE children (excluding Loading Spinner)
  for (const child of node.children) {
    if (child.type === "INSTANCE" && !child.name.includes("Loading Spinner")) {
      // Drill into the instance to find the VECTOR
      return findDeepestVector(child);
    }
    if (child.type === "FRAME") {
      const result = findIconVector(child);
      if (result) return result;
    }
  }
  return null;
}

function findDeepestVector(node) {
  if (node.type === "VECTOR") return node;
  if (node.children) {
    for (const child of node.children) {
      const result = findDeepestVector(child);
      if (result) return result;
    }
  }
  return null;
}

const iconVector = findIconVector(variant);
if (iconVector) {
  const iconVar = allVars.find(v => v.name === "color/interactive/primary/icon/default");
  const paint = {
    type: "SOLID",
    color: { r: 1.0, g: 1.0, b: 1.0 },
    opacity: 1.0,
    visible: true
  };
  iconVector.fills = [figma.variables.setBoundVariableForPaint(paint, "color", iconVar)];
}
```

## Binding Border Color (Stroke)

```javascript
const borderVar = allVars.find(v => v.name === "color/interactive/secondary/border/default");
const strokePaint = {
  type: "SOLID",
  color: { r: 0.008, g: 0.302, b: 1.0 },
  opacity: 1.0,
  visible: true
};
variant.strokes = [figma.variables.setBoundVariableForPaint(strokePaint, "color", borderVar)];
```

## Binding Numeric Properties

Border radius, border width, padding, and spacing use `setBoundVariable`:

```javascript
// Border radius (all 4 corners)
const radiusVar = allVars.find(v => v.name === "borderRadius/interactive/medium");
variant.setBoundVariable("topLeftRadius", radiusVar);
variant.setBoundVariable("topRightRadius", radiusVar);
variant.setBoundVariable("bottomLeftRadius", radiusVar);
variant.setBoundVariable("bottomRightRadius", radiusVar);

// Border width
const widthVar = allVars.find(v => v.name === "border/interactive/default");
variant.setBoundVariable("strokeWeight", widthVar);

// Padding
const blockPadVar = allVars.find(v => v.name === "button/spacing/medium/blockPadding");
variant.setBoundVariable("paddingTop", blockPadVar);
variant.setBoundVariable("paddingBottom", blockPadVar);

const inlinePadVar = allVars.find(v => v.name === "button/spacing/medium/inlinePadding");
variant.setBoundVariable("paddingLeft", inlinePadVar);
variant.setBoundVariable("paddingRight", inlinePadVar);

// Item spacing (gap between children)
const gapVar = allVars.find(v => v.name === "button/spacing/medium/gap");
variant.setBoundVariable("itemSpacing", gapVar);
```

## Binding Typography

Typography tokens are composite, so bind sub-properties individually. Font family and weight must be set directly (not variable-bound).

```javascript
const textNode = variant.children.find(c => c.type === "TEXT");
if (textNode) {
  const allVars = await figma.variables.getLocalVariablesAsync();

  // 1. Bind fontSize variable
  const fontSizeVar = allVars.find(v => v.name === "typography/label/medium/fontSize");
  if (fontSizeVar) {
    textNode.setBoundVariable("fontSize", fontSizeVar);
  }

  // 2. Bind lineHeight variable (must set a fixed value first, not AUTO)
  const lineHeightVar = allVars.find(v => v.name === "typography/label/medium/lineHeight");
  if (lineHeightVar) {
    textNode.lineHeight = { value: 24, unit: "PIXELS" }; // resolved value
    textNode.setBoundVariable("lineHeight", lineHeightVar);
  }

  // 3. Set fontName directly (family + weight from the composite token)
  // Try the token font first, fall back to alternatives
  try {
    await figma.loadFontAsync({ family: "Averta", style: "Semibold" });
    textNode.fontName = { family: "Averta", style: "Semibold" };
  } catch (e) {
    // Font not available - try common fallback or keep existing
    console.log(`Averta not available: ${e.message}`);
  }

  // 4. Set Token Studio sharedPluginData for the composite token
  textNode.setSharedPluginData("tokens", "typography",
    JSON.stringify("typography.label.medium")
  );
}
```

**Font weight mapping** (Token Studio weight → Figma style name):

| Token Weight | Figma Style |
|-------------|-------------|
| 300 (light) | "Light" |
| 400 (regular) | "Regular" |
| 600 (semibold) | "Semibold" or "Semi Bold" |
| 700 (bold) | "Bold" |
| 900 (black) | "Black" |

Note: Figma font style names vary by font family. Always try the expected style, then common alternatives. Use `figma.loadFontAsync` before setting `fontName`.

**Typography token → component mapping:**

| Component | Typography Token |
|-----------|-----------------|
| Button (large) | `typography.label.large` |
| Button (medium) | `typography.label.medium` |
| Button (small) | `typography.label.small` |
| Body text | `typography.body.regular.medium` |
| Heading | `typography.heading.{size}` |

## Setting Token Studio sharedPluginData

After every binding, set the Token Studio metadata:

```javascript
// Fill binding
variant.setSharedPluginData("tokens", "fill",
  JSON.stringify("color.interactive.primary.fill.default")
);

// Text fill (on the TEXT node)
textNode.setSharedPluginData("tokens", "fill",
  JSON.stringify("color.interactive.primary.text.default")
);

// Border color
variant.setSharedPluginData("tokens", "borderColor",
  JSON.stringify("color.interactive.secondary.border.default")
);

// Border radius
variant.setSharedPluginData("tokens", "borderRadius",
  JSON.stringify("borderRadius.interactive.medium")
);

// Border width
variant.setSharedPluginData("tokens", "borderWidth",
  JSON.stringify("border.interactive.default")
);

// Spacing (Token Studio uses a JSON object for padding)
variant.setSharedPluginData("tokens", "spacing",
  JSON.stringify("button.spacing.medium.blockPadding")
);

// Item spacing
variant.setSharedPluginData("tokens", "itemSpacing",
  JSON.stringify("button.spacing.medium.gap")
);

// Typography (on the TEXT node, using the composite token path)
textNode.setSharedPluginData("tokens", "typography",
  JSON.stringify("typography.label.medium")
);
```

Note the `.` dot-notation for Token Studio paths (not `/`).

## Batch Binding Pattern

Process 5-10 variants per MCP call:

```javascript
const componentSet = await figma.getNodeByIdAsync("29422:3597");
const allVars = await figma.variables.getLocalVariablesAsync();

// Build a lookup map for fast variable access
const varMap = {};
for (const v of allVars) { varMap[v.name] = v; }

// Process a batch of variants
const targetVariants = componentSet.children.filter(c => {
  const name = c.name;
  // Filter to specific variant + state combinations
  return name.includes("Variant=Primary") &&
         name.includes("isLoading=False") &&
         (name.includes("State=Default") || name.includes("State=Hover"));
});

const results = [];
for (const variant of targetVariants) {
  const props = {};
  variant.name.split(", ").forEach(pair => {
    const [k, v] = pair.split("=");
    props[k] = v;
  });

  const state = props.State.toLowerCase(); // "default", "hover", etc.
  const variantType = props.Variant.toLowerCase(); // "primary", etc.

  // Bind fill
  const fillVarName = `color/interactive/${variantType}/fill/${state}`;
  const fillVar = varMap[fillVarName];
  if (fillVar) {
    // ... apply binding as shown above
  }

  results.push({ variant: variant.name, bound: true });
}
return results;
```

## Skipping Variants

Skip these variants entirely:
- **isLoading=True**: These have a Loading Spinner replacing standard content. The spinner has its own bindings that are handled separately.
- **Variants without matching tokens**: If a variant combination doesn't have corresponding tokens, skip it and flag it for the user.
