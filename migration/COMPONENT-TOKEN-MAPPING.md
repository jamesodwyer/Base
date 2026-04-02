# Component-to-Token Mapping

> Maps each GDS atom component to the v2 design tokens that should be applied in Figma.
>
> **Legend:**
> - Token paths use the new v2 naming from `tokens/semantic/` and `tokens/component/`
> - "Legacy" column shows the current hardcoded value or GDS colour name for reference
> - States are listed per-property where applicable

---

## 1. Button

### Colour Tokens

| Property | State | v2 Token | Legacy (TM) |
|----------|-------|----------|-------------|
| Fill | Default | `color.interactive.primary.fill.default` | Neptune `#024DDF` |
| Fill | Hover | `color.interactive.primary.fill.hover` | `#0141B8` |
| Fill | Pressed | `color.interactive.primary.fill.pressed` | `#033399` |
| Fill | Disabled | `color.interactive.primary.fill.disabled` | Ammonite `#D6D6D6` |
| Text | Default | `color.interactive.primary.text.default` | Spotlight `#FFFFFF` |
| Text | Disabled | `color.interactive.primary.text.disabled` | Slate `#949494` |
| Icon | Default | `color.interactive.primary.icon.default` | Spotlight `#FFFFFF` |
| Icon | Disabled | `color.interactive.primary.icon.disabled` | Slate `#949494` |

**Secondary variant:**

| Property | State | v2 Token | Legacy (TM) |
|----------|-------|----------|-------------|
| Fill | Default | `color.interactive.secondary.fill.default` | Transparent |
| Fill | Hover | `color.interactive.secondary.fill.hover` | Neptune bg |
| Fill | Pressed | `color.interactive.secondary.fill.pressed` | Darker Neptune |
| Border | Default | `color.interactive.secondary.border.default` | Neptune `#024DDF` |
| Border | Hover | `color.interactive.secondary.border.hover` | Darker Neptune |
| Text | Default | `color.interactive.secondary.text.default` | Neptune `#024DDF` |
| Text | Hover | `color.interactive.secondary.text.hover` | Spotlight `#FFFFFF` |

**Tertiary variant:**

| Property | State | v2 Token | Legacy (TM) |
|----------|-------|----------|-------------|
| Fill | Default | `color.interactive.tertiary.fill.default` | Transparent |
| Fill | Hover | `color.interactive.tertiary.fill.hover` | Neptune bg |
| Border | Default | `color.interactive.tertiary.border.default` | Cosmos `#121212` |
| Text | Default | `color.interactive.tertiary.text.default` | Cosmos `#121212` |

**Ghost variant:**

| Property | State | v2 Token | Legacy (TM) |
|----------|-------|----------|-------------|
| Fill | Default | Transparent (no token) | Transparent |
| Fill | Hover | `color.interactive.ghost.fill.hover` | Neptune bg |
| Text | Default | `color.interactive.ghost.text.default` | Cosmos `#121212` |
| Icon | Default | `color.interactive.ghost.icon.default` | Cosmos `#121212` |

**Transaction variant:**

| Property | State | v2 Token | Legacy (TM) |
|----------|-------|----------|-------------|
| Fill | Default | `color.interactive.transaction.fill.default` | Earth `#01A469` |
| Fill | Hover | `color.interactive.transaction.fill.hover` | `#018A57` |
| Fill | Pressed | `color.interactive.transaction.fill.pressed` | `#016B45` |
| Text | Default | `color.interactive.transaction.text.default` | Spotlight `#FFFFFF` |

**Disabled (all variants):**

| Property | State | v2 Token | Legacy (TM) |
|----------|-------|----------|-------------|
| Fill | Disabled | `color.disabled.b` | Ammonite `#D6D6D6` |
| Text | Disabled | `color.disabled.a` | Slate `#949494` |
| Border | Disabled | `color.disabled.c` | — |

**Focus:**

| Property | v2 Token | Legacy (TM) |
|----------|----------|-------------|
| Focus ring | `color.focus.border` | Neptune `#024DDF` 2px |

### Spacing Tokens

