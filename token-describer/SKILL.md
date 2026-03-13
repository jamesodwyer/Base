---
name: token-describer
description: This skill should be used when the user asks to "generate token descriptions", "document design tokens", "add descriptions to tokens", "update token documentation", or mentions improving design token files with descriptions.
version: 1.0.0
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, ToolSearch, AskUserQuestion
---

# Token Description Generator

This skill generates concise, Figma-informed descriptions for design tokens in a `tokens.json` file. It supports both local file workflows and Git repository workflows, with optional Figma MCP integration for accurate component-based descriptions.

---

## Overview

Design tokens benefit from clear, actionable descriptions that help designers and developers understand their purpose. This skill:

1. **Analyzes token structure** (core/semantic/component tiers)
2. **Integrates with Figma** to understand real component usage
3. **Generates descriptions** based on proven patterns (not just token names)
4. **Creates comprehensive documentation** for maintenance
5. **Supports Git workflows** for team collaboration

**Key principle**: Descriptions must be grounded in **real usage context**, never solely on token naming conventions.

---

## When to Use This Skill

Invoke this skill when:
- Adding descriptions to a design token file
- Documenting a token system for designers/developers
- Updating token descriptions after component changes
- Creating token documentation for a new design system

**Usage**: `/token-describer path/to/tokens.json` or `/token-describer $ARGUMENTS`

---

## Workflow

### Step 1: Determine Workflow Type

Ask the user:

```
Are you working with a local file or a Git repository?

Options:
1. Local file - I'll update the tokens.json in place
2. Git repository - I'll clone, create a branch, and prepare for PR
```

**If Git workflow**:
- Ask for repository URL
- Ask for branch name to create (e.g., `add-token-descriptions`)
- Ask if they want to create a PR at the end (yes/no)

**If local file**:
- Proceed directly to token analysis

---

### Step 2: Git Setup (Conditional)

**If user selected Git workflow**:

1. **Clone repository** (if not already in a git repo)
   ```bash
   git clone {repo_url}
   cd {repo_directory}
   ```

2. **Create feature branch**
   ```bash
   git checkout -b {branch_name}
   ```

3. **Verify tokens.json location**
   - Use provided path or search for `tokens.json` in repo

---

### Step 3: Analyze Token Structure

1. **Read tokens.json** using Read tool
2. **Parse structure** to identify:
   - Total token count
   - Tokens by tier (core, semantic, component)
   - Existing descriptions (count and coverage %)
3. **Report findings** to user:
   ```
   Token Analysis:
   - Total tokens: {count}
   - With descriptions: {count} ({percent}%)
   - Without descriptions: {count}

   By tier:
   - Core tokens: {count}
   - Semantic tokens: {count}
   - Component tokens: {count}
   ```

---

### Step 4: Figma Integration Setup

**Ask user**:
```
Do you have a Figma design file to inspect for component usage?

This helps generate accurate descriptions based on real implementation.

Options:
1. Yes - I'll provide a Figma file URL
2. No - Generate descriptions without Figma context
```

**If Yes**:
1. **Load Figma MCP tools** using ToolSearch:
   ```
   ToolSearch({query: "figma"})
   ```

2. **Ask for Figma file URL/key**:
   ```
   Please provide the Figma file URL or file key.

   Example: https://figma.com/file/ABC123.../Design-System
   Or just: ABC123...
   ```

3. **Extract file key** from URL if needed

**If No**:
- Proceed with pattern-based descriptions
- Flag semantic/component tokens for user review

---

### Step 5: Figma Component Inspection (Conditional)

**If Figma available**:

1. **Get design variables** from Figma
   ```
   figma_get_variables({fileKey: {key}})
   ```

2. **Map variables to token paths**
   - Figma uses slashes: `color/interactive/primary/fill/default`
   - tokens.json uses dots: `color.interactive.primary.fill.default`
   - Convert between formats

