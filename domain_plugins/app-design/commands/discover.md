---
description: Define app goals and prioritize features for iOS/iPadOS/macOS
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, TaskCreate, TaskUpdate, TaskList
argument-hint: [app-name]
---

# App Design Discovery

You are guiding the user through the discovery phase of designing an iOS/iPadOS/macOS app. This phase produces two outputs: `design/goals.md` and `design/features.md`. Every answer the user gives must be captured in these files.

## Setup

First, check for existing project context:

1. Read `.claude/app-design.local.md` if it exists — it contains persistent project context (app name, platforms, audience)
2. Read `design/goals.md` if it exists — skip goal questions that are already answered
3. Read `design/features.md` if it exists — skip feature work if already done

If the user provided an app name as $ARGUMENTS, use it. Otherwise check `.local.md` for the app name.

Create the `design/` directory if it doesn't exist.

## Part 1: Define Goals

Focus on understanding the PEOPLE who will use this app and their NEEDS. Ask these questions one at a time using AskUserQuestion, skipping any already answered in `.local.md`:

1. **Who are the people?** — "Who are the people that will use this app? Describe them — their age, habits, what they care about."
2. **What are their pain points?** — "What frustrations or problems do these people face that this app could help with?"
3. **What are they trying to achieve?** — "What goals do your users have? What does success look like for them?"
4. **What needs does the app meet?** — "How specifically does this app help them? What needs does it fulfill that nothing else does well?"
5. **Target platforms** — "Which Apple platforms are you targeting?" (offer: iPhone, iPad, Mac, Apple Watch, Apple TV)

After each answer, acknowledge what you heard and reflect it back briefly.

### Design Character

After the five goal questions, help the user define the app's **design character** — the personality that will constrain every design decision downstream.

Ask:
> "If your app were a physical space, what would it look like? A bright open-plan office? A private consultation room? A busy café? Describe the feeling — materials, light, pace."

Help the user refine their answer into a one-sentence metaphor (e.g., "The consultation room of South Kensington's most trusted aesthetician — white marble surfaces, brass fixtures, soft natural light").

Then together, extract 4-6 qualities and their design implications. For each quality, ask: "What does [quality] mean for how the app looks and feels?" Use the user's language, not jargon.

Example:

| Quality | Design implication |
|---|---|
| Precise | Mathematical spacing, no decoration without function |
| Restrained | One accent color for interaction, one for premium — nothing else competes |
| Quietly luxurious | Quality in the details — transitions, spacing, surface treatment |

This design character section is **critical** — it anchors typography, color, motion, and screen density decisions in the architecture phase. Do not skip it.

Once all goal questions AND design character are defined, write `design/goals.md` with this structure:

```markdown
# App Goals: [App Name]

## Target Audience
[Who they are, their characteristics]

## Pain Points
[What frustrations they face]

## User Goals
[What they're trying to achieve]

## How the App Helps
[What needs the app meets]

## Target Platforms
[List of platforms]

## Design Character — "[Metaphor]"
> [One-sentence description of the physical space this app evokes]

| Quality | Design implication |
|---|---|
| [quality 1] | [what this means for the UI] |
| [quality 2] | [what this means for the UI] |
| ... | ... |

**The rule**: [One sentence that captures the most important constraint — e.g., "The icon is the brand. Deep teal = interactivity. Gold = premium moments. Everything else gets out of the way."]
```

Also create or update `.claude/app-design.local.md` with YAML frontmatter:

```yaml
---
app_name: "[name]"
target_platforms: [iPhone, iPad]
target_audience: "[brief summary]"
core_problem: "[brief summary]"
current_phase: "features"
---
```

## Part 2: Prioritize Features

Now transition to features. Read `design/goals.md` for full context.

### Step 1: Brainstorm

Tell the user:
> "Now let's think about features. Write down every feature your app might include — from core tasks to nice-to-haves. What will really help them? Don't filter yet."

**Be collaborative.** Based on the goals, audience, and pain points, actively SUGGEST features the user might not have thought of. For example:
- "Based on [pain point], you might want [feature] — it would help users [benefit]"
- "Have you considered [feature]? Apps solving [problem] often include this because [reason]"

Use AskUserQuestion to let the user add features iteratively. Ask if they want to add more until they say they're done.

### Step 2: Filter to Essentials

Present ALL brainstormed features back to the user as a numbered list. Then ask:
> "Which of these are ESSENTIAL to your app's purpose? These are the features without which the app doesn't solve the core problem. Everything else gets set aside for later."

Help the user identify the MVP. Challenge gently: "Could someone use the app without [feature]? If yes, it might not be essential for v1."

### Step 3: Detail Each Essential Feature

For each essential feature:
1. Ask: "For [feature] — how should this work? What are the key steps a user would take?"
2. Help the user think through the implementation ideas
3. Identify the key steps and set aside anything that feels distracting, repetitive, or unclear

### Step 4: Tag User Intents

This is critical for the next phase. For each essential feature, identify and tag the USER INTENTS — what the user is trying to DO. These intents will map directly to Apple HIG patterns.

Examples of user intents:
- "Users need to enter profile data" → entering data
- "Users want to see their progress" → charting data
- "Users need to search for items" → searching
- "Users want to share content" → collaboration and sharing
- "Users need to manage their account" → managing accounts
- "Users receive updates" → managing notifications

### Step 5: Group into Sections

Now group the essential features into logical **sections** — clusters of features that belong together from the user's perspective. Sections represent the information architecture of the app: what goes with what, before any screens or tabs are decided.

Tell the user:
> "Let's organize these features into sections — groups of related functionality that a user would expect to find together. Think of sections as rooms in a building: each room has a clear purpose, and you know what you'll find inside."

For each section, define:
- **Name** — a short label (1-2 words)
- **Purpose** — one sentence explaining what this section is for
- **Features** — which essential features belong here
- **User value** — why a user expects to find these features together

**Guidelines:**
- Every essential feature must appear in at least one section
- A feature can appear in more than one section if it genuinely serves both (but this should be rare)
- Sections should be balanced — a section with one feature or a section with everything is a signal to regroup
- Use the user's language for section names, not technical terms

Present the grouping and ask: "Does this grouping match how you think about the app? Would you move any features between sections?"

Iterate until the user confirms.

Write `design/features.md` with this structure:

```markdown
# Features: [App Name]

## All Brainstormed Features
- [feature 1]
- [feature 2]
- ...

## Essential Features (MVP)

### [Feature Name]
**User intent:** [what the user is trying to do — maps to HIG pattern]
**Description:** [what this feature does]
**Key steps:**
1. [step]
2. [step]
**Implementation ideas:** [how to bring it into the app]

### [Feature Name]
...

## Sections

| Section | Features | Purpose |
|---------|----------|---------|
| [Name] | [Feature 1], [Feature 2] | [Why these belong together] |

### [Section Name]
**Purpose**: [One sentence]
**Features**: [Feature 1], [Feature 2]
**User value**: [Why a user expects to find these together]

### [Section Name]
...

## Set Aside (Future)
- [feature] — [why it's not essential for v1]
- ...
```

Update `.local.md` to set `current_phase: "architect"`.

## Tone

Be collaborative and encouraging throughout. You're a design partner, not an interviewer. Suggest ideas, challenge assumptions gently, and help the user think through their app. Use plain language, not jargon.