| Property | v2 Token | Legacy (TM) |
|----------|----------|-------------|
| Horizontal padding | `button.spacing.large.horizontalPadding` | Auditorium 16px |
| Vertical padding | `button.spacing.large.verticalPadding` | 10px |
| Icon gap | `layout.spacing.interactiveGap` | Club 8px |

### Border Tokens

| Property | v2 Token | Legacy (TM) |
|----------|----------|-------------|
| Border radius | `border-radius.interactive.small` | 4px |
| Border width (secondary/tertiary) | `border.interactive.xsmall` | 1px |
| Border width (active/focus) | `border.interactive.small` | 2px |

### Typography Tokens

| Property | v2 Token | Legacy (TM) |
|----------|----------|-------------|
| Standard | `semantic.typography.label.medium` | Averta Semibold 16px/24px |
| Transactional | `semantic.typography.label.large` | Averta Semibold 18px/26px |

---

## 2. CircleButton

### Colour Tokens

Same interactive colour tokens as Button per variant (primary, secondary, tertiary, inverse).

| Property | State | v2 Token |
|----------|-------|----------|
| Fill | Default | `color.interactive.{variant}.fill.default` |
| Fill | Hover | `color.interactive.{variant}.fill.hover` |
| Icon | Default | `color.interactive.{variant}.icon.default` |
| Border | Default | `color.interactive.{variant}.border.default` |
| Focus ring | | `color.focus.border` |

### Spacing Tokens

| Property | v2 Token |
|----------|----------|
| Icon size | `icon.size.large` (24px) |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.interactive.full` |

---

## 3. SquareButton

Same as CircleButton, except:

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.interactive.small` |

---

## 4. PillButton

### Colour Tokens

| Property | State | v2 Token | Legacy (TM) |
|----------|-------|----------|-------------|
| Fill (unselected) | Default | `color.interactive.secondary.fill.default` | Transparent |
| Fill (selected) | Default | `color.selected.primary.fill.default` | Ganymede `#21FFF2` |
| Text (unselected) | Default | `color.interactive.secondary.text.default` | Cosmos `#121212` |
| Text (selected) | Default | `color.selected.primary.text.default` | Cosmos `#121212` |
| Border | Default | `color.interactive.secondary.border.default` | — |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.interactive.full` |

---

## 5. CloseButton

### Colour Tokens

| Property | State | v2 Token |
|----------|-------|----------|
| Icon | Default | `color.icon.primary` |
| Icon | Hover | `color.interactive.ghost.icon.hover` |
| Fill | Hover | `color.interactive.ghost.fill.hover` |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.interactive.full` |

---

## 6. PaginationButton

### Colour Tokens

| Property | State | v2 Token |
|----------|-------|----------|
| Fill (inactive) | Default | `color.elevation.base` |
| Fill (active) | Default | `color.interactive.primary.fill.default` |
| Fill | Hover | `color.interactive.primary.fill.hover` |
| Text (inactive) | Default | `color.text.primary` |
| Text (active) | Default | `color.interactive.primary.text.default` |
| Border | Default | `color.border.primary` |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.interactive.small` |

---

## 7. Input Field

### Colour Tokens

| Property | State | v2 Token | Legacy (TM) |
|----------|-------|----------|-------------|
| Background | Default | `color.input.fill.default` | Spotlight `#FFFFFF` |
| Background | Disabled | `color.input.fill.disabled` | Diatomite `#EBEBEB` |
| Border | Default | `color.input.border.default` | Slate `#949494` |
| Border | Hover | `color.input.border.hover` | Neptune `#024DDF` |
| Border | Active/Focus | `color.input.border.active` | Neptune `#024DDF` |
| Border | Disabled | `color.input.border.disabled` | Moonrock `#BFBFBF` |
| Border | Error | `color.feedback.border.error` | Mars `#EB0000` |
| Border | Success | `color.feedback.border.success` | Earth `#048851` |
| Text (input) | Default | `color.input.text.default` | Cosmos `#121212` |
| Text (placeholder) | Default | `color.text.placeholder` | Granite `#646464` |
| Text (label) | Default | `color.text.secondary` | Granite `#646464` |
| Text | Disabled | `color.disabled.a` | Slate `#949494` |
| Icon | Default | `color.input.icon.default` | Granite `#646464` |
| Focus ring | | `color.focus.border` | Neptune `#024DDF` |

