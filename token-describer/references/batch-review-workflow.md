# Batch Review Workflow (Step 7 replacement)

This document describes the batch review workflow that replaces the one-by-one
`AskUserQuestion` loop previously described in Step 7 of SKILL.md.

The old approach required a separate confirmation for every unmatched token,
which is impractical for large token sets (100+ tokens). The batch workflow
collects all tokens needing review into a single markdown file, lets the user
fill in decisions at their own pace, then applies them in one pass.

---

## Overview

```
generate_review_report.py
        |
        v
  REVIEW-PENDING.md     <-- user fills in this file
        |
        v
  apply_review.py
        |
        +-- updates token JSON files ($description fields)
        +-- records corrections in runs/corrections.jsonl
        +-- archives review to runs/review-YYYY-MM-DD.md
```

---

## Step 7: Batch Review for Tokens Without Figma Context

### 7a. Generate the review report

After generating provisional descriptions in Step 6, run:

```bash
python3 token-describer/scripts/generate_review_report.py
```

This scans all token files under `tokens/` and identifies tokens that either:
- Have no `$description` field at all, or
- Have a provisional (pattern-generated) description that has not been
  Figma-verified (no `$extensions.figmaVerified` flag).

To scan a single file or directory instead of all token files:

```bash
python3 token-describer/scripts/generate_review_report.py tokens/semantic/colorLight.json
python3 token-describer/scripts/generate_review_report.py tokens/semantic/
```

The script writes `token-describer/REVIEW-PENDING.md` and prints a summary:

```
Scanning 11 token file(s)...
  tokens/semantic/colorLight.json: 47 token(s) needing review
  tokens/component/spacing/desktop.json: all descriptions verified
  ...

Review file written to: /path/to/token-describer/REVIEW-PENDING.md
Total tokens needing review: 47
```

### 7b. Present the review file to the user

Open `REVIEW-PENDING.md` and present it to the user. The file groups tokens
by category (interactive, text, input, feedback, surface, elevation, border,
typography, component) with one row per token:

```markdown
## Interactive Tokens (12)

| Token Path | Provisional Description | Reason | Accept? | New Description | Notes |
|---|---|---|---|---|---|
| color.interactive.tertiary.fill.default | Use for tertiary buttons. Low emphasis. | provisional — not Figma-verified |  |  |  |
| color.interactive.tertiary.fill.hover | Tertiary button fill on hover. | provisional — not Figma-verified |  |  |  |
```

The user fills in the table. Three valid actions per row:

| Situation | What to write |
|---|---|
| Provisional description is correct | Write `y` in Accept? |
| Provisional is wrong | Leave Accept? blank, write replacement in New Description |
| Not sure yet | Leave both blank — row stays pending |

The Notes column is optional. Encourage the user to record reasoning there
when they change a description — it feeds into the corrections log.

### 7c. User fills in the review file

The user can:
- Edit `REVIEW-PENDING.md` directly in their editor, or
- Ask you (the AI) to propose values for Accept? and New Description based
  on any Figma context gathered in Step 5.

If Figma context is available, use it to pre-fill Accept? = `y` for tokens
whose provisional descriptions match observed component usage, and propose
replacements for those that don't.

**Partial reviews are fully supported.** The user does not need to fill in
every row in one session. Blank rows are simply skipped by `apply_review.py`
and will reappear in the next review report.

### 7d. Apply the decisions

Once the user has filled in at least some rows, run:

```bash
python3 token-describer/scripts/apply_review.py
```

The script:
1. Parses the markdown tables in `REVIEW-PENDING.md`.
2. For each filled-in row, locates the token across all files under `tokens/`.
3. Updates `$description` in the token JSON file.
4. For accepted rows, sets `$extensions.figmaVerified = true` so the token
   is excluded from future review reports.
5. Records every change in `token-describer/runs/corrections.jsonl` via
   `run_tracker.record_correction`.
6. Moves `REVIEW-PENDING.md` to `token-describer/runs/review-YYYY-MM-DD.md`.
7. Prints a summary:

```
==================================================
APPLY REVIEW COMPLETE
==================================================
  Accepted (kept provisional):  31
  Corrected (new description):  9
  Token not found in files:     0
  Still pending (blank rows):   7

  Review file archived to: token-describer/runs/review-2026-03-31.md
```

To override the default review file path:

```bash
python3 token-describer/scripts/apply_review.py --review path/to/OTHER-REVIEW.md
```

### 7e. Handle remaining pending tokens

If any tokens were left blank (pending count > 0), run the generator again
after the next round of Figma inspection or team review:

```bash
python3 token-describer/scripts/generate_review_report.py
```

The new `REVIEW-PENDING.md` will contain only the still-unverified tokens.
Accepted/corrected tokens are excluded because they now carry
`$extensions.figmaVerified = true`.

Continue the cycle until pending count reaches zero, or until the team
decides the remaining provisional descriptions are acceptable for release.

---

## Scripts reference

| Script | Purpose |
|---|---|
| `scripts/generate_review_report.py` | Scan token files and write REVIEW-PENDING.md |
| `scripts/apply_review.py` | Parse filled-in REVIEW-PENDING.md and update token files |
| `scripts/run_tracker.py` | Module for recording corrections to runs/corrections.jsonl |

---

## Corrections log

Every decision applied by `apply_review.py` is appended to
`token-describer/runs/corrections.jsonl` in JSONL format. Each line is one
JSON object:

```json
{
  "timestamp": "2026-03-31T14:22:05Z",
  "date": "2026-03-31",
  "token_path": "color.interactive.tertiary.fill.default",
  "old_description": "Use for tertiary buttons. Low emphasis.",
  "new_description": "Low-emphasis fills for ghost-style buttons in cards and banners.",
  "source_file": "",
  "notes": "Confirmed via Figma: tertiary = ghost style in card/banner close buttons"
}
```

This log is the audit trail for the "User Review Loop" design principle: every
description that was changed from its provisional value is recorded with the
user's reasoning.

---

## Why batch instead of one-by-one

The original Step 7 used `AskUserQuestion` for each individual token. This
approach breaks down at scale:

- A typical semantic token file has 80-120 tokens, most of which lack Figma
  verification on first pass.
- 100 sequential prompts interrupts flow and makes it impossible to compare
  related tokens side-by-side.
- The user cannot easily spot inconsistencies across a group (e.g. all
  `interactive.tertiary.*` tokens) when reviewing one at a time.

The batch approach trades real-time confirmation for a richer review surface:
the user sees all tokens in a category together, can cross-reference related
tokens, and can fill in the review file at a pace that suits them (including
across multiple sessions).
