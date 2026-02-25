---
description: Validate design specs against actual code — find gaps between what was designed and what was built
allowed-tools: Read, Write, Edit, Glob, Grep, Task, AskUserQuestion, TaskCreate, TaskUpdate, TaskList
argument-hint: [path-to-source-code]
---

# App Design Validate

You are auditing an app's Swift/SwiftUI code against its design specifications produced by the app-design plugin. Your job is to find every gap between what the design specs say and what the code actually does. You are a skeptic — code is non-compliant until proven compliant with specific evidence.

## Hard Rules

These are non-negotiable.

1. **NEVER declare a requirement "implemented" without quoting the exact code location (file:line) that satisfies it.** If you can't point to the code, it's a gap.
2. **NEVER use soft language.** No "appears to comply," "seems implemented," "likely correct," "should be fine." Either the code does it or it doesn't.
3. **NEVER assume compliance from naming.** A view called `LoadingView` is NOT evidence that loading states are correctly implemented. Read the actual code.
4. **NEVER infer implementation from existence.** A file existing is not compliance. A function existing is not compliance. The actual behavior must match the spec.
5. **EVERY gap must cite the specific spec requirement** (file + section + exact text) **and what the code does instead** (file:line + what it actually does, or "no matching code found").
6. **For EACH screen, check EVERY requirement** — components, states (all 4), navigation, hierarchy. No skipping. No "similar to previous screen."
7. **ALWAYS read the code.** Do not rely on function/class names, file names, or comments to determine compliance. Read the implementation.
8. **Treat absence of evidence as evidence of absence.** If you search and can't find code that handles an error state, that IS a gap — don't speculate that it "might be handled elsewhere."
9. **NEVER batch screens as "all compliant."** Every screen gets its own section with its own evidence. If 5 screens are identical in compliance, write 5 sections anyway.
10. **The spec is the source of truth.** If the code does something the spec doesn't mention, that's "undocumented behavior." If the spec says something the code doesn't do, that's a gap. No exceptions.

## Compact-Resilient Workflow

This command is designed to survive auto-compact. All state lives on disk — never in conversation memory alone.

**Principles:**
- **Write results to `design/validation-report.md` incrementally** — after each step, not all at once at the end
- **Use TaskCreate/TaskUpdate as persistent progress tracking** — tasks survive compact
- **Subagents read files themselves** — pass file paths, not file contents
- **Re-read the report file before each step** to recover context if compact occurred
- **Never hold large amounts of spec/code text in conversation** — read, validate, write results, move on

## Setup

1. Read `.claude/app-design.local.md` for project context (app name, target platforms)
2. Verify design specs exist by checking these paths with Glob:
   - `design/goals.md`
   - `design/features.md`
   - `design/patterns.md`
   - `design/navigation.md`
   - `design/vocabulary.md`
   - `design/states.md`
   - `design/foundations.md`
   - `design/screens/*.md` (must find at least one)
3. If design specs are incomplete, tell the user to run `/app-design:design` first — **STOP here**
4. Identify the source code location:
   - If the user provided a path argument, use that as the root for Swift file search
   - Otherwise, search for Swift files: `**/*.swift`
   - If no Swift files found, ask the user where the source code is — **STOP here**
5. List all screen spec files and all Swift source files — **do NOT read them yet**

## Step 0: Inventory & Report Scaffold

Before validating anything, map the design to the code and write the initial report.

### 0a: Screen-to-Code Mapping

For each screen spec in `design/screens/`:
1. Read the screen spec header only (first ~20 lines — enough to get name, intention, components)
2. Search the codebase for the corresponding view/screen:
   - Search by name (screen name → View name)
   - Search by purpose (grep for key components, content types, or navigation targets)
   - Search by content (grep for strings, labels, or identifiers mentioned in the spec)
3. Record the mapping: spec file → code file(s), or "NOT FOUND"

For each View/Screen in the codebase that doesn't map to a spec:
1. Note it as "code without spec"

### 0b: Section Integrity Check

Read the `## Sections` from `design/features.md` and verify structural integrity before validating code:

1. **Every screen's `**Section**` field maps to a section in `features.md`** — read the header of each screen spec and check its Section field against the sections list. Flag any screen pointing to a non-existent section.
2. **Every section has at least one screen** — for each section in `features.md`, verify at least one screen spec lists it in the Section field. Flag orphaned sections.
3. **Every feature appears in at least one section** — cross-reference the essential features list against the sections table. Flag any feature not assigned to a section.