### Spacing Tokens

| Property | v2 Token | Legacy (TM) |
|----------|----------|-------------|
| Left padding | `button.spacing.large.horizontalPadding` | Auditorium 16px |
| Vertical padding | — (needs token) | 10px |
| Label gap | — (needs token) | 4px |
| Icon gap | — (needs token) | 10px |
| Form stacking gap | `layout.spacing.formGap` | 24px |

### Border Tokens

| Property | v2 Token | Legacy (TM) |
|----------|----------|-------------|
| Border radius | `border-radius.input.small` | 2px |
| Border width (default) | `border.interactive.xsmall` | 1px |
| Border width (active) | `border.interactive.small` | 2px |

### Typography Tokens

| Property | v2 Token | Legacy (TM) |
|----------|----------|-------------|
| Label | `semantic.typography.body.regular.small` | Averta Regular 14px/20px |
| Input text | `semantic.typography.body.regular.medium` | Averta Regular 16px/24px |
| Validation text | `semantic.typography.caption` | Averta Semibold 12px/16px |

---

## 8. Checkbox

### Colour Tokens

| Property | State | v2 Token |
|----------|-------|----------|
| Border (unchecked) | Default | `color.input.border.default` |
| Border (unchecked) | Hover | `color.input.border.hover` |
| Fill (checked) | Default | `color.interactive.primary.fill.default` |
| Fill (checked) | Hover | `color.interactive.primary.fill.hover` |
| Checkmark icon | Default | `color.interactive.primary.icon.default` |
| Fill | Disabled | `color.disabled.b` |
| Border | Disabled | `color.disabled.c` |
| Label text | Default | `color.text.primary` |
| Focus ring | | `color.focus.border` |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.input.small` |
| Border width | `border.interactive.small` |

---

## 9. CheckboxControl

Same token mapping as Checkbox (visual wrapper variant).

---

## 10. Radio Button

### Colour Tokens

| Property | State | v2 Token |
|----------|-------|----------|
| Border (unselected) | Default | `color.input.border.default` |
| Border (unselected) | Hover | `color.input.border.hover` |
| Fill (selected dot) | Default | `color.interactive.primary.fill.default` |
| Fill (selected dot) | Hover | `color.interactive.primary.fill.hover` |
| Outer ring (selected) | Default | `color.interactive.primary.fill.default` |
| Fill | Disabled | `color.disabled.b` |
| Label text | Default | `color.text.primary` |
| Focus ring | | `color.focus.border` |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border width | `border.interactive.small` |

---

## 11. Dropdown

### Colour Tokens

Same input tokens as Input Field for the trigger:

| Property | State | v2 Token |
|----------|-------|----------|
| Background | Default | `color.input.fill.default` |
| Border | Default | `color.input.border.default` |
| Border | Hover | `color.input.border.hover` |
| Border | Active | `color.input.border.active` |
| Text (value) | Default | `color.input.text.default` |
| Text (placeholder) | Default | `color.text.placeholder` |
| Caret icon | Default | `color.input.icon.default` |
| Label | Default | `color.text.secondary` |

**Dropdown menu (popover):**

| Property | v2 Token |
|----------|----------|
| Background | `color.elevation.level-1` |
| Border | `color.border.elevation` |
| Border radius | `border-radius.popover.medium` |
| Item text | `color.text.primary` |
| Item hover fill | `color.interactive.secondary.fill.hover` |
| Item selected fill | `color.selected.primary.fill.default` |

---

## 12. Toggle

### Colour Tokens

| Property | State | v2 Token |
|----------|-------|----------|
| Track (off) | Default | `color.input.border.default` |
| Track (on) | Default | `color.interactive.primary.fill.default` |
| Track | Disabled | `color.disabled.b` |
| Thumb | Default | `color.elevation.base` |
| Focus ring | | `color.focus.border` |

---

## 13. Date Picker

### Colour Tokens

Uses Input Field tokens for the trigger. Calendar popover uses:

| Property | State | v2 Token |
|----------|-------|----------|
| Popover background | | `color.elevation.level-1` |
| Day text | Default | `color.text.primary` |
| Day text | Disabled | `color.disabled.a` |
| Selected day fill | | `color.interactive.primary.fill.default` |
| Selected day text | | `color.interactive.primary.text.default` |
| Today indicator | | `color.interactive.primary.fill.default` |
| Hover fill | | `color.interactive.secondary.fill.hover` |
| Border radius (popover) | | `border-radius.popover.medium` |

---

## 14. Double Range Input

### Colour Tokens

| Property | State | v2 Token |
|----------|-------|----------|
| Track (filled) | Default | `color.interactive.primary.fill.default` |
| Track (unfilled) | Default | `color.border.secondary` |
| Thumb | Default | `color.interactive.primary.fill.default` |
| Thumb | Hover | `color.interactive.primary.fill.hover` |
| Thumb border | Default | `color.elevation.base` |
| Min/max labels | Default | `color.text.secondary` |
| Focus ring | | `color.focus.border` |

Input fields use same tokens as Input Field.

---

## 15. Stepper

### Colour Tokens

| Property | State | v2 Token |
|----------|-------|----------|
| Button fill | Default | `color.interactive.secondary.fill.default` |
| Button fill | Hover | `color.interactive.secondary.fill.hover` |
| Button icon | Default | `color.interactive.secondary.icon.default` |
| Button | Disabled | `color.disabled.b` |
| Value text | Default | `color.text.primary` |
| Border | Default | `color.input.border.default` |
| Focus ring | | `color.focus.border` |

---

## 16. Alert

### Colour Tokens

| Property | Variant | v2 Token |
|----------|---------|----------|
| Fill | Error | `color.feedback.fill.error` |
| Fill | Success | `color.feedback.fill.success` |
| Fill | Warning | `color.feedback.fill.warning` |
| Fill | Info | `color.feedback.fill.info` |
| Icon | Error | `color.feedback.icon.error` |
| Icon | Success | `color.feedback.icon.success` |
| Icon | Warning | `color.feedback.icon.warning` |
| Icon | Info | `color.feedback.icon.info` |
| Text | Error | `color.feedback.text.error` |
| Text | Success | `color.feedback.text.success` |
| Text | Warning | `color.feedback.text.warning` |
| Text | Info | `color.feedback.text.info` |
| Border | Error | `color.feedback.border.error` |
| Border | Success | `color.feedback.border.success` |
| Border | Warning | `color.feedback.border.warning` |
| Border | Info | `color.feedback.border.info` |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.container.medium` |

