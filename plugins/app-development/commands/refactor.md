---
description: Rework existing data model and engineering decisions using Apple best practices
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, TaskCreate, TaskUpdate, TaskList
argument-hint: [app-name]
---

# App Development Refactor

You are reworking an app whose data model, persistence strategy, or performance approach needs revision. You read the existing engineering decisions, compare against what Apple actually recommends, keep what's good, and fix what's wrong.

## Hard Rules

These are non-negotiable.

1. **NEVER recommend a change without reading the relevant reference doc first.** Open the file. Read it. Then cite it.
2. **ALWAYS quote Apple's documentation** when justifying a decision.
3. **EVERY entity MUST have its own file** in `engineering/entities/<entity-name>.md`. No monolithic files.
4. **EVERY entity MUST address all data concerns** (validation, defaults, optionality, indexing).
5. **ALWAYS evaluate alternatives** in the conversation.
6. **ALWAYS produce an updated relationship graph** in `engineering/relationships.md`.
7. **NEVER use soft language.** No "consider," "you might." State what the model DOES.
8. **ALWAYS compare with the existing model in conversation.** For every decision, state whether KEEPING, CHANGING, or ADDING — and why.
9. **Refactoring does not mean throwing everything away.** When the previous choice was correct, say so and carry it forward.
10. **Saved artifacts contain ONLY current truth.** Comparisons and rationale live in the conversation. The git diff is the changelog. Do NOT add "Previous model" or "Changes from previous" fields to saved files.

## Output Structure

Same as the model command:

```
engineering/
  requirements.md      # Data requirements (updated if changed)
  persistence.md       # Strategy rationale (current truth)
  relationships.md     # Entity relationship graph (current truth)
  migrations.md        # Schema migration plan (appended)
  performance.md       # Performance plan (updated if exists)
  monitoring.md        # Monitoring plan (updated if exists)
  entities/
    <name>.md          # One file per entity (current truth)
```

## Setup

1. Read `.claude/app-development.local.md` for project context
2. Read `engineering/requirements.md` for data requirements
3. Read `engineering/persistence.md` for current persistence strategy
4. If `engineering/requirements.md` or `engineering/persistence.md` are missing, tell the user to run `/app-development:model` first — STOP here
5. Read ALL existing engineering files:
   - `engineering/relationships.md`
   - `engineering/migrations.md`
   - `engineering/performance.md` (if exists)
   - `engineering/monitoring.md` (if exists)
   - All files in `engineering/entities/`
6. Read `${CLAUDE_PLUGIN_ROOT}/skills/apple-engineering/SKILL.md` for the reference structure
7. Read design artifacts if they exist (for drift detection):
   - Read `design/features.md` → current feature list
   - Read all `design/screens/*.md` → current screen specs
   - Compare against the Design Traceability section in `engineering/requirements.md` (if present)
   - Flag any **new features/screens** in design that don't have engineering coverage
   - Flag any **removed features/screens** whose entities may be orphaned

If design drift is detected, present it before Step 0:

> "Design drift detected since your last engineering pass:"
> - **New in design**: [features/screens added since engineering was defined]
> - **Removed from design**: [features/screens no longer in design — check for orphaned entities]
> - **Unchanged**: [features/screens still aligned]

## Step 0: Review Requirements

Walk through the data requirements with the user to check for drift since the original model.

For each requirement in `engineering/requirements.md`:
1. State what you understand the requirement is
2. Flag anything unclear, under-specified, or evolved
3. Ask: "Is this still accurate? Has anything changed about [requirement]?"

If requirements have changed, update `engineering/requirements.md` before proceeding.

Do NOT proceed until the user confirms understanding of ALL requirements.

## Step 1: Review & Redo Persistence Strategy

Read `${CLAUDE_PLUGIN_ROOT}/skills/apple-engineering/indexes/data-by-need.md`.

Read existing `engineering/persistence.md`. Compare the current strategy against what Apple's reference docs actually recommend for the (possibly updated) requirements.

Read the FULL reference from `${CLAUDE_PLUGIN_ROOT}/skills/apple-engineering/references/data/` for each candidate.

**In the conversation**, present analysis with Apple quotes. Explicitly state KEPT / CHANGED for the persistence strategy. Present alternatives with citations.

Ask: "Is the current persistence approach still right, or should we change it?"

### Save to `engineering/persistence.md`

Current truth only. No comparison notes.

## Step 2: Review & Redo Entities

Read existing entity files from `engineering/entities/`.

For each entity, assess:
- Are the right properties defined?
- Are types correct for the chosen persistence framework?
- Are validation rules complete?
- Are indexes optimized for actual query patterns?
- Are relationships correctly modeled?

**In the conversation**, present each entity with KEPT / CHANGED / NEW / REMOVED status:

```
### [Entity Name] — [KEPT / CHANGED / NEW / REMOVED]
**Reason**: [Why this decision]
**Apple says**: "[Direct quote if relevant]"
**Changes**: [List specific property/relationship changes, or "No changes"]
```

Ask the user to confirm before saving each entity.

### Save to `engineering/entities/<entity-name>.md`

Current truth only. Delete entity files for entities that no longer exist. Create new files for new entities.

## Step 3: Update Relationships

After entity changes, rebuild the relationship graph.

Read the relationship documentation from the reference files.

**In the conversation**, compare the old graph with the new:
- Relationships KEPT with same rules
- Relationships CHANGED (cardinality, delete rule, etc.)
- Relationships ADDED for new entities
- Relationships REMOVED for deleted entities

Walk through cascade analysis for any changed delete rules.

### Save to `engineering/relationships.md`

Current truth only — updated graph, table, cascade analysis.

## Step 4: Update Migration Plan

This is the one file that DOES accumulate history — each schema version builds on the previous.

Read `engineering/migrations.md`. Append the new version:

```markdown
### V[N] — [Description of changes]
**Changes from V[N-1]**:
- [Entity added/removed/changed]
- [Property added/removed/changed]
- [Relationship changed]

**Migration type**: [Lightweight / Staged / Heavyweight]
**Migration steps** (if staged/heavyweight):
1. [Step 1]
2. [Step 2]

**Test plan**:
- [ ] Upgrade from V[N-1] with production-size data
- [ ] Verify no data loss
- [ ] Verify CloudKit schema compatibility (if syncing)
```

## Step 5: Update Performance & Monitoring (If Exists)

If `engineering/performance.md` and `engineering/monitoring.md` exist, review them in light of the model changes:

- Do index changes affect query performance?
- Do new entities need fetch performance tests?
- Do relationship changes affect memory patterns?
- Are monitoring thresholds still appropriate?

**In the conversation**, note which performance/monitoring items need updating. Update files with current truth.

## Completion

Present a summary of what changed:

> "Here's your refactored data model for [App Name]:"

- **Persistence**: [KEPT / CHANGED] — [1-sentence summary]
- **Entities**: [kept] kept, [changed] changed, [new] added, [removed] removed — [biggest change]
- **Relationships**: [describe graph changes]
- **Migrations**: V[N] added — [migration type]
- **Performance**: [updated / unchanged]
- **Carried forward**: [What was kept and why it was already correct]

Files updated:
- `engineering/requirements.md` — Requirements (if changed)
- `engineering/persistence.md` — Persistence strategy
- `engineering/relationships.md` — Entity relationship graph
- `engineering/migrations.md` — Migration plan (new version appended)
- `engineering/entities/*.md` — Per-entity specs
- `engineering/performance.md` — Performance plan (if applicable)
- `engineering/monitoring.md` — Monitoring plan (if applicable)
