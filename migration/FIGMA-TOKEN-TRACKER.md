# Figma Token Application Tracker

> Track progress of applying v2 design tokens to GDS Figma components.
>
> **Status key:**
> - [ ] Not started
> - [~] In progress
> - [x] Complete
> - [!] Blocked (see notes)
>
> **Columns:**
> - **Mapped** = token-to-property mapping is documented in COMPONENT-TOKEN-MAPPING.md
> - **Figma Applied** = tokens are attached to the Figma component as variables
> - **Verified** = visual QA confirms the component looks correct with tokens applied
> - **Storybook** = coded token output matches Figma (future phase)

---

## Priority 1: Interactive Primitives

These are the foundation — most other components compose from these patterns.

| # | Component | Mapped | Figma Applied | Verified | Storybook | Notes |
|---|-----------|--------|---------------|----------|-----------|-------|
| 1 | Button (Primary) | [x] | [ ] | [ ] | [ ] | Start here. Validates interactive colour tokens + spacing + border. |
| 2 | Button (Secondary) | [x] | [ ] | [ ] | [ ] | Validates border colour tokens. |
| 3 | Button (Tertiary) | [x] | [ ] | [ ] | [ ] | |
| 4 | Button (Ghost) | [x] | [ ] | [ ] | [ ] | |
| 5 | Button (Inverse) | [x] | [ ] | [ ] | [ ] | |
| 6 | Button (Transaction) | [x] | [ ] | [ ] | [ ] | |
| 7 | CircleButton | [x] | [ ] | [ ] | [ ] | Shares button colour tokens. |
| 8 | SquareButton | [x] | [ ] | [ ] | [ ] | Shares button colour tokens. |
| 9 | PillButton | [x] | [ ] | [ ] | [ ] | Validates selected state tokens. |
| 10 | CloseButton | [x] | [ ] | [ ] | [ ] | Ghost icon variant. |
| 11 | PaginationButton | [x] | [ ] | [ ] | [ ] | |

## Priority 2: Form Controls

These validate input token patterns (fill, border, text per state).

| # | Component | Mapped | Figma Applied | Verified | Storybook | Notes |
|---|-----------|--------|---------------|----------|-----------|-------|
| 12 | Input Field | [x] | [ ] | [ ] | [ ] | Core form component. Validates input colour + feedback tokens. |
| 13 | Checkbox | [x] | [ ] | [ ] | [ ] | |
| 14 | CheckboxControl | [x] | [ ] | [ ] | [ ] | Visual wrapper of Checkbox. |
| 15 | Radio Button | [x] | [ ] | [ ] | [ ] | |
| 16 | Dropdown | [x] | [ ] | [ ] | [ ] | Input tokens + popover/elevation tokens. |
| 17 | Toggle | [x] | [ ] | [ ] | [ ] | |
| 18 | Date Picker | [x] | [ ] | [ ] | [ ] | Input tokens + calendar popover. |
| 19 | Double Range Input | [x] | [ ] | [ ] | [ ] | |
| 20 | Stepper | [x] | [ ] | [ ] | [ ] | |

## Priority 3: Feedback & Status

These validate the feedback token set (error, success, warning, info).

| # | Component | Mapped | Figma Applied | Verified | Storybook | Notes |
|---|-----------|--------|---------------|----------|-----------|-------|
| 21 | Alert | [x] | [ ] | [ ] | [ ] | All 4 feedback variants. |
| 22 | Toast | [x] | [ ] | [ ] | [ ] | Subset of Alert tokens. |
| 23 | Badge | [x] | [ ] | [ ] | [ ] | |
| 24 | Loading Spinner | [x] | [ ] | [ ] | [ ] | 3 colour variants. Large size needs token. |

## Priority 4: Overlays & Containers

These validate elevation and border-radius tokens.

| # | Component | Mapped | Figma Applied | Verified | Storybook | Notes |
|---|-----------|--------|---------------|----------|-----------|-------|
| 25 | Modal | [x] | [ ] | [ ] | [ ] | Elevation + overlay tokens. |
| 26 | Side Panel | [x] | [ ] | [ ] | [ ] | |
| 27 | Tooltip | [x] | [ ] | [ ] | [ ] | Inverse elevation. |
| 28 | Accordion | [x] | [ ] | [ ] | [ ] | |

## Priority 5: Content & Utility

Lower priority — simpler token needs.

| # | Component | Mapped | Figma Applied | Verified | Storybook | Notes |
|---|-----------|--------|---------------|----------|-----------|-------|
| 29 | Divider | [x] | [ ] | [ ] | [ ] | Single border colour token. |
| 30 | Image | [x] | [ ] | [ ] | [ ] | Minimal — placeholder fill + optional radius. |
| 31 | Countdown Timer | [x] | [ ] | [ ] | [ ] | Text + elevation tokens. |
| 32 | Filterbar | [x] | [ ] | [ ] | [ ] | Interactive + selected tokens. |
| 33 | Toggler BarBlock | [x] | [ ] | [ ] | [ ] | Same as Filterbar. |
| 34 | Payment Icons | [x] | [ ] | [ ] | [ ] | Minimal — container only. |

---

## Summary

| Priority | Components | Status |
|----------|-----------|--------|
| P1: Interactive Primitives | 11 | 0/11 applied |
| P2: Form Controls | 9 | 0/9 applied |
| P3: Feedback & Status | 4 | 0/4 applied |
| P4: Overlays & Containers | 4 | 0/4 applied |
| P5: Content & Utility | 6 | 0/6 applied |
| **Total** | **34** | **0/34 applied** |

---

## Blockers & Dependencies

| Blocker | Impact | Resolution |
|---------|--------|------------|
| Zero-width Unicode chars in token names | Tokens won't bind correctly in Figma | Clean token names before applying (see TOKEN-AUDIT.md #1) |
| Spaces in component/spacing directory names | Style Dictionary glob issues | Rename directories before building (see TOKEN-AUDIT.md #2) |
| Missing input spacing tokens | Input Field spacing can't be fully tokenised | Add `input.spacing.*` tokens to component set |
| Mobile token inconsistencies | Mobile variants can't be applied until fixed | Fix naming + remove `px` suffix (see TOKEN-AUDIT.md #3, #4) |
| No dark theme | Only light theme can be applied | Dark theme is future work; not a blocker for light theme |

---

## Workflow per Component

1. Open the GDS Figma file
2. Navigate to the component
3. For each property in the mapping doc:
   a. Select the layer/element
   b. In the Fill/Stroke/Text panel, click the variable picker
   c. Select the corresponding v2 token variable
   d. Repeat for all states (use Figma's component properties / variants)
4. Mark "Figma Applied" in this tracker
5. Visually compare against the current component — should look identical for TM brand
6. Mark "Verified" when confirmed
7. Repeat for all variants and states of the component
