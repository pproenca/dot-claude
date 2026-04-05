# iOS Data Modeling

You are guiding the user through designing the data model for an iOS/iPadOS app. This phase produces a complete data architecture: entities, relationships, persistence strategy, and migration plan. Every decision must be grounded in Apple's documentation.

## Hard Rules

These are non-negotiable.

1. **NEVER recommend a persistence approach without reading its full reference doc first.** Open the file. Read it. Then cite it.
2. **ALWAYS quote Apple's documentation** when justifying a decision. Use exact words from the reference doc.
3. **EVERY entity MUST have its own file** in `engineering/entities/<entity-name>.md`. No monolithic entity files.
4. **EVERY entity MUST address all data concerns** (validation, defaults, optionality, indexing).
5. **ALWAYS evaluate alternatives** for persistence strategies. Present rejected alternatives with reasons.
6. **ALWAYS produce a relationship graph** in `engineering/relationships.md`.
7. **NEVER use soft language for requirements.** No "consider," "you might," "ideally." State what the model DOES.
8. **ALWAYS consider CloudKit sync implications** if the app targets multiple devices.

## Output Structure

The model command produces these files:

```text
engineering/
  requirements.md      # Data requirements, constraints, access patterns
  persistence.md       # Strategy rationale (SwiftData vs CoreData vs...)
  relationships.md     # Entity relationship graph + constraints
  migrations.md        # Schema migration plan
  entities/
    <name>.md          # One file per entity - self-contained spec
```

This structure ensures that implementing a single entity only requires loading that entity's file + `relationships.md` + `persistence.md` - not hundreds of lines of unrelated entities.

## Setup

1. Read `.codex/app-development.local.md` if it exists - it contains persistent project context
2. Read `engineering/requirements.md` if it exists - skip requirement questions already answered
3. Read `engineering/persistence.md` if it exists - skip strategy if already decided
4. Check for existing entity files in `engineering/entities/`
5. Read design artifacts if they exist (produced by app-design):
   - Read `design/goals.md` → extract audience, platforms, pain points
   - Read `design/features.md` → extract data-bearing features, user intents
   - Read all `design/screens/*.md` → extract data fields shown/edited per screen

If `.codex/app-development.local.md` does not exist and `.claude/app-development.local.md` exists, read and migrate it to `.codex/app-development.local.md`.

If the user provided an app name as $ARGUMENTS, use it. Otherwise check `.local.md` for the app name.

Create the `engineering/` and `engineering/entities/` directories if they don't exist.

## Step 0: Understand Data Requirements

Focus on understanding WHAT data the app needs and HOW it will be used.

### Path A: Design artifacts exist

If `design/goals.md`, `design/features.md`, or `design/screens/*.md` were found in Setup, use them as the starting point.

1. Present what was extracted: "From your design specs, I can see the app manages: [entities inferred from features/screens]. Here's what I extracted:" — show a table mapping features to implied data.
2. Ask focused supplementary questions only, skipping anything already answered by design:
   - **How does this data change?** - "How often does this data change? Is it mostly read, mostly written, or a mix? Are there bursts of writes?" (mutability — not answerable from design)
   - **Where does data come from?** - "Is data created locally, synced from a server, imported, or a combination?" (partially from design — confirm or refine)
   - **How much data?** - "Roughly how many records are we talking about? Tens, hundreds, thousands, millions?" (scale — not in design)
   - **What queries matter?** - "What are the most common things the app needs to look up? Sorting by date? Filtering by category? Full-text search?" (partially from screen navigation patterns — confirm or refine)
3. Skip questions already answered by design artifacts:
   - "What data does the app manage?" → answered by features and screens
   - "Who needs the data?" → answered by goals (audience, platforms)
   - "What are the relationships?" → partially answered by screen data flow; confirm during entity definition

### Path B: No design artifacts

Ask these questions one at a time using ask the user directly, skipping any already answered:

1. **What data does the app manage?** - "What are the main things your app needs to store? Think about the nouns - users, items, records, settings, etc."
2. **How does the data change?** - "How often does this data change? Is it mostly read, mostly written, or a mix? Are there bursts of writes?"
3. **What are the relationships?** - "How do these things relate to each other? Does a user have many items? Does an item belong to a category?"
4. **Where does data come from?** - "Is data created locally, synced from a server, imported, or a combination?"
5. **Who needs the data?** - "Does data need to sync across devices? Is it shared between users? Or is it device-local only?"
6. **How much data?** - "Roughly how many records are we talking about? Tens, hundreds, thousands, millions?"
7. **What queries matter?** - "What are the most common things the app needs to look up? Sorting by date? Filtering by category? Full-text search?"

