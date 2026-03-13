# Figma Integration Guide

This document explains how to inspect Figma components to understand actual token usage, ensuring descriptions are based on real implementation rather than naming assumptions.

---

## Why Figma Integration Matters

**Critical insight**: Token names don't always reflect actual usage.

### Example: The Tertiary Button Misconception

**Token name**: `color.interactive.tertiary.*`

**Name assumption**: "For tertiary priority buttons"

**Actual Figma usage**: Ghost buttons in cards and banner close buttons

**Correct description**: "Use for ghost buttons. Cards/banners."

### Key Principle

> **Descriptions must be grounded in real component usage, never solely on token naming conventions.**

Without Figma inspection, descriptions risk being:
- Misleading (wrong component types)
- Too generic ("for interactive elements")
- Missing context (where it's actually used)

---

## Figma MCP Tools Overview

The Figma MCP server provides tools for inspecting design files and extracting component usage data.

### Loading Figma MCP Tools

```javascript
// Use ToolSearch to load Figma MCP tools
ToolSearch({query: "figma"})

// Key tools you'll need:
// - figma_get_variables: Get all design variables/tokens
// - figma_get_component_details: Inspect component structure
// - figma_get_file_data: Get file structure and components
```

### Required Information

Before starting Figma integration:
1. **Figma file URL** or **file key** (from the URL: `figma.com/file/{FILE_KEY}/...`)
2. **Access permissions** to the design file
3. **Variable collection names** (usually matches token.json structure)

---

## Figma Inspection Workflow

### Step 1: Get Variable List

**Goal**: Understand what variables exist in Figma and their IDs

```javascript
// Pseudo-code for getting variables
const variables = await figma_get_variables({
  fileKey: "ABC123...",
  collectionName: "TM1 - Color" // Or null for all collections
});

// Result structure:
{
  "variables": [
    {
      "id": "VariableID:123:456",
      "name": "color/interactive/primary/fill/default",
      "resolvedType": "COLOR",
      "valuesByMode": {
        "light": { "r": 0.2, "g": 0.4, "b": 1.0, "a": 1.0 },
        "dark": { "r": 0.3, "g": 0.5, "b": 1.0, "a": 1.0 }
      }
    }
  ]
}
```

### Step 2: Map Variable Names to Token Paths

**Goal**: Connect Figma variable names to your tokens.json structure

```javascript
// Variable naming in Figma may use different separators
// Figma: "color/interactive/primary/fill/default"
// tokens.json: "color.interactive.primary.fill.default"

function mapVariableToToken(figmaVarName) {
  // Convert Figma slashes to dots
  return figmaVarName.replace(/\//g, '.');
}
```

### Step 3: Find Components Using Variables

**Goal**: Identify which components bind to which variables

```javascript
// Get component details
const component = await figma_get_component_details({
  fileKey: "ABC123...",
  nodeId: "1:234" // Component node ID
});

// Look for boundVariables in the response
// This shows which layers use which variables

// Example result:
{
  "name": "Button",
  "type": "COMPONENT",
  "children": [
    {
      "name": "Container",
      "type": "RECTANGLE",
      "fills": [
        {
          "type": "SOLID",
          "boundVariables": {
            "color": {
              "type": "VARIABLE_ALIAS",
              "id": "VariableID:123:456" // maps to interactive.primary.fill
            }
          }
        }
      ]
    },
    {
      "name": "Label",
      "type": "TEXT",
      "boundVariables": {
        "characters": { ... },
        "fills": {
          "color": {
            "id": "VariableID:123:789" // maps to interactive.primary.text
          }
        }
      }
    }
  ]
}
```

### Step 4: Extract Component Variants

**Goal**: Understand different states and sizes

```javascript
// Components often have variants (size, state, type)
// Example: "Button" component with variants:
// - Size: Small, Medium, Large
// - Type: Solid, Outline, Ghost
// - State: Default, Hover, Pressed, Disabled

// Each variant may use different variables
// Example mappings:
{
  "Button/Size=Medium, Type=Solid, State=Default": {
    "fill": "color.interactive.primary.fill.default",
    "text": "color.interactive.primary.text.default",
    "icon": "color.interactive.primary.icon.default"
  },
  "Button/Size=Medium, Type=Solid, State=Hover": {
    "fill": "color.interactive.primary.fill.hover",
    "text": "color.interactive.primary.text.hover",
    "icon": "color.interactive.primary.icon.hover"
  },
  "Button/Size=Medium, Type=Outline, State=Default": {
    "fill": "color.interactive.secondary.fill.default",
    "text": "color.interactive.secondary.text.default",
    "border": "color.interactive.secondary.border.default"
  }
}
```

### Step 5: Build Component-to-Token Mapping

**Goal**: Create a reference of which tokens are used where

```markdown
## Button Component Analysis

### Solid Button (Primary)
**Variants inspected**: 51 total
**Token usage**:
- Container fill: `color.interactive.primary.fill.*`
- Text fill: `color.interactive.primary.text.*`
- Icon fill: `color.interactive.primary.icon.*`
- Border: `color.interactive.primary.border.*`
- Padding (vertical): `core.dimension.300`
- Padding (horizontal): `core.dimension.400`
- Border radius: `border-radius.interactive.m`

### Outline Button (Secondary)
**Token usage**:
- Container fill: `color.interactive.secondary.fill.*` (subtle/transparent)
- Text fill: `color.interactive.secondary.text.*`
- Border: `color.interactive.secondary.border.*` (KEY visual indicator)
- Icon fill: `color.interactive.secondary.icon.*`

### Ghost Button (Tertiary)
**Used in**: Card action buttons, Banner close buttons
**Token usage**:
- Container fill: `color.interactive.tertiary.fill.*`
- Text fill: `color.interactive.tertiary.text.*`
- Icon fill: `color.interactive.tertiary.icon.*`
```

### Step 6: Document Findings

**Goal**: Record insights for description generation

```markdown
# FIGMA-TOKEN-USAGE-MAPPING.md

## Interactive Primary Tokens

**Components**: Button (Solid variant), Card primary actions

| Token | Usage in Figma |
|-------|----------------|
| `color/interactive/primary/fill/default` | Solid button backgrounds (default state) |
| `color/interactive/primary/fill/hover` | Solid button backgrounds (hover state) |
| `color/interactive/primary/text/default` | Text color on solid buttons (default) |

**Description pattern**: "Use for solid buttons. [Context]."
```

---

## Real-World Example: Button Analysis

### Initial State (Before Figma Inspection)

**Tokens**:
- `color.interactive.primary.*`
- `color.interactive.secondary.*`
- `color.interactive.tertiary.*`

**Initial descriptions (name-based)**:
- "Primary button colors"
- "Secondary button colors"
- "Tertiary button colors"

**Problem**: Vague, doesn't explain visual difference

---

### After Figma Inspection

**Discovered in Figma**:
1. **"Primary" buttons** → Solid filled backgrounds (high emphasis)
2. **"Secondary" buttons** → Outlined with border (medium emphasis)
3. **"Tertiary" buttons** → Ghost/minimal style, used in cards and banners (low emphasis)

**Updated descriptions (Figma-informed)**:
- `interactive.primary.fill.default`: "Use for solid buttons. Primary CTAs."
- `interactive.secondary.fill.default`: "Use for outline buttons. Secondary actions."
- `interactive.tertiary.fill.default`: "Use for ghost buttons. Cards/banners."

**Impact**: Designers now know:
- Visual style (solid vs outline vs ghost)
- Usage context (CTAs, secondary actions, cards/banners)
- Actual component names from library

---

## Handling Tokens Without Figma Context

**Problem**: Some tokens may not (yet) be implemented in Figma components.

### Two-Step Approach

1. **Generate provisional description** based on naming pattern
2. **Review with user** using AskUserQuestion tool

**Example workflow**:

```javascript
// Token: semantic.color.interactive.control.fill.default
// No Figma component bindings found

// Step 1: Generate provisional description
const provisionalDescription = "Use for control fills. Toggles/checkboxes.";

// Step 2: Present to user for review
AskUserQuestion({
  questions: [{
    question: "This token lacks Figma component usage data. The provisional description is: '" + provisionalDescription + "'. Would you like to change this? If so, what should it be and why?",
    header: "Review Token",
    options: [
      {
        label: "Keep provisional description",
        description: "The generated description is accurate"
      },
      {
        label: "Change description",
        description: "Provide corrected description based on actual usage"
      }
    ]
  }]
});

// Step 3: Document user reasoning
// If user changes it, record in FIGMA-TOKEN-USAGE-MAPPING.md:
// - Token: semantic.color.interactive.control.fill.default
// - Provisional: "Use for control fills. Toggles/checkboxes."
// - User correction: "Use for checkbox backgrounds. Form controls."
// - Reasoning: "This token is only used for checkboxes, not toggles"
```

### Documentation Structure for Unmatched Tokens

```markdown
## Tokens Without Figma Context

### semantic.color.interactive.control.fill.default

**Provisional description**: "Use for control fills. Toggles/checkboxes."

**User review**: Changed

**Corrected description**: "Use for checkbox backgrounds. Form controls."

**Reasoning**: This token is only used for checkboxes in the codebase, not toggle switches. Toggles use a different token.

**Action**: Update TOKEN-DESCRIPTIONS.md pattern library with this insight.
```

---

## Component Types to Inspect

### Priority 1: High-Usage Components

1. **Button** (solid, outline, ghost variants)
   - Focus on: Fill, text, icon, border for all states
   - States: Default, hover, pressed, disabled
   - Sizes: Small, medium, large

2. **Input Fields** (text input, textarea, select)
   - Focus on: Fill, border, text, placeholder, icon
   - States: Default, hover, focus, error, success, disabled

3. **Feedback Components** (banner, alert, toast)
   - Focus on: Fill, border, icon, text for each type
   - Types: Error, success, warning, info

### Priority 2: Common UI Elements

4. **Card** (container, surface)
   - Focus on: Surface, border, elevation
   - Variants: Default, raised, sunken

5. **Badge/Tag** (status indicators)
   - Focus on: Fill, text
   - Types: Draft, published, archived, etc.

### Priority 3: Specialized Components

6. **Table** (data grids)
   - Focus on: Column headers, cell fills, borders
   - States: Default, hover, selected, highlighted

7. **Navigation** (tabs, menus)
   - Focus on: Fill, text, border, selected states

---

## Variable Binding Types in Figma

### 1. Fill Bindings

```javascript
// Solid color fill bound to variable
{
  "fills": [{
    "type": "SOLID",
    "boundVariables": {
      "color": {
        "type": "VARIABLE_ALIAS",
        "id": "VariableID:123:456"
      }
    }
  }]
}
```

**Usage**: Button backgrounds, container fills, icon colors

---

### 2. Text Bindings

```javascript
// Text color bound to variable
{
  "fills": [{
    "type": "SOLID",
    "boundVariables": {
      "color": {
        "type": "VARIABLE_ALIAS",
        "id": "VariableID:789:012"
      }
    }
  }]
}
```

**Usage**: Text labels, button text, placeholders

---

### 3. Stroke/Border Bindings

```javascript
// Border color bound to variable
{
  "strokes": [{
    "type": "SOLID",
    "boundVariables": {
      "color": {
        "type": "VARIABLE_ALIAS",
        "id": "VariableID:345:678"
      }
    }
  }]
}
```

**Usage**: Input borders, button outlines, dividers

---

### 4. Effect Bindings (Shadows)

```javascript
// Shadow effect bound to variable
{
  "effects": [{
    "type": "DROP_SHADOW",
    "boundVariables": {
      "color": {
        "type": "VARIABLE_ALIAS",
        "id": "VariableID:901:234"
      }
    }
  }]
}
```

**Usage**: Elevation shadows, focus rings

---

## Automation Pseudo-Code

### Complete Figma Inspection Flow

```python
async def inspect_figma_for_token_usage(figma_file_key, token_path):
    """
    Inspect Figma file to find actual usage of a token.
    Returns component names and usage contexts.
    """

    # Step 1: Get variable ID from token path
    variables = await figma_get_variables(figma_file_key)
    token_var_name = token_path.replace('.', '/')
    variable = find_variable_by_name(variables, token_var_name)

    if not variable:
        return {"found": False, "reason": "Variable not found in Figma"}

    variable_id = variable['id']

    # Step 2: Get all components in file
    file_data = await figma_get_file_data(figma_file_key)
    components = extract_components(file_data)

    # Step 3: Find components using this variable
    usage_list = []

    for component in components:
        # Get detailed component data
        details = await figma_get_component_details(
            figma_file_key,
            component['id']
        )

        # Recursively search for variable bindings
        bindings = find_variable_bindings(details, variable_id)

        if bindings:
            usage_list.append({
                "component": component['name'],
                "layer": bindings['layer_name'],
                "property": bindings['property'],  # fill, stroke, text
                "variant": component.get('variant')
            })

    # Step 4: Extract component names and contexts
    if usage_list:
        component_names = list(set([u['component'] for u in usage_list]))
        contexts = infer_contexts_from_names(component_names)

        return {
            "found": True,
            "components": component_names,
            "contexts": contexts,
            "usage_details": usage_list
        }
    else:
        return {
            "found": False,
            "reason": "Variable exists but not bound to any components"
        }


def find_variable_bindings(node, variable_id, layer_path=""):
    """
    Recursively search node tree for variable bindings.
    """
    bindings = []

    # Check fills
    if 'fills' in node:
        for fill in node['fills']:
            if 'boundVariables' in fill:
                if fill['boundVariables'].get('color', {}).get('id') == variable_id:
                    bindings.append({
                        "layer_name": node['name'],
                        "property": "fill",
                        "layer_path": layer_path
                    })

    # Check strokes
    if 'strokes' in node:
        for stroke in node['strokes']:
            if 'boundVariables' in stroke:
                if stroke['boundVariables'].get('color', {}).get('id') == variable_id:
                    bindings.append({
                        "layer_name": node['name'],
                        "property": "stroke",
                        "layer_path": layer_path
                    })

    # Check effects (shadows)
    if 'effects' in node:
        for effect in node['effects']:
            if 'boundVariables' in effect:
                if effect['boundVariables'].get('color', {}).get('id') == variable_id:
                    bindings.append({
                        "layer_name": node['name'],
                        "property": "effect",
                        "layer_path": layer_path
                    })

    # Recursively check children
    if 'children' in node:
        for child in node['children']:
            child_bindings = find_variable_bindings(
                child,
                variable_id,
                f"{layer_path}/{node['name']}"
            )
            bindings.extend(child_bindings)

    return bindings


def infer_contexts_from_names(component_names):
    """
    Infer usage contexts from component names.
    """
    contexts = []

    # Map component names to contexts
    context_map = {
        "Button": "CTAs",
        "Card": "Cards",
        "Banner": "Banners",
        "Input": "Text fields",
        "TextField": "Inputs",
        "Badge": "Status indicators",
        "Table": "Tables",
        "Modal": "Modals",
        "Dialog": "Dialogs"
    }

    for component in component_names:
        for key, context in context_map.items():
            if key.lower() in component.lower():
                contexts.append(context)

    return list(set(contexts))
```

---

## Integration Checklist

When inspecting Figma for token usage:

- [ ] Load Figma MCP tools using ToolSearch
- [ ] Get Figma file key from user
- [ ] Retrieve all variables from file
- [ ] Map variable names to token paths
- [ ] For each token, find component bindings
- [ ] Extract component names and variant info
- [ ] Identify usage contexts (cards, buttons, inputs, etc.)
- [ ] Document findings in FIGMA-TOKEN-USAGE-MAPPING.md
- [ ] For tokens without bindings:
  - [ ] Generate provisional description
  - [ ] Review with user
  - [ ] Document user reasoning
- [ ] Use findings to inform description generation

---

## Output Format

After Figma inspection, create a mapping document:

```markdown
# Figma Component Token Usage Mapping

> **Source**: Inspected {FIGMA_FILE_NAME} on {DATE}
> **Components analyzed**: {COUNT} components

## Token: color.interactive.primary.fill.default

**Components using this token**:
- Button (Solid variant) - Container fill layer
- Card (Action button) - Background fill

**Usage contexts**: Primary CTAs, High-emphasis actions

**Description**: "Use for solid buttons. Primary CTAs."

---

## Token: color.interactive.tertiary.fill.default

**Components using this token**:
- Card (Action button - Ghost variant) - Container fill
- Banner (Close button) - Background fill

**Usage contexts**: Cards, Banners, Minimal actions

**Description**: "Use for ghost buttons. Cards/banners."

---

## Tokens Without Figma Bindings

### color.interactive.control.fill.default

**Status**: Not found in Figma components

**Provisional description**: "Use for control fills. Toggles/checkboxes."

**User review**: Changed to "Use for checkbox backgrounds. Form controls."

**Reasoning**: Token only used in checkbox component in codebase, not toggle switches.
```

---

## Key Takeaways

1. **Always inspect Figma** before finalizing semantic/component token descriptions
2. **Token names can be misleading** - verify actual usage
3. **Document component mappings** for future reference and maintenance
4. **Handle missing context gracefully** - use provisional descriptions + user review
5. **Record user reasoning** when Figma context is unavailable - it captures domain knowledge

---

## Next Steps

After completing Figma inspection:
1. Use findings to generate descriptions (see `description-templates.md`)
2. Validate descriptions against Figma usage
3. Create FIGMA-TOKEN-USAGE-MAPPING.md document
4. Update TOKEN-DESCRIPTIONS.md with new patterns learned
5. Run validation checks to ensure quality
