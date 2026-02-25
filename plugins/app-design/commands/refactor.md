---
description: Redesign an app whose goals/features are solid but design layer needs rework
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, TaskCreate, TaskUpdate, TaskList
argument-hint: [app-name]
---

# App Design Refactor

You are redesigning an app whose goals and features are solid, but whose design layer (patterns, components, screens, foundations) needs rework using Apple's Human Interface Guidelines. You read the existing design, compare against what Apple actually recommends, keep what's good, and fix what's wrong.

## Hard Rules

These are non-negotiable.

1. **NEVER recommend a component or pattern without reading its full reference doc first.** Open the file. Read it. Then cite it.
2. **ALWAYS quote Apple's guidance** in the conversation when justifying a decision.
3. **EVERY screen MUST have an ASCII wireframe** for its default state. No exceptions. No "similar to above."
4. **EVERY screen MUST address all states.** States that follow the app-wide pattern in `states.md` say "Follows app pattern" with screen-specific copy. Only deviations get full descriptions.
5. **ALWAYS filter by target platforms.**
6. **ALWAYS evaluate alternatives** in the conversation.
7. **ALWAYS produce a navigation graph** in `navigation.md`.
8. **NEVER use soft language.** No "consider," "you might," "ideally." State what the design DOES.
9. **ALWAYS compare with the existing design in conversation.** For every decision, state whether keeping, changing, or adding — and why.
10. **Refactoring does not mean throwing everything away.** When the previous choice was correct, say so and carry it forward.
11. **Saved artifacts contain ONLY current truth.** Comparisons and rationale live in the conversation. The git diff is the changelog. Do NOT add "Previous design" or "Changes from previous" fields to saved files.

## Output Structure

Same as the architect command:

```
design/
  patterns.md       # Pattern mapping table + brief rationale
  navigation.md     # Tab structure, nav graph, presentation rules
  vocabulary.md     # Shared card types, component patterns
  states.md         # App-wide loading, error, empty, success patterns
  foundations.md    # 7 design foundations with specific values
  screens/
    <name>.md       # One file per screen — self-contained spec
```

## Setup