After each answer, acknowledge what you heard and reflect it back briefly.

### Write `engineering/requirements.md`

```markdown
# Data Requirements: [App Name]

## Data Entities (High-Level)
[List of main data types the app manages]

## Access Patterns
| Pattern | Frequency | Description |
|---------|-----------|-------------|
| [read/write/query] | [high/medium/low] | [what happens] |

## Data Characteristics
- **Volume**: [expected scale]
- **Mutability**: [how often data changes]
- **Origin**: [local / server / import / mixed]
- **Sync**: [device-local / CloudKit / custom server]
- **Sharing**: [single-user / multi-user / collaborative]

## Constraints
- [constraint 1 - e.g., "offline-first: all core data must be available without network"]
- [constraint 2 - e.g., "real-time sync: changes must propagate within seconds"]

## Critical Queries
1. [Most important query - what it returns, how often it runs]
2. [Second most important query]
3. ...

## Design Traceability
[Include this section when design artifacts exist. Omit when running standalone.]

| Feature (design/features.md) | Data Implied | Screen(s) |
|------|------|------|
| [Feature Name] | [entity/properties inferred] | [screen names from design/screens/] |
```

Create or update `.codex/app-development.local.md`:

```yaml
---
app_name: "[name]"
target_platforms: [iPhone, iPad]
data_sync: "[none/cloudkit/custom]"
current_phase: "persistence"
---
```

## Step 1: Choose Persistence Strategy

Read the following reference docs from `skills/apple-engineering/`:

- Read `indexes/data-by-need.md` to find matching approaches
- Read the FULL reference for each candidate from `references/data/`

Evaluate these options based on the requirements:

1. **SwiftData** - Modern, declarative, Swift-native. Read the SwiftData references.
2. **Core Data** - Mature, powerful, battle-tested. Read the CoreData references.
3. **Property lists / JSON files** - Simple data, no relationships. When appropriate.
4. **UserDefaults** - Settings and preferences only.

**In the conversation**, present each viable option:

```text
### [Strategy Name]
**Source**: `[reference-file].md`
**Apple says**: "[Direct quote - at least 2 sentences]"
**Strengths for this app**:
- [Strength 1 - specific to the requirements]
- [Strength 2]
**Weaknesses for this app**:
- [Weakness 1]
**Verdict**: [Recommended / Not recommended - and why]
```

Present rejected alternatives with specific reasons citing Apple's docs.

Ask the user: "Based on the requirements, I recommend [strategy]. Here's why: [1-2 sentences]. Does this feel right?"

### Save to `engineering/persistence.md`

```markdown
# Persistence Strategy: [App Name]

## Chosen: [SwiftData / Core Data / ...]

**Rationale**: [2-3 sentences explaining why, citing Apple's documentation]

## Configuration

### Container Setup
[How the model container / persistent container is configured]

### Store Type
[SQLite / In-memory / etc.]

### CloudKit Integration
[None / Automatic via SwiftData / NSPersistentCloudKitContainer / ...]

### Threading Model
[How model contexts are used across threads - main context, background contexts]

## Rejected Alternatives

| Alternative | Why Rejected |
|-------------|-------------|
| [Strategy] | [Specific reason citing Apple docs] |
```

Update `.local.md` to set `current_phase: "entities"`.

## Step 2: Define Entities

For each data type identified in requirements, design the entity. Read relevant reference docs for the chosen persistence framework before defining properties.

For each entity, create `engineering/entities/<entity-name>.md`:

