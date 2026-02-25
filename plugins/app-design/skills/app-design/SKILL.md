---
name: app-design
description: Full App design workflow — check progress and continue from where you left off
---

# App Design — Full Workflow

This command checks your design progress and runs the right phase.

## Check Progress

1. Read `.codex/app-design.codex/app-design.local.md` if it exists
2. Check which `design/` files exist:
   - `design/goals.md`
   - `design/features.md`
   - `design/patterns.md`
   - `design/navigation.md`
   - `design/vocabulary.md`
   - `design/states.md`
   - `design/foundations.md`
   - `design/screens/` directory (check for any `.md` files inside)

Report progress to the user:

> "Here's where we are with [App Name]:"
> - [x/blank] Goals defined (`design/goals.md`)
> - [x/blank] Features prioritized (`design/features.md`)
> - [x/blank] Patterns matched (`design/patterns.md`)
> - [x/blank] Navigation designed (`design/navigation.md`)
> - [x/blank] Visual vocabulary defined (`design/vocabulary.md`)
> - [x/blank] State patterns defined (`design/states.md`)
> - [x/blank] Screens designed (`design/screens/` — list files found)
> - [x/blank] Foundations applied (`design/foundations.md`)

**Legacy detection**: If `design/screens.md` exists (monolithic) but `design/screens/` directory does not, note that the design uses the legacy format and will be migrated to split files on next architect or refactor run.

## Route to the Right Phase

### If goals or features are missing → Discovery

Run the discovery phase. Follow EVERY instruction below — this is the full discovery process.

#### Part 1: Define Goals

Ask these questions one at a time using a direct user question, skipping any already answered in `.codex/app-design.codex/app-design.local.md`:

1. **Who are the people?** — "Who are the people that will use this app? Describe them — their age, habits, what they care about."
2. **What are their pain points?** — "What frustrations or problems do these people face that this app could help with?"
3. **What are they trying to achieve?** — "What goals do your users have? What does success look like for them?"
4. **What needs does the app meet?** — "How specifically does this app help them? What needs does it fulfill that nothing else does well?"
5. **Target platforms** — "Which Apple platforms are you targeting?" (offer: iPhone, iPad, Mac, Apple Watch, Apple TV)

After each answer, acknowledge and reflect it back briefly.

Then define the **design character**:

> "If your app were a physical space, what would it look like? A bright open-plan office? A private consultation room? A busy café? Describe the feeling — materials, light, pace."

Refine into a one-sentence metaphor. Extract 4-6 qualities with design implications as a table.

Write `design/goals.md` and create/update `.codex/app-design.codex/app-design.local.md`.

#### Part 2: Prioritize Features

1. **Brainstorm** — Ask the user to list every possible feature. Actively suggest features based on goals and pain points.
2. **Filter** — Present all features, ask which are ESSENTIAL for v1. Challenge gently.
3. **Detail** — For each essential feature, ask how it should work. Identify key steps.
4. **Tag intents** — For each feature, tag the user intent that maps to an Apple HIG pattern.

Write `design/features.md`. Update `.codex/app-design.codex/app-design.local.md` to set `current_phase: "architect"`.

### If features exist but design files are incomplete → Architecture

Tell the user: "Running the architect phase. Use `$app-design-architect` for the full design process."

Then follow the architect command's full process (Steps 0-4).

### If all design files exist → Complete

> "Your design is complete! All files are in `design/`."

Suggest next steps:
- "Run `$app-design-refactor` to rework design decisions you're not happy with"
- "Each screen file in `design/screens/` is self-contained — load just the screen you're implementing"
- "Cross-screen concerns live in `design/navigation.md`, `design/vocabulary.md`, and `design/states.md`"
- "The `design/` folder is your source of truth — update it as you iterate"