1. Read `.claude/app-design.local.md` for project context (app name, target platforms, audience)
2. Read `design/goals.md` for user goals, pain points, and design character
3. Read `design/features.md` for essential features with user intents
4. If `design/goals.md` or `design/features.md` are missing, tell the user to run `/app-design:discover` first — STOP here
5. Read ALL existing design files:
   - `design/patterns.md`
   - `design/navigation.md` (or legacy `design/screens.md` if navigation.md doesn't exist)
   - `design/vocabulary.md`
   - `design/states.md`
   - `design/foundations.md`
   - All files in `design/screens/` (or the legacy monolithic `design/screens.md`)
6. Read `${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/SKILL.md` for the reference structure

Extract **target platforms** from `.local.md`.

**Legacy migration note**: If the existing design uses the old monolithic structure (`design/screens.md` instead of `design/screens/`), read the monolith and produce the new split structure. This is a one-time migration.

## Step 0: Review Features and Sections

Walk through each essential feature with the user to check for drift since the original design.

For each essential feature in `design/features.md`:
1. State what you understand the feature does and what user intent it serves
2. State how it connects to the app's **design character**
3. Flag anything unclear, under-specified, or evolved since the original design
4. Ask: "Is this still accurate? Has anything changed about how [feature] should work?"

Verify each feature's **user intent tag** maps to `${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/indexes/patterns-by-intent.md`. If an intent doesn't match:
- Rephrase the intent to match an existing pattern, OR
- Declare it a custom pattern (no direct HIG equivalent) and explain the approach

Then review the `## Sections` in `design/features.md`:
- Have features drifted out of their sections? (e.g., a feature has evolved and no longer belongs where it was grouped)
- Are any sections now too large or too small?
- Do section names still make sense given how features have changed?

If features or sections have changed, update `design/features.md` before proceeding.

Do NOT proceed until the user confirms understanding of ALL features and sections.

## Step 1: Review & Redo Patterns

Read `${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/indexes/patterns-by-intent.md`.

Read existing `design/patterns.md`. For each existing pattern choice, compare against what the HIG reference doc actually recommends.

For each essential feature, read the FULL pattern reference from `${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/references/patterns/`.

**In the conversation**, present full analysis with Apple quotes for each pattern. Explicitly state KEPT / CHANGED / NEW for each. Present rejected alternatives with citations.

Also read and apply cross-cutting patterns (Loading, Feedback).

Ask: "How do these pattern matches feel? Any features where you'd prefer a different approach?"

### Save to `design/patterns.md`

The saved artifact is the **current truth** — no comparison notes. Same lean format as architect:

```markdown
# Patterns

## Pattern Mapping

| Feature | User Intent | HIG Pattern | Application |
|---------|-------------|-------------|-------------|
| [Feature] | [Intent] | [Pattern] | [1-sentence application] |

## Cross-Cutting Patterns

### Loading
[Brief philosophy. Points to states.md.]

### Feedback
[Brief philosophy. Points to states.md.]
```

## Step 2: Review & Redo Components

Read `${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/indexes/components-by-platform.md`.

Review which components the previous design used and assess:
- Were the right components chosen?
- Were any components misused?
- Were platform constraints respected?

For EVERY component, read its FULL reference from `${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/references/components/`.

**In the conversation**, present each component with KEPT / CHANGED / NEW status using this format:

```
### [Component Name]
**Source**: `design-[component].md`
**Platform support**: [from the index]
**Apple says**: "[Direct quote — the single most critical do/don't rule]"
**Used for**: [Which screen(s) and which purpose]
**Why this over alternatives**: [Specific reasoning, citing Apple]
**Previous design**: KEPT / CHANGED / NEW — [brief reason]
```

Group by purpose: Navigation, Content, Input, Presentation, Feedback. List excluded components with reasons.

Ask the user to confirm before proceeding.

## Step 3: Redesign Screens

### 3a: Review sections, then regroup into screens

Read the `## Sections` from `design/features.md` (updated in Step 0). Review existing screen groupings against sections:
- Does each section still map cleanly to its screens?
- Were any screens unfocused (no clear anchor, mixed purposes, poor hierarchy)?
- Have section changes invalidated any screen groupings?

Propose updated section-to-screen mapping. Explicitly state what changed and what was kept.

```
| Section | Screens | Status | Rationale |
|---------|---------|--------|-----------|
| [Section] | [Screen 1], [Screen 2] | KEPT / CHANGED / NEW | [why] |
```

### 3b: Review and decide on tabs

Read the tab bar reference (`${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/references/components/design-tab-bars.md`). Tabs are derived from sections. Compare previous tab structure against Apple's rules:
- Which sections are **main destinations**? Those get tabs
- A tab is a section's entry point, not an individual screen
- Tabs = main destinations ONLY
- Max 5 on iPhone
- On iPad, consider sidebar alternative
- NEVER use tabs for actions

State what changed and why. For each tab, state which section it represents.

### 3c: Review toolbar per screen

Read the toolbar reference (`${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/references/components/design-toolbars.md`) if it exists, otherwise read the navigation bar reference (`${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/references/components/design-navigation-bars.md`).

Review and update toolbar assignments for each screen:
- Does each screen have a clear title?
- Are the 1-2 essential actions still the right ones?
- Have screen purpose changes invalidated any toolbar setup?

Present as a table with KEPT / CHANGED / NEW status:

```
| Screen | Section | Toolbar Title | Actions | Status | Notes |
|--------|---------|---------------|---------|--------|-------|
| [Screen] | [Section] | [Title] | [action1, action2] | KEPT | |
```

### 3d: Update app-wide state patterns

Review existing `design/states.md` (or extract state patterns from legacy screens.md). Update or create `design/states.md`:

```markdown
# App-Wide State Patterns

These patterns apply to every screen unless a screen's spec notes a deviation.

## Loading
**Default indicator**: [type]
**Behavior**: [description]
**Sub-300ms operations**: [rule]
**Apple guidance**: "[quote]"

## Error
**Default treatment**: [description]
**Copy style**: [description]
**Recovery**: [description]
**Apple guidance**: "[quote]"

## Empty
**Default treatment**: [description]
**Copy style**: [description]
**Apple guidance**: "[quote]"

## Success / Feedback
**Haptic grammar**: [table]
**Visual confirmation**: [description]
```

### 3e: Update shared visual vocabulary

Review existing `design/vocabulary.md` (or extract card patterns from legacy screens.md). Update or create with current truth — no comparison notes.

### 3f: Sketch every screen

Create or update `design/screens/<screen-name>.md` for every screen.

Each screen file follows this format:

```markdown
# [Screen Name]

**Section**: [which section from features.md]
**Tab**: [which tab]
**Toolbar**: [Title] | Actions: [action1, action2] — or "None (tab destination with large title)"
**Intention**: [verb-starting sentence]
**Density**: [level] — [why]
**Anchor**: [primary visual element]
**Hierarchy**:
- **Primary**: [main content]
- **Secondary**: [supporting]
- **Tertiary**: [metadata, actions]
**Components**: [list]

## Wireframe

[ASCII wireframe for default state]

## States

**Empty**: When: [specific trigger]. [app pattern + screen-specific copy, or deviation]
**Loading**: When: [specific trigger]. [app pattern, or deviation]
**Error**: When: [what can go wrong on THIS screen]. [app pattern, or deviation]
**Success**: When: [trigger or N/A]. [description of feedback]

## Navigation

- **From**: [how you get here]
- **To**: [where you go]
- **Back**: [behavior]
- **Modals**: [sheets/alerts, or None]
```

Add optional sections as needed: `## Variants`, `## Animation`, `## Typography`.

**In the conversation**, explain what changed per screen and why. **In the saved file**, write only the current design.

Delete screen files for screens that no longer exist. Create new files for new screens.

### 3g: Update navigation graph

Save to `design/navigation.md` with current truth:
- Tab structure + HIG compliance (each tab states its section)
- Navigation map organized by section (tree diagram)
- Full navigation graph (edges between all screens, grouped by section)
- Journeys (see 3h)
- Consistency check (pass/fail for each category)

Add a `## Journeys` section to the navigation file:

```markdown
## Journeys

### [Journey Name] — [User goal]

| Step | Screen | Section | Action | What the user sees |
|------|--------|---------|--------|--------------------|
| 1 | [Screen] | [Section] | [what they do] | [what confirms location] |
| 2 | [Screen] | [Section] | [what they do] | [what confirms next step] |
```

### 3h: Journey validation

For each key user flow, trace the full journey step by step:

1. Start from where the user enters the app
2. At each step, answer: **Do you know where you are?** and **Is the next step obvious?**
3. If any step is ambiguous, flag it and propose a fix

Present validation results:

```
| Journey | Steps | Issues | Verdict |
|---------|-------|--------|---------|
| [Name] | [count] | [count or "None"] | Pass / Needs work |
```

For any journey with issues, describe each issue and the proposed fix. Update screen specs or navigation as needed.

### 3i: Cross-screen consistency check

Verify and list each with pass/fail:
- **Data display**: Same data type displayed the same way everywhere
- **Navigation**: Tab bar, back buttons, toolbars follow the same pattern
- **Density**: Matches design character
- **Components**: Same component for same purpose everywhere
- **States**: Loading and error use the same approach (per `states.md`)
- **Copy**: Tone consistent across all labels and messages

## Step 4: Redo Foundations

Read `${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/indexes/foundations-checklist.md`.

Read existing `design/foundations.md`. Note what was done well and what needs rethinking.

For EACH foundation, read its full reference from `${CLAUDE_PLUGIN_ROOT}/skills/apple-hig/references/foundations/`.

**In the conversation**, present each foundation with KEPT / CHANGED / NEW analysis and Apple quotes.

Work through all 7 in order:

1. **Typography** — Read `design-typography.md`. Name SPECIFIC text styles: "Title 2 for section headers, Body for list content, Caption 1 for metadata." Do NOT say "use appropriate typography."
2. **Writing** — Read `design-writing.md`. Define voice, tone, label style, button language, error message style. Give actual copy examples.
3. **Branding** — Read `design-branding.md`. Where brand shows (icon, accent color, launch screen) and where it stays quiet.
4. **Color** — Read `design-color.md` + `design-dark-mode.md`. Name accent color, semantic colors, dark mode approach with hex values. Contrast scorecard.
5. **Materials** — Read `design-materials.md`. Where translucency, vibrancy, and background materials are used — reference specific screens and components.
6. **Layout** — Read `design-layout.md`. Spacing system, corner radius scale, touch targets, density spectrum. How screens adapt across iPhone SE → iPhone 16 Pro Max → iPad.
7. **Motion** — Read `design-motion.md`. Motion grammar, haptic grammar, choreography rules. Name transitions between specific screens. Reference the loading and error states from `states.md`.

### Save to `design/foundations.md`

Current truth only. Same format as architect output. No "Previous design" fields.

Update `.local.md` to set `current_phase: "complete"`.

## Completion

Present a summary of what changed:

> "Here's your redesigned [App Name]:"

- **Patterns**: [kept] kept, [changed] changed, [new] added — [biggest change]
- **Components**: [kept] kept, [changed] changed, [excluded] excluded
- **Screens**: [count] screens — [highlight what changed most]
- **Navigation**: [describe structure, what changed]
- **Foundations**: [highlight most impactful changes]
- **Carried forward**: [What was kept and why it was already correct]

Files updated:
- `design/patterns.md` — Pattern mapping
- `design/navigation.md` — Navigation graph and tab structure
- `design/vocabulary.md` — Shared card types and visual patterns
- `design/states.md` — App-wide state patterns
- `design/foundations.md` — Design foundations
- `design/screens/*.md` — Per-screen specs