3. **For priority tokens** (interactive, input, feedback):
   - Get component details
   - Find variable bindings
   - Extract component names (Button, Input, Card, Banner, etc.)
   - Note usage contexts

4. **Document findings**:
   - Create mapping: token path → component names → usage contexts
   - Store for description generation

**Reference**: See `references/figma-integration.md` for detailed inspection workflow

---

### Step 6: Generate Descriptions by Tier

**CRITICAL RULES**:
1. Descriptions must NEVER be based solely on token names
2. Follow the **Token Description Writing Guide** framework for tone selection
3. Match constraint level to token stability and usage breadth

**Reference**: See `TOKEN-DESCRIPTION-WRITING-GUIDE.md` for complete framework

---

#### Description Framework: Tone Selection

Before generating descriptions, assess each token:

**Decision Questions**:
1. Is the token's purpose stable or still evolving?
2. Does it serve 1-2 uses or 3+ contexts?
3. Are there critical constraints (mode behavior, usage limits)?
4. What information does the user need to select correctly?

**Tone Guide**:
- **Declarative** (identity): Core tokens with self-evident purpose → `"XS corner radius"`
- **Factual** (definitional): Semantic tokens with stable, clear purpose → `"High-emphasis fills for buttons, icon buttons, and toggle buttons."`
- **Directive** (prescriptive): Specific job, critical constraint → `"Use for text that explains expected input to the user."`
- **Observational** (flexible): Multiple contexts (3+), evolving purpose → `"Commonly used for long-form body text, medium-emphasis small titles, and helper text."`
- **Behavioral** (dynamic): Mode-dependent or state-dependent → `"Text that inverts with mode. Light on dark, dark on light."`

---

#### When to Use "Commonly used for"

**Use when**:
- ONE token serves MULTIPLE distinct purposes (3+ use cases)
- Token is intentionally flexible (emphasis-agnostic, multi-purpose)
- Purpose is still evolving or expanding

**Don't use when**:
- Relationship is definitional (token IS for that component)
- Example: ❌ "Commonly used for buttons" → ✅ "High-emphasis fills for buttons, icon buttons, and toggle buttons."

---

#### Tier 1: Core Tokens (Declarative/Identity)

**Approach**: Simple identity statements. Self-evident purpose.

**Patterns**:
- Dimension: `"{Size} spacing/dimension"` OR `"Base spacing unit. Foundation for scale."` (if foundational)
- Border radius: `"{Size} corner radius."`
- Border width: `"{Size} border width."` + usage context if needed
- Typography: `"{Property description}. {Context if needed}."`

**Examples**:
- `core.dimension.100` → `"Base spacing unit. Foundation for scale."`
- `core.border.radius.m` → `"Medium corner radius."`
- `core.border.width.xs` → `"XS border width. Default for most borders."`
- `core.typography.font-weight.bold` → `"Bold weight (700)."`

**Rationale**: Core tokens are primitives. Identity guides usage without directive.

---

#### Tier 2: Semantic Tokens (Context-Dependent Tone)

**Approach**: Choose tone based on token stability and usage breadth.

**Pattern Selection**:

**For stable, single-purpose tokens** (Factual/Definitional):
- Interactive emphasis levels: `"{Emphasis level}-emphasis {property} for {components}."`
  - Example: `"High-emphasis fills for buttons, icon buttons, and toggle buttons."`
- State variations: `"{Emphasis level}-emphasis {property} {state}."`
  - Example: `"High-emphasis fills on hover."`

**For multi-purpose tokens** (Observational/Flexible):
- Text secondary: `"Commonly used for {context 1}, {context 2}, and {context 3}."`
  - Example: `"Commonly used for long-form body text, medium-emphasis small titles, and helper text."`
- Interactive neutral: `"Neutral interactive {property}. Commonly used for {contexts}."`
  - Example: `"Neutral interactive fills. Commonly used for menu items, links, cards, or object lists."`

**For behavioral tokens** (Dynamic):
- Mode-switching: `"{Behavior description}. {State details}."`
  - Example: `"Text that inverts with mode. Light on dark, dark on light."`