Add results to the report scaffold under a new `## Section Integrity` heading (after Screen-to-Code Mapping, before Cross-Cutting Code Locations).

### 0c: Cross-Cutting Code Inventory

Use Grep to identify code locations for:
- **Navigation**: Files containing NavigationStack, NavigationLink, TabView, sheet, fullScreenCover
- **Shared components**: Reusable view structs used across multiple screens
- **State handling**: Loading views, error views, empty state views, progress indicators
- **Design tokens**: Color definitions, font/typography constants, spacing constants

### 0d: Write Report Scaffold to Disk

**Write `design/validation-report.md` NOW** with the inventory and placeholder sections:

```markdown
# Validation Report

**Generated**: [today's date]
**App**: [name from .local.md]
**Design spec files**: [count]
**Source files analyzed**: [count]
**Screens validated**: pending

## Screen-to-Code Mapping

| Screen Spec | Code File(s) | Status |
|-------------|--------------|--------|
| design/screens/home.md | Views/HomeView.swift | Mapped |
| design/screens/settings.md | — | NOT FOUND |
| — | Views/OnboardingView.swift | No spec |

## Section Integrity

| Check | Result | Details |
|-------|--------|---------|
| Every screen Section field maps to features.md | PASS/FAIL | [details] |
| Every section has at least one screen | PASS/FAIL | [details] |
| Every feature appears in at least one section | PASS/FAIL | [details] |

## Cross-Cutting Code Locations

- **Navigation**: [file list]
- **Shared components**: [file list]
- **State handling**: [file list]
- **Design tokens**: [file list]

## Screen Validation

(pending — populated by Step 1)

## Navigation Gaps

(pending — populated by Step 2)

## Vocabulary Gaps

(pending — populated by Step 3)

## States Gaps

(pending — populated by Step 4)

## Foundations Gaps

(pending — populated by Step 5)

## Summary

(pending — populated by Step 6)

## Priority Recommendations

(pending — populated by Step 6)
```

### 0e: Create Tracking Tasks

Create one TaskCreate per remaining step. Each task description MUST include the file paths it needs:

- **Task: "Validate screens"** — description lists every (spec path → code path) mapping
- **Task: "Validate navigation"** — description says "read design/navigation.md, check against [nav code files]"
- **Task: "Validate vocabulary"** — description says "read design/vocabulary.md, check against [shared component files]"
- **Task: "Validate states"** — description says "read design/states.md, check against [state handling files]"
- **Task: "Validate foundations"** — description says "read design/foundations.md, check against [design token files]"
- **Task: "Compile summary"** — description says "read design/validation-report.md, add summary table and priority recommendations"

## Step 1: Parallel Screen Validation

Mark the "Validate screens" task as in_progress.

For EACH mapped screen (spec has matching code), launch a validation subagent using the **Task tool** with `subagent_type: "general-purpose"`. Launch up to 4 in parallel.

Each subagent prompt provides **file paths only** — the subagent reads files itself:

```
You are validating one screen's code against its design spec. You are a skeptic. Code is non-compliant until proven otherwise.

## Files to Read

1. **Screen spec**: [path to design/screens/<name>.md] — read this FIRST
2. **Code file(s)**: [path(s) to Swift file(s)] — read ALL of these
3. **App-wide states**: design/states.md — read this for state pattern compliance
4. **Vocabulary**: design/vocabulary.md — read this if the screen spec references vocabulary items

## What to Check

Read the code file(s). Then check EVERY requirement below. For each, state PASS, FAIL, or PARTIAL with evidence.

**Components**: For each component listed in the spec header's "Components" field:
- Is this HIG component used in the code? Quote the code line (file:line).
- Is it used for the correct purpose per the spec?

**Hierarchy**: Does the code's view body structure match the spec's wireframe?
- Primary element: [quote code or "not found"]
- Secondary element: [quote code or "not found"]
- Tertiary element: [quote code or "not found"]

**States — Empty**:
- Does the code handle the empty state? Quote the conditional (e.g., `if items.isEmpty`).
- Does the trigger match the spec? Quote the condition.
- Does the copy/message match? Quote the string literal from code vs the spec.
- If spec says "Follows app pattern" — does it use the app-wide empty state component from states.md?

**States — Loading**:
- Does the code show a loading indicator? Quote the code.
- Does the indicator type match the spec (skeleton, spinner, etc.)?
- If spec notes a deviation from app pattern, is that deviation implemented?

**States — Error**:
- Does the code handle errors for this screen? Quote the catch/error handling.
- Does the error treatment match the spec (inline banner, alert, etc.)?
- Is recovery implemented as specified (retry button, pull-to-refresh, etc.)?

**States — Success**:
- Is success feedback implemented? Quote the code.
- If haptics are specified, is the correct haptic type used?
- If visual feedback is specified, is it implemented?
- If "N/A" in spec, search for `.sensoryFeedback`, `UINotificationFeedbackGenerator(.success)`, success banner/toast views, or completion animations in this view. If any are found, flag as undocumented success feedback.

**Navigation — From**:
- Can you reach this screen from where the spec says? Find the NavigationLink/sheet/etc. in the source screen's code. Quote it.

**Navigation — To**:
- Does this screen navigate to where the spec says? Quote navigation actions in this screen's code.

**Navigation — Back**:
- Is back behavior correct? (e.g., scroll position preserved, state maintained)

**Navigation — Modals**:
- Are sheets/alerts/action sheets implemented as specified? Quote the `.sheet`/`.alert`/`.actionSheet` modifiers.
- If "None" in spec, search for `.sheet`, `.alert`, `.actionSheet`, `.fullScreenCover` modifiers in this view's code. If any are found, flag as "undocumented modal." (Cross-screen modal flows are validated separately.)

## Output Format

Return EXACTLY this structure:

### [Screen Name]

**Spec**: `[spec path]`
**Code**: `[code path]`
**Result**: X/Y requirements pass, Z gaps found

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | ... | PASS/FAIL/PARTIAL | ... |

**Gaps**:
1. [Gap with spec reference and code evidence]
```

After each batch of subagents completes, **immediately append their results** to `design/validation-report.md` under the `## Screen Validation` section. Use the Edit tool to replace `(pending — populated by Step 1)` with the actual results (on first batch) or append after existing results (on subsequent batches).

For screens where the spec exists but NO code was found (from the inventory), append a section with every requirement marked FAIL: "No code file found."

Mark the "Validate screens" task as completed.

## Step 2: Navigation Validation

Mark the "Validate navigation" task as in_progress.

**Re-read `design/validation-report.md`** to see the inventory (screen-to-code mapping and cross-cutting code locations). Then read `design/navigation.md`.

### 2a: Tab Structure

- Read the tab bar definition from the spec
- Find the TabView in code — quote the file:line
- Check: correct number of tabs, correct labels, correct icons, correct order
- For each tab: quote the spec requirement alongside the code

### 2b: Navigation Graph Edges

For EVERY edge in the navigation graph (the `[Screen A] --action--> [Screen B]` lines):
- Find the corresponding NavigationLink / sheet / fullScreenCover / navigationDestination in code
- Quote the code line
- Or mark as "EDGE NOT FOUND"

For every navigation action in code NOT in the spec's navigation graph:
- Flag as "undocumented navigation"

### 2c: Consistency Check

The spec's consistency check lists 6 criteria with pass/fail. Verify each against actual code:
- **Data display**: Same data type rendered the same way everywhere?
- **Navigation**: Consistent navigation patterns across screens?
- **Density**: Visual density matches design character?
- **Components**: Same component for same purpose?
- **States**: Loading and error consistent per `states.md`?
- **Copy**: Tone consistent across all strings?

**Write results to disk**: Edit `design/validation-report.md` — replace `(pending — populated by Step 2)` with navigation gap findings.

Mark the "Validate navigation" task as completed.

## Step 3: Vocabulary Validation

Mark the "Validate vocabulary" task as in_progress.

Read `design/vocabulary.md`. Then validate against code.

For each card type defined in the vocabulary:
1. Search for the corresponding reusable View component in code
2. If found, check:
   - Leading element matches spec
   - Content element matches spec
   - Trailing element matches spec
   - Identity signal is present
3. Check the usage matrix: for each screen listed, verify the card is actually used there
4. If a card type is NOT implemented as a reusable component (instead duplicated inline in multiple screens), flag as "vocabulary not extracted"

For presentation rules:
- Check that push / sheet / fullScreenCover / alert usage across the codebase matches the rules table in vocabulary.md
- Quote examples of violations

**Write results to disk**: Edit `design/validation-report.md` — replace `(pending — populated by Step 3)` with vocabulary gap findings.

Mark the "Validate vocabulary" task as completed.

## Step 4: States Validation

Mark the "Validate states" task as in_progress.

Read `design/states.md`. Then validate against code.

For each app-wide pattern, find the default implementation and check consistency:

1. **Loading**: Find the app's default loading component/approach. Search at least 5 screens (or all, if fewer). For each, quote the loading code. Flag any screen that uses a different approach without the spec noting a deviation.
2. **Error**: Find the app's default error handling approach. Search at least 5 screens. For each, quote the error handling code. Flag inconsistencies.
3. **Empty**: Find the app's default empty state approach. Search at least 5 screens. For each, quote the empty state code. Check copy style matches.
4. **Success/Feedback**: Find haptic usage across the codebase. Build a table of actual haptic usage vs. the haptic grammar table in the spec. Flag mismatches.

**Write results to disk**: Edit `design/validation-report.md` — replace `(pending — populated by Step 4)` with states gap findings.

Mark the "Validate states" task as completed.

## Step 5: Foundations Validation

Mark the "Validate foundations" task as in_progress.

Read `design/foundations.md`. Then validate against code.

For each of the 7 foundations:

1. **Typography**: Find text style usage in code (`.font(.title2)`, `.font(.body)`, etc.). Sample at least 5 screens. Do the styles match what the spec assigns? (e.g., spec says "Title 2 for section headers" → are section headers actually `.font(.title2)`?)
2. **Writing**: Sample actual string literals from code. Do they match the voice, tone, and style described? Check button labels, error messages, empty state copy, section headers. Flag strings that violate the copy guidelines.
3. **Branding**: Check accent color definition in Asset Catalog or code. Check that branding is present where spec says and absent where spec says quiet.
4. **Color**: Find color definitions (Asset Catalog, Color extension, SwiftUI Color usage). Check hex values match spec. Check semantic colors for success/warning/error. Check dark mode support (`.colorScheme`, Asset Catalog variants, or conditional colors).
5. **Materials**: Search for `.ultraThinMaterial`, `.thinMaterial`, `.regularMaterial`, `.thickMaterial`, `.ultraThickMaterial`, `.bar` material usage. Do the locations match what the spec prescribes?
6. **Layout**: Check spacing values (padding, spacing in stacks). Check corner radii (`.cornerRadius`, `.clipShape(RoundedRectangle(cornerRadius:))`). Check touch target sizes (frame minWidth/minHeight of 44pt). Sample at least 3 screens.
7. **Motion**: Search for `.animation`, `.transition`, `withAnimation`, `.sensoryFeedback`, `UIImpactFeedbackGenerator`. Do the types and triggers match the motion grammar in the spec?

**Write results to disk**: Edit `design/validation-report.md` — replace `(pending — populated by Step 5)` with foundations gap findings.

Mark the "Validate foundations" task as completed.

## Step 6: Compile Summary

Mark the "Compile summary" task as in_progress.

**Read `design/validation-report.md`** in full — all sections are now populated.

Count totals across all sections. Replace `(pending — populated by Step 6)` in the Summary section with:

```markdown
## Summary

| Area | Checks | Pass | Fail | Partial | Compliance |
|------|--------|------|------|---------|------------|
| Screens | — | — | — | — | —% |
| Navigation | — | — | — | — | —% |
| Vocabulary | — | — | — | — | —% |
| States | — | — | — | — | —% |
| Foundations | — | — | — | — | —% |
| **Total** | **—** | **—** | **—** | **—** | **—%** |
```

Replace `(pending — populated by Step 6)` in Priority Recommendations with:

```markdown
## Priority Recommendations

Ordered by impact (what affects the most screens or the most critical user flows):

1. **[Critical]** [description] — affects [screens/areas]. Spec: [reference]. Code: [what's wrong or missing].
2. **[High]** [description] — affects [screens/areas].
3. **[Medium]** [description] — affects [screens/areas].
4. **[Low]** [description].
```

Update the report header: replace `**Screens validated**: pending` with the actual count.

Mark the "Compile summary" task as completed.

## Completion

Update `.claude/app-design.local.md` to add or update:
```yaml
last_validated: [today's date]
validation_compliance: [overall percentage]
```

Present a summary to the user:

> "Validation complete for [App Name]."

- **Overall compliance**: X%
- **Total checks**: [count]
- **Pass**: [count] | **Fail**: [count] | **Partial**: [count]
- **Missing screens**: [count] specs with no code
- **Undocumented screens**: [count] code with no spec
- **Critical gaps**: [count] — [brief description of the most critical]
- **Report**: `design/validation-report.md`

> "Review the report to decide what to address. Priority recommendations are at the bottom, ordered by impact."
