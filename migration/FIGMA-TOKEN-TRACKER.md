# Figma Token Application Tracker

> **Last audited:** 2026-05-06 — full automated sharedPluginData audit across all pages in `dfLpxHSoyojN9805EQXqy6`
>
> **Status key:**
> - [ ] Not started
> - [~] In progress / partial
> - [x] Complete
> - [!] Needs redo — format issues or broken token paths
>
> **Columns:**
> - **Mapped** = token-to-property mapping documented in COMPONENT-TOKEN-MAPPING.md
> - **Stripped** = hardcoded fills/strokes/style references removed from all nodes
> - **Tokens Applied** = Token Studio sharedPluginData attached to all nodes
> - **Verified** = visual QA confirms component looks correct after Token Studio sync

---

## Audit Summary (2026-05-06)

| Group | Components | Action needed |
|-------|-----------|---------------|
| Not started | 8 | Apply tokens from scratch; strip styles |
| Format issues | 3 | Clear legacy keys; reapply correctly; strip styles |
| Partial (low) | 7 | Complete token application; strip styles |
| Partial (medium) | 5 | Complete token application; strip styles |
| Higher coverage | 3 | Verify + complete gaps; strip styles |

**Critical:** No component has been stripped of embedded styles yet. All components still carry hardcoded fills/strokes/style references regardless of token coverage.

**Token file gap:** Toggle bindings reference `toggle.color.*` paths that don't exist in `tokens/component/` — a `toggle.json` needs to be created before Toggle can be properly re-applied.

---

## Priority 1: Interactive Primitives

| # | Component | Page | Node | Token Coverage | Stripped | Tokens Applied | Verified | Notes |
|---|-----------|------|------|---------------|----------|----------------|----------|-------|
| 1 | Button (all variants) | `3:14` | `—` | 48% | [ ] | [!] | [ ] | `tokenName` key on component set is legacy format — needs clearing. Otherwise bindings on child nodes look structurally valid. |
| 2 | Circle Button | `34612:13776` | `—` | 0% | [ ] | [ ] | [ ] | Not started. |
| 3 | Square Button | `34612:14405` | `—` | 0% | [ ] | [ ] | [ ] | Not started. |
| 4 | Pill Button | `33403:293` | `—` | 71% | [ ] | [~] | [ ] | Highest coverage of all. Spot-check bindings then complete gaps. |
| 5 | Pagination Button | `30:20730` | `355:36072` | ✅ | ✅ | [x] | [ ] | Stripped and re-applied 2026-05-06. 4 nodes bound: container fill, text (fill + typography), loading bar (fill + borderRadius), progress bar (fill + borderRadius). Awaiting Token Studio sync to verify visual. |

## Priority 2: Form Controls

| # | Component | Page | Node | Token Coverage | Stripped | Tokens Applied | Verified | Notes |
|---|-----------|------|------|---------------|----------|----------------|----------|-------|
| 6 | Input Field | `30:15296` | `—` | 7% | [ ] | [~] | [ ] | Very low coverage — effectively not started. 557 nodes. |
| 7 | Checkbox | `30:15297` | `—` | 25% | [ ] | [~] | [ ] | Partial — only fill/border applied, no text or spacing tokens. |
| 8 | Radio Button | `30:15298` | `21:28156` | 56% | [ ] | [~] | [ ] | Previously marked done but coverage incomplete. Missing typography + spacing. |
| 9 | Toggle | `30:15299` | `21:28235` | 69% | [ ] | [!] | [ ] | Token paths reference `toggle.color.*` — no matching file in `tokens/component/`. Need to create `toggle.json`. Component set also has legacy `values` key. |
| 10 | Dropdown | `30:15300` | `—` | 15% | [ ] | [~] | [ ] | Partial — fill/border only, no text, typography, or spacing. |
| 11 | Double Range Input | `30:15301` | `—` | 0% | [ ] | [ ] | [ ] | Not started. |
| 12 | Stepper | `30:15302` | `—` | 69% | [ ] | [~] | [ ] | High coverage. Spot-check paths and fill gaps. |

## Priority 3: Feedback & Status

| # | Component | Page | Node | Token Coverage | Stripped | Tokens Applied | Verified | Notes |
|---|-----------|------|------|---------------|----------|----------------|----------|-------|
| 13 | Alert Box | `30:15280` | `10410:52042` | ✅ | ✅ | [x] | [ ] | Stripped and re-applied 2026-05-06. 50 nodes across all 16 variants (Desktop/Mobile × Error/Warning/Information/Success × Nested/Non-nested). Filled in missing icon fill on Error variants (`color.feedback.icon.error`). Removed stale `fontSize`/`lineHeight` keys from all text nodes — composite `typography` token handles these. Awaiting Token Studio sync. |
| 14 | Toast | `38852:11802` | `38852:13585` | ✅ | ✅ | [x] | [ ] | Stripped and re-applied 2026-05-06. 7 nodes bound: 2 containers, 2 text, 2 close icons, 1 status icon. Awaiting Token Studio sync to verify visual. |
| 15 | Badge | `30:15282` | `21:25864` | ✅ | ✅ | [x] | [ ] | Stripped and re-applied 2026-05-06. All 37 variants stripped and confirmed complete: fill, borderRadius, spacing (verticalPadding/horizontalPadding/itemSpacing), typography, and text fill on every variant. Filled=Off variants also have borderColor + borderWidth. Fixed missing borderColor/borderWidth on Type=Promoted Filled=Off. ⚠️ Fill tokens reference brand-level paths (color.accent.*, color.neutrals.grey.*, color.common.white) — semantic wrappers needed for theme-switching. JIRA story required. |
| 16 | Loading Spinner | `33145:4265` | `33145:3778` | ✅ | ✅ | [x] | [ ] | Stripped and re-applied 2026-05-06. 35 nodes bound: arc + trail fills on all 4 base variants and all 9 main variants (3 sizes × 3 colours), plus fill + typography on all 9 Label text nodes. Note: all main variants were pointing to Variant1 (Primary) as base — colour override tokens set at instance level to compensate. Awaiting Token Studio sync. |