- Mode-static: `"{Context description}. {Invariant behavior}."`
  - Example: `"Text on non-canvas, usually dark backgrounds. Text is always white between modes."`

**For constraint tokens** (Directive):
- Specific purpose: `"Use for {specific purpose/context}."`
  - Example: `"Use for text that explains expected input to the user."`
- Usage limits: `"{Property description}. {Constraint}."`
  - Example: `"Medium border width. Used rarely."`

**If Figma context available**:
- Use actual component names from inspection
- Verify emphasis levels match actual usage
- Document multi-purpose tokens vs single-purpose

**If NO Figma context**:
1. Generate provisional description using appropriate tone
2. Flag for user review (Step 7)
3. Document user reasoning

---

#### Tier 3: Component Tokens (Factual/Implementation-Specific)

**Approach**: State the relationship. Property + Component + Size.

**Pattern**: `"{Property} for {size} {component}."`

**Examples**:
- `button.spacing.m.verticalPadding` → `"Vertical padding for medium buttons."`
- `input.height.s` → `"Height for small inputs."`
- `card.gap.content` → `"Gap between card content elements."`

**For state variations**:
- Default: Full context
- Other states: `"{Property} {state}."`

**If Figma context available**:
- Verify sizing from component inspection
- Confirm component usage

**If NO Figma context**:
1. Generate provisional description
2. Flag for user review (Step 7)

---

### Step 7: User Review for Tokens Without Figma Context

**For each semantic/component token lacking Figma context**:

1. **Present provisional description** using AskUserQuestion:

```javascript
AskUserQuestion({
  questions: [{
    question: "Token '{token_path}' lacks Figma component usage data. The provisional description is: '{provisional_desc}'. Is this accurate?",
    header: "Review Token",
    multiSelect: false,
    options: [
      {
        label: "Accept description",
        description: "The provisional description is accurate"
      },
      {
        label: "Change description",
        description: "Provide a corrected description"
      }
    ]
  }]
})
```

2. **If user changes description**:
   - Ask: "What should the description be and why?"
   - Use their reasoning to:
     - Update the token description
     - Document in FIGMA-TOKEN-USAGE-MAPPING.md
     - Add pattern insight to TOKEN-DESCRIPTIONS.md
     - Update architectural notes if relevant

3. **Example interaction**:
   ```
   Token: semantic.color.interactive.tertiary.fill.default
   Provisional: "Use for tertiary actions. Low-emphasis buttons."

   User changes to: "Use for ghost buttons. Cards/banners."
   Reasoning: "This token is actually used for ghost-style buttons in cards and banner components, not general tertiary actions."

   Actions:
   - Update token description ✓
   - Document in FIGMA-TOKEN-USAGE-MAPPING.md: token → ghost buttons (cards, banners)
   - Note in TOKEN-DESCRIPTIONS.md: tertiary = ghost style, not priority level
   ```

**This ensures descriptions are always grounded in real context.**

---

### Step 8: Apply Descriptions to tokens.json

