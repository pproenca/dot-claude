# App Development — Full Workflow

This command checks your engineering progress and runs the right phase.

## Check Progress

1. Read `.codex/app-development.local.md` if it exists
2. Check which `design/` files exist (produced by app-design):
   - `design/goals.md`
   - `design/features.md`
   - `design/screens/` directory (check for any `.md` files inside)
3. Check which `engineering/` files exist:
   - `engineering/requirements.md`
   - `engineering/persistence.md`
   - `engineering/relationships.md`
   - `engineering/migrations.md`
   - `engineering/entities/` directory (check for any `.md` files inside)
   - `engineering/performance.md`
   - `engineering/monitoring.md`
   - `engineering/debug-log.md`

If `.codex/app-development.local.md` does not exist and `.claude/app-development.local.md` exists, read and migrate it to `.codex/app-development.local.md`.

Report progress to the user:

> "Here's where you are in the design → engineering loop:"
>
> **Design Phase** (from app-design):
> - [x/blank] Goals defined (`design/goals.md`)
> - [x/blank] Features prioritized (`design/features.md`)
> - [x/blank] Screens designed (`design/screens/`)
>
> **Engineering Phase**:
> - [x/blank] Data requirements defined (`engineering/requirements.md`)
> - [x/blank] Persistence strategy chosen (`engineering/persistence.md`)
> - [x/blank] Entities defined (`engineering/entities/` - list files found)
> - [x/blank] Relationships mapped (`engineering/relationships.md`)
> - [x/blank] Migrations planned (`engineering/migrations.md`)
> - [x/blank] Performance audited (`engineering/performance.md`)
> - [x/blank] Monitoring set up (`engineering/monitoring.md`)
> - [x/blank] Debug log started (`engineering/debug-log.md`)

If no `design/` artifacts exist, add: "No design artifacts found. You can run the app-design workflow first for a richer starting point, or proceed directly with engineering."

## Route to the Right Phase

### If requirements or persistence are missing → Data Modeling

Run the data modeling phase. Follow EVERY instruction below — this is the full modeling process.

#### Step 0: Understand Data Requirements

Ask these questions one at a time using ask the user directly, skipping any already answered:

1. **What data does the app manage?** - "What are the main things your app needs to store?"
2. **How does the data change?** - "How often does this data change? Read-heavy, write-heavy, or mixed?"
3. **What are the relationships?** - "How do these things relate to each other?"
4. **Where does data come from?** - "Created locally, synced from a server, imported, or a combination?"
5. **Who needs the data?** - "Does data need to sync across devices? Shared between users? Device-local only?"
6. **How much data?** - "Roughly how many records? Tens, hundreds, thousands, millions?"
7. **What queries matter?** - "What are the most common lookups? Sorting? Filtering? Full-text search?"

Write `engineering/requirements.md` and create/update `.codex/app-development.local.md`.

#### Step 1: Choose Persistence Strategy

Read `indexes/data-by-need.md` and relevant reference docs. Evaluate SwiftData, Core Data, and alternatives. Present with Apple quotes. Save to `engineering/persistence.md`.

#### Step 2: Define Entities

For each data type, create `engineering/entities/<entity-name>.md` with properties, validation, relationships, computed properties, and fetch patterns.

#### Step 3: Map Relationships

Create `engineering/relationships.md` with ASCII graph, relationship table, cascade analysis.

#### Step 4: Plan Migrations

Create `engineering/migrations.md` with V1 schema and migration checklist.

### If data model exists but performance is missing → Performance

Tell the user: "Data model is complete. Running the performance phase. Use `optimize workflow` for the full process."

Then follow the optimize command's full process (Steps 0-3).

### If everything exists → Complete

> "Your engineering foundation is complete! All files are in `engineering/`."

Suggest next steps:
- "Run `optimize workflow` to re-audit performance"
- "Run `debug workflow` when you hit an issue"
- "Run `refactor workflow` to rework the data model"
- "Each entity file in `engineering/entities/` is self-contained - load just the entity you're implementing"
- "Cross-entity concerns live in `engineering/relationships.md` and `engineering/persistence.md`"
