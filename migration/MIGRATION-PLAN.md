# Token Migration Plan

## Status: Not Started

## Objective

Migrate from the legacy token structure to the new standardised token structure, ensuring alignment between Figma (Token Studio) and coded outputs (Style Dictionary).

## Phases

### Phase 1 — Audit & Document
- [ ] Import current tokens into `resources/current-tokens/`
- [ ] Import token definitions into `resources/definitions/`
- [ ] Import new token structure reference into `resources/new-token-structure/`
- [ ] Document current token inventory (categories, count, naming patterns)
- [ ] Document new token structure (categories, naming conventions, hierarchy)
- [ ] Identify mismatches between Figma tokens and code tokens

### Phase 2 — Mapping
- [ ] Create old → new token mapping table
- [ ] Identify tokens that can be mapped 1:1
- [ ] Identify tokens that need renaming only
- [ ] Identify tokens that need restructuring
- [ ] Identify tokens that are deprecated / removed
- [ ] Identify new tokens with no legacy equivalent

### Phase 3 — Build Pipeline
- [ ] Configure Style Dictionary with Token Studio transforms
- [ ] Validate build output against current coded tokens
- [ ] Set up output formats for all required platforms (CSS, SCSS, JS)

### Phase 4 — Migration Execution
- [ ] Migrate tokens in `tokens/` to new structure
- [ ] Validate build output matches expected new structure
- [ ] Test in Storybook
- [ ] Document breaking changes

### Phase 5 — Cutover
- [ ] Move token repo from GitHub to GitLab
- [ ] Update Token Studio sync settings to point to GitLab
- [ ] Update CI/CD pipeline for token builds
- [ ] Deprecation notices for legacy token consumers

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| | | |
