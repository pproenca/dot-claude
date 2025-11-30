---
name: brainstorming
description: Use when creating or developing, before writing code or implementation plans - refines rough ideas into fully-formed designs through collaborative questioning, alternative exploration, and incremental validation. Don't use during clear 'mechanical' processes
allowed-tools: Read, AskUserQuestion, Skill
---

# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design in small sections (200-300 words), checking after each section whether it looks right so far.

**Announce at start:** "I'm using the brainstorming skill to refine this idea into a design."

## Progress Tracking

Create TodoWrite todos for each phase:
- Understanding: Clarify the problem space
- Exploring: Investigate alternative approaches
- Presenting: Document proposed design
- Handoff: Transition to implementation

Mark each phase as `in_progress` when starting, `completed` when done. This makes progress visible and prevents skipping phases.

## Using AskUserQuestion

Use the AskUserQuestion tool for structured decision points:
- Scope and constraint gathering
- Approach selection (after presenting options)
- Design section validation
- Documentation and implementation handoff

Keep free-form conversation for:
- Context-specific clarifications
- Deep-dive questions unique to this idea
- Exploring edge cases and nuances

**Principle:** Structured questions for decisions, conversational for discovery.

## The Process

### Phase 1: Understanding the Idea

**Step 1: Check project context**
- Read relevant files, docs, recent commits
- Understand what exists before proposing what to build

**Step 2: Gather initial constraints**

Use AskUserQuestion to understand scope:

```
Question: "What is the scope of this feature?"
Header: "Scope"
Options:
- MVP / Proof of concept: Minimal viable implementation to validate the idea
- Production-ready: Full implementation with error handling, tests, and docs
- Enhancement: Adding to existing feature rather than building new
```

**Step 3: Identify target users (if unclear)**

Use AskUserQuestion when user type matters:

```
Question: "Who is the primary user of this feature?"
Header: "User"
Options:
- End users: External users of the application
- Developers: Engineers working with the codebase
- Both: Needs to serve multiple user types
```

**Step 4: Gather constraints**

Use AskUserQuestion with multiSelect for constraints:

```
Question: "What constraints should I consider?"
Header: "Constraints"
multiSelect: true
Options:
- Performance-critical: Speed and efficiency are primary concerns
- Backwards compatible: Must not break existing functionality
- Security-sensitive: Requires security review and hardening
- External dependencies: Integrates with third-party services
```

**Step 5: Context-specific questions**

Continue with free-form questions one at a time:
- Purpose: What problem does this solve?
- Success criteria: How will we know it works?
- Any unique constraints or requirements

### Phase 2: Exploring Approaches

**Step 1: Identify 2-3 approaches**

After understanding the idea, propose 2-3 different approaches:
- Describe each briefly with trade-offs
- Lead with your recommendation and explain why
- Keep descriptions concise (2-3 sentences each)

**Step 2: Get approach selection**

Use AskUserQuestion to select approach:

```
Question: "Which approach would you prefer?"
Header: "Approach"
Options:
- [Approach A name] (recommended): [Brief description of why this is recommended]
- [Approach B name]: [Brief description and trade-off]
- [Approach C name]: [Brief description and trade-off]
```

Generate option labels and descriptions dynamically based on the approaches identified.

### Phase 3: Presenting the Design

**Step 1: Present design in sections**

Once approach is selected, present the design:
- Break into sections of 200-300 words
- Cover: architecture, components, data flow, error handling, testing
- One section at a time

**Step 2: Validate each section**

After each section, use AskUserQuestion:

```
Question: "Does this section of the design look right?"
Header: "Feedback"
Options:
- Looks good: This section is accurate, proceed to next
- Minor tweaks: Small changes needed, I will specify
- Needs rethinking: This approach has issues, let's discuss
```

If "Minor tweaks" or "Needs rethinking" selected, pause for their input.

**Step 3: Handle feedback**

- **Looks good:** Proceed to next section
- **Minor tweaks:** Wait for their specification, apply changes, re-validate section
- **Needs rethinking:** Discuss issues, potentially return to Phase 2

### Phase 4: After the Design

**Step 1: Documentation decision**

Use AskUserQuestion for documentation:

```
Question: "How should I proceed with documentation?"
Header: "Docs"
Options:
- Save and commit: Write design doc and commit to git
- Save only: Write design doc without committing
- Skip docs: Proceed without saving design document
```

**Step 2: Save design (if chosen)**

- Write to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Use elements-of-style:writing-clearly-and-concisely skill if available
- Commit if "Save and commit" was selected

**Step 3: Implementation handoff**

Use AskUserQuestion for next steps:

```
Question: "Ready to proceed with implementation?"
Header: "Next step"
Options:
- Set up worktree: Create isolated workspace and write implementation plan
- Just the plan: Write implementation plan in current workspace
- Stop here: I will handle implementation separately
```

**Step 4: Execute choice**

- **Set up worktree:** Use super:using-git-worktrees, then super:writing-plans
- **Just the plan:** Use super:writing-plans directly
- **Stop here:** Report completion, offer to continue later

## Key Principles

- **Structured for decisions, conversational for discovery** - AskUserQuestion for clear choices, free-form for exploration
- **One question at a time** - Don't overwhelm with multiple questions
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense

## When to Skip AskUserQuestion

Use free-form text instead when:
- The question is highly context-specific
- Options would be artificial or unclear
- You need open-ended exploration
- The user has already indicated a preference conversationally

The "Other" option in AskUserQuestion always allows custom input, but some questions are better asked conversationally.

## Integration

**REQUIRED SUB-SKILLS (when continuing to implementation):**
- **super:using-git-worktrees** - If "Set up worktree" selected
- **super:writing-plans** - For creating implementation plan

**Pairs with:**
- **elements-of-style:writing-clearly-and-concisely** - For design documentation
