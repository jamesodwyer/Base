# HSL Modifier Algorithm

Token Studio applies color modifiers (darken, lighten, alpha) using HSL color space. Figma has no runtime HSL transform capability, so all modifier values must be precomputed before creating Figma Variables.

## Token Format

Tokens with modifiers have this structure in the JSON:

```json
{
  "$extensions": {
    "studio.tokens": {
      "modify": {
        "type": "darken",        // "darken" | "lighten" | "alpha"
        "value": "{core.color.modify.100}",  // reference to modifier scale
        "space": "hsl"           // always "hsl" in this project
      }
    }
  },
  "$type": "color",
  "$value": "{color.interactive.primary.fill.default}"  // base color to modify
}
```

## Modifier Scale

The modifier amounts come from `tokens/global/modify.json`:

| Token | Resolved Value |
|-------|---------------|
| `core.color.modify.50` | 0.05 |
| `core.color.modify.100` | 0.1 |
| `core.color.modify.150` | 0.15 |
| `core.color.modify.200` | 0.2 |
| `core.color.modify.250` | 0.25 |
| `core.color.modify.300` | 0.3 |
| ... | pattern: value / 1000 |
| `core.color.modify.1000` | 1.0 |

The base value is `modify.100 = 0.1`. Others are multiples: `modify.200 = 0.1 * 2 = 0.2`.

## Algorithms

### Darken

Reduce lightness proportionally:
```
L_new = L * (1 - amount)
```

Example: `#024dff` (L=0.5) darkened by 0.1 --> `L = 0.5 * 0.9 = 0.45`

### Lighten

Increase lightness toward white:
```
L_new = L + (1 - L) * amount
```

Example: `#024dff` (L=0.5) lightened by 0.1 --> `L = 0.5 + 0.5 * 0.1 = 0.55`

### Alpha

Set the opacity (no hue/saturation change):
```
opacity = amount
```

The RGB values stay the same; only the alpha channel changes.

## Python Implementation

Python's `colorsys` module uses **HLS** order (Hue, Lightness, Saturation), not HSL. Be careful with argument order.

```python
import colorsys

def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    """Convert #RRGGBB to (r, g, b) floats 0-1."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return (r, g, b)

def rgb_to_hex(r: float, g: float, b: float) -> str:
    """Convert (r, g, b) floats 0-1 to #RRGGBB."""
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def apply_modifier(
    base_hex: str,
    modifier_type: str,
    amount: float
) -> tuple[str, float]:
    """
    Apply a Token Studio modifier to a color.
    
    Returns (hex_color, opacity).
    For darken/lighten, opacity is 1.0.
    For alpha, hex is unchanged and opacity is the amount.
    """
    r, g, b = hex_to_rgb(base_hex)
    
    if modifier_type == "alpha":
        return (base_hex, amount)
    
    # Python colorsys: rgb_to_hls returns (h, l, s) -- note L before S
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    
    if modifier_type == "darken":
        l = l * (1 - amount)
    elif modifier_type == "lighten":
        l = l + (1 - l) * amount
    
    # Clamp
    l = max(0.0, min(1.0, l))
    
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return (rgb_to_hex(r2, g2, b2), 1.0)
```

## Resolving the Chain

To compute the final color for a modified token:

1. Resolve `$value` to find the base color (may be an alias like `{color.brand.01}`)
2. Follow the alias chain until you reach a concrete hex value
3. Resolve `modify.value` to get the numeric amount (e.g., `{core.color.modify.100}` --> 0.1)
4. Apply the modifier function
5. The result is what gets stored as the Figma Variable value (since we can't alias + modify)

## Edge Cases

- **Chained modifiers**: A token could reference another token that also has a modifier. Resolve the inner modifier first, then apply the outer one.
- **Alpha + darken/lighten**: These don't combine in a single token in this project, but if they did, apply darken/lighten first, then alpha.
- **White/black base**: Darken on white or lighten on black works correctly with the formulas above.
