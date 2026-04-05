---
name: apple-hig
description: This skill should be used when designing UI for Apple platforms (iOS, iPadOS, macOS, tvOS, visionOS, watchOS). Covers choosing the right component (tab bar vs sidebar, sheet vs popover, list vs collection), applying HIG patterns (onboarding, search, settings, data entry, modality), and making visual design decisions (typography, color, layout, dark mode, motion). Activates on questions like "which navigation pattern should I use," "how should I design this screen for iPad," "what does Apple recommend for onboarding," or "check this design against HIG."
---

# Apple Human Interface Guidelines Reference

This skill contains Apple's official Human Interface Guidelines. Use it to make informed, platform-correct design decisions.

## How to Use This Skill

Follow the progressive discovery pipeline. Each step narrows the decision space for the next:

```text
Features (user intents) -> Patterns -> Components -> Foundations
```

### Step 1: Match Features to Patterns

Read `indexes/patterns-by-intent.md` to find which HIG patterns match the user's feature intents. Then read the full pattern reference:

```text
references/patterns/design-[pattern-name].md
```

Patterns tell you the approach - how Apple recommends handling things like entering data, searching, onboarding, managing notifications, and similar intents.

### Step 2: Select Components by Platform

Read `indexes/components-by-platform.md` for the full component catalog with platform support flags. Filter by the user's target platforms. Then read the full component reference:

```text
references/components/design-[component-name].md
```

Each component doc contains:
- Best practices - bold-prefixed do/don't rules from Apple
- Platform considerations - what differs on iOS vs iPadOS vs macOS
- When to use / when not to use - concrete component selection guidance
- Related - links to adjacent components and developer APIs

### Step 3: Apply Foundations

Read `indexes/foundations-checklist.md` for the ordered list of 7 foundation decisions. Then read each foundation reference:

```text
references/foundations/design-[foundation-name].md
```

Work through: Typography -> Writing -> Branding -> Color (+ Dark Mode) -> Materials -> Layout -> Motion.

## Key Rules

- Always read the reference doc before recommending a component or pattern. Do not rely on general knowledge.
- Always check platform support. Never recommend a component that is unsupported on the user's target platforms.
- Be specific. Do not say "use appropriate typography" - cite guidance and name specific text styles.
- Quote Apple's rules. When a component has a critical do/don't, cite it directly.

## Reference Structure

```text
references/
├── patterns/          # 25 files - design approach for user intents
├── components/        # 63 files - UI component guidance with platform rules
└── foundations/       # 8 files - visual design decisions
```