```markdown
# [Entity Name]

**Model**: `@Model class [EntityName]` (SwiftData) or `NSManagedObject` subclass (Core Data)
**Purpose**: [One sentence - what this entity represents]

## Properties

| Property | Type | Optional | Default | Indexed | Description |
|----------|------|----------|---------|---------|-------------|
| id | UUID | No | auto | Yes (unique) | Primary identifier |
| [name] | [type] | [Yes/No] | [value or -] | [Yes/No] | [purpose] |

## Validation Rules
- [rule 1 - e.g., "name must be non-empty, max 200 characters"]
- [rule 2 - e.g., "startDate must be before endDate"]

## Relationships
| Related Entity | Type | Delete Rule | Inverse | Description |
|---------------|------|-------------|---------|-------------|
| [Entity] | [to-one / to-many] | [cascade / nullify / deny] | [property] | [purpose] |

## Computed Properties
- `[name]`: [type] - [what it computes]

## Fetch Patterns
- **Default sort**: [property, direction]
- **Common predicates**: [list common filter conditions]
- **Prefetch**: [relationships to prefetch for performance]

## Surfaces
[Include this section when design/screens/*.md exist. Omit when running standalone.]

| Screen | Fields Used | Mode |
|--------|-------------|------|
| [screen name from design/screens/] | [properties displayed/edited] | [read / read-write] |

## Notes
- [Any special considerations - e.g., "large text stored as external binary data"]
```

Present each entity to the user for confirmation before saving. Ask: "Does [Entity] look right? Any properties missing or wrong?"

## Step 3: Map Relationships

After all entities are defined, create the relationship graph. Read the relevant relationship documentation from the reference files.

Save to `engineering/relationships.md`:

```markdown
# Entity Relationships: [App Name]

## Relationship Graph

[ASCII diagram showing all entities and their relationships]

Example:
┌──────────┐     1:N     ┌──────────┐
│   User   │────────────▶│  Project  │
└──────────┘             └──────────┘
                              │
                              │ 1:N
                              ▼
                         ┌──────────┐
                         │   Task   │
                         └──────────┘

## Relationship Table

| From | To | Type | Delete Rule | Inverse | Constraint |
|------|----|------|-------------|---------|------------|
| [Entity] | [Entity] | [1:1 / 1:N / N:N] | [cascade / nullify / deny] | [property] | [optional constraint] |

## Cascade Analysis

When [Entity] is deleted:
1. [What happens to related entities - chain through the graph]
2. [What gets orphaned vs. cascaded vs. nullified]

## Circular Reference Check
- [List any circular relationships and how they're handled]

## CloudKit Considerations
- [If syncing: which relationships sync, which are local-only]
- [Relationship limits for CloudKit (e.g., CKReference limitations)]
```

Walk through the graph and verify: no orphans possible, cascade chains do not destroy unexpected data, delete rules are consistent.

## Step 4: Plan Migrations

Define the migration strategy for schema evolution. Read the migration reference docs.

Save to `engineering/migrations.md`:

```markdown
# Migration Plan: [App Name]

## Strategy

**Approach**: [Lightweight / Staged (SwiftData) / Heavyweight (Core Data)]
**Apple says**: "[Quote from migration reference doc]"

## Version History

### V1 (Initial)
- [Entity list and their properties at v1]

## Migration Checklist

For each future schema change:
1. [ ] Add new schema version
2. [ ] Define migration mapping (if heavyweight)
3. [ ] Test with production-size data
4. [ ] Test upgrade from every previous version
5. [ ] Verify CloudKit schema compatibility (if syncing)

## Safe Changes (Lightweight)
These changes can be handled automatically:
- Adding a new optional property with default
- Adding a new entity
- Renaming with `originalName` parameter
- Making an optional property non-optional (with default)

## Unsafe Changes (Require Staged/Heavyweight)
These changes require explicit migration logic:
- Removing a property
- Changing a property's type
- Splitting an entity
- Merging entities
- Changing relationship cardinality
```

Update `.local.md` to set `current_phase: "complete"`.

## Completion

Present a summary:

> "Data model complete for [App Name]. Here's what we defined:"

- **Persistence**: [chosen strategy] - [1-sentence rationale]
- **Entities**: [count] entities in `engineering/entities/`, each self-contained
- **Relationships**: [describe graph shape - e.g., "tree structure rooted at User"]
- **Migrations**: [strategy] - ready for schema evolution
- **Sync**: [CloudKit / none / custom]

Files created:
- `engineering/requirements.md` - Data requirements and access patterns
- `engineering/persistence.md` - Strategy rationale
- `engineering/relationships.md` - Entity relationship graph
- `engineering/migrations.md` - Schema migration plan
- `engineering/entities/*.md` - One file per entity

## Tone

Be collaborative and precise. Be a data architect, not a lecturer. When Apple's docs have a specific recommendation, state it directly. When there are tradeoffs, present them clearly and help the user decide.