---

## 17. Toast

Same feedback tokens as Alert, typically `info` or `success` variant only.

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.container.medium` |
| Elevation | `color.elevation.level-3` (shadow) |

---

## 18. Badge

### Colour Tokens

| Property | Variant | v2 Token | Legacy (TM) |
|----------|---------|----------|-------------|
| Fill | Active | `color.feedback.fill.success` | Earth `#048851` |
| Fill | Inactive | `color.elevation.inverse` | Cosmos `#121212` |
| Text | | `color.text.inverse` | Spotlight `#FFFFFF` |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.interactive.full` |

---

## 19. Loading Spinner

### Colour Tokens

| Property | Variant | v2 Token | Legacy (TM) |
|----------|---------|----------|-------------|
| Arc | Primary | `color.interactive.primary.fill.default` | Neptune `#024DDF` |
| Arc | Secondary | `color.icon.secondary` | Granite `#646464` |
| Arc | Inverse | `color.text.inverse` | Spotlight `#FFFFFF` |

### Sizing

| Size | v2 Token |
|------|----------|
| Small (24px) | `icon.size.large` |
| Medium (32px) | `icon.size.xlarge` |
| Large (72px) | — (needs token or hardcoded) |

---

## 20. Modal

### Colour Tokens

| Property | v2 Token | Legacy (TM) |
|----------|----------|-------------|
| Background | `color.elevation.level-1` | Spotlight `#FFFFFF` |
| Overlay | `color.elevation.overlay` | Cosmos 60% opacity |
| Title text | `color.text.primary` | Cosmos `#121212` |
| Body text | `color.text.secondary` | Granite `#646464` |
| Close icon | `color.icon.primary` | — |
| Divider | `color.border.primary` | — |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.container.large` |

### Spacing Tokens

| Property | v2 Token |
|----------|----------|
| Content to button | `layout.spacing.contentToButton` |

---

## 21. Side Panel

### Colour Tokens

| Property | v2 Token | Legacy (TM) |
|----------|----------|-------------|
| Background | `color.elevation.level-1` | Spotlight `#FFFFFF` |
| Overlay | `color.elevation.overlay` | Cosmos 60% opacity |
| Header text | `color.text.primary` | Cosmos `#121212` |
| Close icon | `color.icon.primary` | — |
| Divider | `color.border.primary` | — |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.container.none` (flush edge) |

---

## 22. Tooltip

### Colour Tokens

| Property | v2 Token |
|----------|----------|
| Background | `color.elevation.inverse` |
| Text | `color.text.inverse` |
| Arrow | `color.elevation.inverse` |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.popover.small` |