## Priority 4: Overlays & Containers

| # | Component | Page | Node | Token Coverage | Stripped | Tokens Applied | Verified | Notes |
|---|-----------|------|------|---------------|----------|----------------|----------|-------|
| 17 | Modal | `21:4835` | `—` | 0% | [ ] | [ ] | [ ] | Not started. Largest component — 1,261 nodes across 35 component sets. |
| 18 | Tooltip | `3:9` | `—` | 0% | [ ] | [ ] | [ ] | Not started. |
| 19 | PopOver | `49448:2639` | `—` | 0% | [ ] | [ ] | [ ] | Not started. Token file exists (`tokens/component/popover.json`). |
| 20 | Accordion | `2508:146157` | `—` | 48% | [ ] | [~] | [ ] | Medium coverage. 766 nodes. |

## Priority 5: Content & Utility

| # | Component | Page | Node | Token Coverage | Stripped | Tokens Applied | Verified | Notes |
|---|-----------|------|------|---------------|----------|----------------|----------|-------|
| 21 | Filter Bar | `30:22688` | `30:20751` | 45% | [ ] | [~] | [ ] | Previously marked done. Coverage audit shows only fill/border — missing spacing. |
| 22 | Display Heading | `42691:1307` | `—` | 49% | [ ] | [~] | [ ] | Typography + fill applied. Check all heading levels. |
| 23 | Image | `38863:4977` | `—` | 0% | [ ] | [ ] | [ ] | Not started. Minimal — placeholder fill + optional radius only. |
| 24 | Slot | `25353:4183` | `—` | 0% | [ ] | [ ] | [ ] | Not started. |

---

## Blockers & Outstanding Issues

| Blocker | Impact | Resolution |
|---------|--------|------------|
| No `tokens/component/toggle.json` | Toggle bindings reference non-existent token paths | Create toggle.json before re-applying Toggle |
| Legacy `values` key on Toggle component set | Old Token Studio format — won't work in current Token Studio | Clear all `values` keys, reapply with correct individual property keys |
| Legacy `tokenName` key on Button component set | Non-standard key — will be ignored by Token Studio | Clear key before re-validating Button coverage |
| ~~Non-standard `spacing` key on Toast~~ | ~~Token Studio does not recognise `spacing` as a property key~~ | ✅ Resolved 2026-05-06 — Toast Figma bindings updated to use `paddingTop/Bottom/Left/Right` and `itemSpacing`. Toast spacing tokens also moved to `component/spacing/desktop.json`. |
| No embedded styles stripped yet | Hardcoded fills/strokes remain on all nodes | Strip phase must precede or accompany token application |
| Zero-width Unicode chars in `colorLight.json` token names | Bindings will break silently at sync | Clean token names first (see TOKEN-AUDIT.md #1) |

---

## Token Files vs Component Coverage

| Token file | Component(s) | Status |
|-----------|-------------|--------|
| `tokens/component/toast.json` | Toast | ✅ File exists |
| `tokens/component/stepper.json` | Stepper | ✅ File exists |
| `tokens/component/filterBar.json` | Filter Bar | ✅ File exists |
| `tokens/component/loading.json` | Loading Spinner | ✅ File exists |
| `tokens/component/popover.json` | PopOver | ✅ File exists |
| `tokens/component/spacing/desktop.json` | All spacing | ✅ File exists |
| `tokens/component/spacing/mobile.json` | All spacing | ✅ File exists |
| ❌ `tokens/component/toggle.json` | Toggle | ❌ Missing — must create |
| ❌ `tokens/component/button.json` | Button (spacing) | ❌ No component file — spacing uses semantic tokens directly |
| ❌ `tokens/component/badge.json` | Badge | ❌ No component file |
| ❌ `tokens/component/modal.json` | Modal | ❌ No component file |
| ❌ `tokens/component/tooltip.json` | Tooltip | ❌ No component file |

---

## Workflow per Component

1. **Strip** — remove all fills, strokes, and style references from every node on the page
2. **Resolve** — trace token paths for each node/state against the token JSON files; verify colour math
3. **Apply** — write `sharedPluginData` bindings using `setSharedPluginData("tokens", key, JSON.stringify(path))`
4. **Verify** — read back keys; sync Token Studio; visual QA
5. **Mark complete** in this tracker