1. **Traverse token tree** recursively
2. **For each token**:
   - Identify tier (core/semantic/component)
   - Select appropriate pattern from templates
   - Generate description
   - Add/update `description` field (or `$description` if that's the convention)
3. **Track changes**:
   - Count of descriptions added
   - Count of descriptions updated
   - Tokens that couldn't be matched

4. **Write updated tokens.json** using Edit or Write tool

---

### Step 9: Validation

Run validation checks on generated descriptions:

```bash
python .claude/skills/token-describer/scripts/validate-descriptions.py path/to/tokens.json
```

Or with absolute path:
```bash
python3 "$(pwd)/.claude/skills/token-describer/scripts/validate-descriptions.py" path/to/tokens.json
```

**Validation checks** (from TOKEN-DESCRIPTION-WRITING-GUIDE.md):
- ✓ Length: 20-60 characters (concise but clear)
- ✓ Platform-agnostic: No px, pt, rem, dp, iOS, Android, Web references
- ✓ Component mentions: Semantic/component tokens mention relevant components
- ✓ Behavioral clarity: Mode-dependent tokens explain behavior
- ✓ Natural grammar: Prepositions match semantic intent
- ✓ Tone consistency: Similar tokens use similar tone patterns
- ✓ AI-friendly: Provides decision criteria, not just labels
- ✓ Figma context: Documented or user-reviewed

**If validation fails**:
- Review error/warning messages
- Fix critical issues (unit references, missing descriptions)
- Re-run validation

---

### Step 10: Generate Documentation

Create comprehensive documentation files in the same directory as tokens.json:

#### 1. TOKEN-DESCRIPTION-WRITING-GUIDE.md

**Content**:
- Philosophy: Context-appropriate precision
- Core principle: Match constraint to stability
- Decision framework (4 key questions)
- Tone guide (5 tone patterns with examples)
- Pattern recognition ("commonly used for" rules)
- Natural grammar = semantic intent
- Common scenarios with rationale
- Anti-patterns to avoid
- Validation checklist

**Source**: Copy from project root if it exists, or generate using the framework principles

**Purpose**: Reference for maintaining and extending token descriptions

---

#### 2. TOKEN-DESCRIPTIONS.md

**Content**:
- Core principles (concise, platform-agnostic, purpose-driven)
- Description patterns by tier
- Decision-making process for new tokens
- Catalog of patterns used
- User reasoning for tokens without Figma context
- Common mistakes and fixes
- Maintenance checklist
- Reference to TOKEN-DESCRIPTION-WRITING-GUIDE.md

**Source**: Based on `references/token-patterns.md` and `references/description-templates.md`

---

#### 2. TOKEN-USAGE.md

**Content**:
- Quick decision tree for token selection
- When to use each tier (with examples)
- Semantic token selection guide
- Component token patterns
- Common scenarios (correct/incorrect examples)
- Anti-patterns to avoid

**Purpose**: Help designers/developers choose the right tokens

---

#### 3. FIGMA-TOKEN-USAGE-MAPPING.md

**Content** (always create, even if partial Figma data):
- Tokens WITH Figma context:
  - Component names
  - Variable bindings
  - Usage contexts
- Tokens WITHOUT Figma context:
  - Provisional descriptions
  - User-provided reasoning
  - Actual usage notes

**Format**:
```markdown
## Token: color.interactive.primary.fill.default

**Components using this token**:
- Button (Solid variant) - Container fill
- Card (Primary action) - Background

**Usage contexts**: Primary CTAs, High-emphasis actions

**Description**: "Use for solid buttons. Primary CTAs."

---

## Tokens Without Figma Context

### color.interactive.control.fill.default

**Provisional**: "Use for control fills. Toggles/checkboxes."
**User review**: Changed to "Use for checkbox backgrounds. Form controls."
**Reasoning**: Only used for checkboxes in codebase, not toggles.
```

**Purpose**: Reference for future updates and maintenance

---

#### 4. TOKEN-ARCHITECTURE.md

**Content**:
- Three-tier architecture explanation
- Token categories breakdown
- Naming conventions
- Design principles
- Figma variable collection mappings

**Purpose**: System structure reference

---

#### 5. MIGRATION-GUIDE.md

**Content**:
- How to deploy token updates
- Integration steps (Figma, code)
- Testing checklist
- Rollout recommendations

**Purpose**: Deployment guidance

---

### Step 11: Git Finalization (Conditional)

**If Git workflow**:

1. **Stage changes**:
   ```bash
   git add tokens.json *.md
   ```

2. **Create commit**:
   ```bash
   git commit -m "$(cat <<'EOF'
   Add comprehensive token descriptions

   - Generated descriptions for {count} tokens
   - {percent}% description coverage achieved
   - Figma-informed descriptions based on component inspection
   - Created comprehensive documentation

   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
   EOF
   )"
   ```

3. **Push branch**:
   ```bash
   git push -u origin {branch_name}
   ```

4. **Provide PR instructions** (if user requested):
   ```
   ✅ Branch pushed successfully!

   Next steps:
   1. Go to your repository on GitHub/GitLab
   2. Create a pull request from branch '{branch_name}'
   3. Title: "Add token descriptions"
   4. Description:
      - {count} tokens with descriptions
      - {percent}% coverage
      - Figma-informed approach
      - Documentation created

   PR link will be available at:
   {repo_url}/compare/{branch_name}
   ```

**If local workflow**:
- Inform user that changes are complete
- List files modified/created

---

### Step 12: Summary Report

Provide final summary to user:

```
✅ Token Description Generation Complete

📊 Summary:
- Total tokens processed: {count}
- Descriptions added: {count}
- Descriptions updated: {count}
- Coverage: {before}% → {after}%

📁 Files created/updated:
- tokens.json (updated with descriptions)
- TOKEN-DESCRIPTIONS.md (pattern guide)
- TOKEN-USAGE.md (usage guidelines)
- FIGMA-TOKEN-USAGE-MAPPING.md (component mappings)
- TOKEN-ARCHITECTURE.md (system structure)
- MIGRATION-GUIDE.md (deployment guide)

✅ Quality Metrics:
- Description length compliance: {percent}%
- No unit references: ✓
- No platform references: ✓
- Component mentions: {percent}%
- Figma context: {with_figma} tokens, {without_figma} user-reviewed

🎯 Next Steps:
1. Review generated descriptions in tokens.json
2. Check documentation files
3. Run tests/build to verify token structure
{4. Create PR from branch '{branch_name}' (if Git workflow)}
```

---

## Key Design Decisions

### 1. Description Writing Framework (MANDATORY)

**Why**: Descriptions must provide context-appropriate precision—tight constraints where needed, flexibility where useful.

**Principle**: Match constraint to stability
- High constraint → Precise, directive language
- Medium constraint → Factual, definitional language
- Low constraint → Observational, flexible language

**Framework**: See `TOKEN-DESCRIPTION-WRITING-GUIDE.md` for complete methodology

**Key distinctions**:
- **Definitional** ("for buttons") vs **Observational** ("commonly used for")
  - Definitional: Token IS for that component (stable, 1-2 uses)
  - Observational: Token serves multiple contexts (flexible, 3+ uses)
- **Behavioral tokens** must explain mode/state behavior
- **Natural grammar** matches semantic intent (for/as/in/on/when)

**Example**:
- Token with stable, single purpose: `"High-emphasis fills for buttons, icon buttons, and toggle buttons."`
- Token with multiple purposes: `"Commonly used for long-form body text, medium-emphasis small titles, and helper text."`
- Behavioral token: `"Text that inverts with mode. Light on dark, dark on light."`

---

### 2. Figma-Informed Approach (MANDATORY)

**Why**: Token names can be misleading. Real component usage is the source of truth.

**Example**:
- Token name: `interactive.tertiary.*`
- Name assumption: "For tertiary priority buttons"
- Actual Figma usage: Ghost buttons in cards and banner close buttons
- Correct description: "Low-emphasis fills for buttons, icon buttons, and toggle buttons." (factual, not prescriptive about button style)

**Implementation**:
- Always attempt Figma integration
- For tokens without Figma context, require user review
- Apply appropriate tone based on token stability and usage breadth
- Document user reasoning for future reference

---

### 2. User Review Loop

**Why**: Ensures descriptions are never based on assumptions.

**When triggered**:
- Semantic/component tokens without Figma bindings
- User has domain knowledge not captured in design file

**Process**:
1. Generate provisional description
2. Present to user with AskUserQuestion
3. Ask why changes are needed
4. Document reasoning in multiple places
5. Update pattern library with insights

---

### 3. Progressive Disclosure

**Why**: Keep skill execution fast, reference detailed docs when needed.

**Structure**:
- SKILL.md: ~2,000 words, workflow-focused
- references/*: Detailed patterns, templates, integration guides
- examples/*: Working samples for each tier

---

### 4. Validation Before Finalization

**Why**: Consistent quality across different users and design systems.

**Automated checks**:
- Length compliance
- No platform-specific terms
- Component mentions
- Figma context or user review

---

## Reference Files

This skill references detailed documentation:

**Core Framework**:
- **TOKEN-DESCRIPTION-WRITING-GUIDE.md**: Complete framework for tone selection, decision-making, and pattern application (generated/copied during Step 10)

**Supporting References**:
- **references/token-patterns.md**: Three-tier architecture, naming conventions, pattern recognition
- **references/description-templates.md**: Complete pattern library (Python-style dictionaries)
- **references/figma-integration.md**: Figma MCP workflow, component inspection, variable bindings

**Examples**:
- **examples/core-tokens.json**: Core token examples with descriptions
- **examples/semantic-tokens.json**: Semantic token examples with Figma-informed descriptions
- **examples/component-tokens.json**: Component token examples

**Validation**:
- **scripts/validate-descriptions.py**: Automated quality validation

---

## Error Handling

### If tokens.json not found
- Search current directory and subdirectories
- Ask user for correct path

### If tokens.json is invalid JSON
- Report parsing error with line number
- Ask user to fix JSON syntax first

### If Figma MCP not available
- Warn user that Figma integration is unavailable
- Proceed with pattern-based descriptions
- Flag all semantic/component tokens for user review

### If validation fails
- Show errors/warnings
- Offer to fix automatically (unit references, length)
- Re-run validation after fixes

### If Git operations fail
- Show error message
- Offer to continue with local file workflow instead

---

## Usage Examples

### Example 1: Local File with Figma

```
User: /token-describer tokens.json

Skill: Are you working with a local file or a Git repository?
User: Local file

Skill: Do you have a Figma design file to inspect?
User: Yes - https://figma.com/file/ABC123.../Design-System

Skill:
- Loads Figma MCP tools
- Analyzes tokens.json (756 tokens, 2% coverage)
- Inspects Figma components (Button, Input, Card, Banner)
- Generates descriptions based on actual usage
- Updates tokens.json
- Creates documentation files
- Runs validation (passes)

Report: ✅ 756 tokens processed, 100% coverage, documentation created
```

---

### Example 2: Git Workflow without Figma

```
User: /token-describer path/to/tokens.json

Skill: Are you working with a local file or a Git repository?
User: Git repository

Skill: Repository URL?
User: https://github.com/org/design-system

Skill: Branch name?
User: add-token-descriptions

Skill: Create PR at the end?
User: Yes

Skill: Do you have a Figma design file?
User: No

Skill:
- Clones repository
- Creates branch 'add-token-descriptions'
- Analyzes tokens
- Generates provisional descriptions
- Flags semantic tokens for review
- Presents provisional descriptions to user
- User confirms or corrects
- Documents user reasoning
- Updates tokens.json
- Creates documentation
- Validates (passes)
- Commits changes
- Pushes branch
- Provides PR link

Report: ✅ Branch pushed, ready for PR
```

---

## Customization

This skill can be adapted for:
- Different token formats (Style Dictionary, Theo)
- Additional token tiers
- Custom validation rules
- Organization-specific patterns

To customize:
1. Edit `references/description-templates.md` to add patterns
2. Update `references/token-patterns.md` for new tier logic
3. Modify `scripts/validate-descriptions.py` for custom checks

---

## Version History

**Version 1.0.0** (2026-02-14)
- Initial release
- Figma MCP integration
- Three-tier token support
- User review workflow for tokens without Figma context
- Comprehensive documentation generation
- Git workflow support

---

## Credits

Based on the GDS-E token description project (February 2026), which successfully added descriptions to 756 tokens using Figma-informed patterns.

**Research sources**: Polaris, Atlassian Design System, Nordhealth, Carbon Design System, Helios, Adobe Spectrum, GitHub Primer.