---

## 23. Accordion

### Colour Tokens

| Property | State | v2 Token |
|----------|-------|----------|
| Header text | Default | `color.text.primary` |
| Header background | Default | `color.elevation.base` |
| Header background | Hover | `color.interactive.secondary.fill.hover` |
| Chevron icon | Default | `color.icon.primary` |
| Body text | Default | `color.text.primary` |
| Divider | Default | `color.border.primary` |
| Focus ring | | `color.focus.border` |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.container.none` |

---

## 24. Divider

### Colour Tokens

| Property | v2 Token | Legacy (TM) |
|----------|----------|-------------|
| Line colour | `color.border.primary` | Moonrock `#BFBFBF` |

---

## 25. Image

No colour tokens required. Container may use:

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.container.medium` (optional) |
| Placeholder fill | `color.elevation.base` |

---

## 26. Countdown Timer

### Colour Tokens

| Property | v2 Token |
|----------|----------|
| Text | `color.text.primary` |
| Separator | `color.text.secondary` |
| Background | `color.elevation.base` |

### Typography Tokens

| Property | v2 Token |
|----------|----------|
| Digits | `semantic.typography.heading.large` |
| Labels | `semantic.typography.caption` |

---

## 27. Filterbar

### Colour Tokens

| Property | State | v2 Token |
|----------|-------|----------|
| Segment (inactive) | Default | `color.elevation.base` |
| Segment (active) | Default | `color.interactive.primary.fill.default` |
| Text (inactive) | Default | `color.text.primary` |
| Text (active) | Default | `color.interactive.primary.text.default` |
| Icon (inactive) | Default | `color.icon.secondary` |
| Icon (active) | Default | `color.interactive.primary.icon.default` |

### Border Tokens

| Property | v2 Token |
|----------|----------|
| Border radius | `border-radius.interactive.full` |

---

## 28. Toggler BarBlock

Same tokens as Filterbar (visual variant).

---

## 29. Payment Icons

No semantic colour tokens — icons are brand-specific SVGs. Container may use:

| Property | v2 Token |
|----------|----------|
| Background | `color.elevation.base` |

---

## Token Gaps Identified

Tokens that are needed by components but **do not exist yet** in the v2 token set:

| Gap | Component(s) | Suggested Token |
|-----|-------------|-----------------|
| Input vertical padding | Input Field, Dropdown | `input.spacing.verticalPadding` |
| Input label gap | Input Field | `input.spacing.labelGap` |
| Input icon gap | Input Field | `input.spacing.iconGap` |
| Input validation gap | Input Field | `input.spacing.validationGap` |
| Large spinner size (72px) | Loading Spinner | `icon.size.xxlarge` or component token |
| Gradient tokens | — (brand metadata) | Not a token; stays in brand config |
| Logo SVG | — (brand metadata) | Not a token; stays in brand config |
| ISM colours | — (product-specific) | Not a token; stays in product config |
