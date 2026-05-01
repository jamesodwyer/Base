# Figma Component Binding Patterns

Bind tokens to Figma component variants using **Token Studio `sharedPluginData` only**. No Figma variables, no variable collections, no `setBoundVariable`, no `setBoundVariableForPaint`.

## The Only Binding Mechanism

```javascript
node.setSharedPluginData("tokens", "fill", JSON.stringify("color.interactive.primary.fill.default"));
```

That's it. Set the key, set the value. Do not touch `node.fills`, `node.strokes`, or any other visual property.

## Reading the Component Structure

```javascript
const componentSet = figma.getNodeById("30:20751");

for (const variant of componentSet.children) {
  // Parse variant properties from name
  const props = {};
  variant.name.split(", ").forEach(pair => {
    const [key, value] = pair.split("=");
    props[key] = value;
  });

  // Explore children
  for (const child of variant.children) {
    console.log(child.id, child.name, child.type);
    // Check existing bindings
    const keys = child.getSharedPluginDataKeys("tokens");
    for (const k of keys) {
      console.log(`  ${k} = ${child.getSharedPluginData("tokens", k)}`);
    }
  }
}
```

## Setting Bindings by Property

### Fill (background colour)

```javascript
wrapper.setSharedPluginData("tokens", "fill",
  JSON.stringify("color.interactive.primary.fill.hover")
);
```

### Border colour (stroke)

```javascript
node.setSharedPluginData("tokens", "borderColor",
  JSON.stringify("color.brand.02")
);
```

### Text colour

On the TEXT child node:
```javascript
textNode.setSharedPluginData("tokens", "fill",
  JSON.stringify("color.text.inverse")
);
```

### Icon colour

On the icon INSTANCE node (not the vector inside it):
```javascript
iconInstance.setSharedPluginData("tokens", "fill",
  JSON.stringify("color.icon.inverse")
);
```

### Typography (composite)

On the TEXT node — a single key for the composite token:
```javascript
textNode.setSharedPluginData("tokens", "typography",
  JSON.stringify("typography.label.medium")
);
```

### Spacing

```javascript
pill.setSharedPluginData("tokens", "paddingTop", JSON.stringify("button.spacing.medium.blockPadding"));
pill.setSharedPluginData("tokens", "paddingBottom", JSON.stringify("button.spacing.medium.blockPadding"));
pill.setSharedPluginData("tokens", "paddingLeft", JSON.stringify("button.spacing.medium.inlinePadding"));
pill.setSharedPluginData("tokens", "paddingRight", JSON.stringify("button.spacing.medium.inlinePadding"));
pill.setSharedPluginData("tokens", "itemSpacing", JSON.stringify("button.spacing.medium.gap"));
```

### Border radius and width

```javascript
node.setSharedPluginData("tokens", "borderRadius", JSON.stringify("borderRadius.interactive.medium"));
node.setSharedPluginData("tokens", "borderWidth", JSON.stringify("border.interactive.default"));
```

## Key Reference

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

## Clearing Existing Bindings

Always clear stale keys before setting new ones:
```javascript
const existingKeys = node.getSharedPluginDataKeys("tokens");
for (const key of existingKeys) {
  node.setSharedPluginData("tokens", key, "");
}
```

## Registering New Token Sets

When creating a new component token file (e.g. `tokens/component/toggleBar.json`), register it:
```javascript
const current = JSON.parse(figma.root.getSharedPluginData("tokens", "usedTokenSet"));
current["component/toggleBar"] = "enabled";
figma.root.setSharedPluginData("tokens", "usedTokenSet", JSON.stringify(current));
```

## Batch Binding Pattern

Process 10–15 variants per MCP call:
```javascript
const componentSet = figma.getNodeById("30:20751");
const results = [];

for (const variant of componentSet.children) {
  const props = {};
  variant.name.split(", ").forEach(pair => {
    const [k, v] = pair.split("=");
    props[k] = v;
  });

  // Map state to tokens and apply
  const state = props.State;
  if (state === "Hover") {
    variant.setSharedPluginData("tokens", "fill",
      JSON.stringify("color.interactive.primary.fill.hover"));
  }

  // Find and bind children
  if (variant.children) {
    for (const child of variant.children) {
      if (child.type === "TEXT" || child.name === "Text") {
        child.setSharedPluginData("tokens", "fill",
          JSON.stringify("color.text.inverse"));
      }
    }
  }

  results.push({ id: variant.id, name: variant.name });
}
return JSON.stringify(results);
```

## Skipping Variants

- **isLoading=True**: Spinner replaces standard content. Skip.
- **Variants without matching tokens**: Flag for the user, don't invent token paths.
