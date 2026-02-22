---
description: Create user story maps via Jeff Patton methodology
argument-hint: [feature name] or --resume [session-name] or --list
allowed-tools: Read, Write, Bash, Grep, Glob, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, Task
---

# User Story Mapping Interview

Create comprehensive user story maps by interviewing the user about their feature requirements using Jeff Patton's User Story Mapping methodology.

## Input

$ARGUMENTS

**Commands:**
- `feature name` - Start new interview session for a feature
- `--resume <session>` - Resume existing interview session
- `--list` - List all active/completed sessions

## Session Management

### Check for Existing Sessions

```bash
ls -la docs/user-stories/*.session.md 2>/dev/null | head -20 || echo "No sessions found"
```

**If `--list`:** Show sessions and exit.

**If `--resume <session>`:** Load session state from `docs/user-stories/<session>.session.md` and continue.

**If no session name provided:** Use AskUserQuestion to ask what feature to map.

### Session File Format

Progress saves to `docs/user-stories/<feature-name>.session.md`:

```markdown
---
feature: <name>
personas: [<persona1>, <persona2>]
current_persona: <persona>
current_phase: <opening|activities|tasks|stories|skeleton|review>
started: <ISO timestamp>
updated: <ISO timestamp>
---

# Interview Progress

## Answers
<captured answers as markdown>

## Story Map Draft
<evolving map structure>

## Pending Questions
<questions to circle back to>
```

## Interview Process

### Phase 1: Opening (Structured Template)

Use AskUserQuestion in sequence to establish context:

**Question 1: Problem**
```claude
AskUserQuestion:
  header: "Problem"
  question: "What problem does this feature solve? Describe the user's pain point."
  multiSelect: false
  options:
    - label: "Efficiency problem"
      description: "Users waste time doing X manually/slowly"
    - label: "Capability gap"
      description: "Users cannot do X at all today"
    - label: "Quality issue"
      description: "Users can do X but results are poor/unreliable"
    - label: "Experience friction"
      description: "Users can do X but find it frustrating/confusing"
```

**Question 2: User**
```claude
AskUserQuestion:
  header: "User"
  question: "Who is the primary user of this feature?"
  multiSelect: false
  options:
    - label: "End user/customer"
      description: "External users of the product"
    - label: "Internal team member"
      description: "Developers, ops, support staff"
    - label: "Administrator"
      description: "People who configure/manage the system"
    - label: "Let me describe them"
      description: "Custom persona definition"
```

**Question 3: Solution**
```claude
AskUserQuestion:
  header: "Solution"
  question: "In one sentence, what does this feature do?"
  multiSelect: false
  options:
    - label: "Automates a process"
      description: "Removes manual steps from a workflow"
    - label: "Adds new capability"
      description: "Enables something previously impossible"
    - label: "Improves existing feature"
      description: "Makes current functionality better"
    - label: "Integrates systems"
      description: "Connects previously separate tools/data"
```

**Question 4: Success Metric**
```claude
AskUserQuestion:
  header: "Success"
  question: "How will you know this feature succeeded? What metric matters to your team?"
  multiSelect: false
  options:
    - label: "User engagement"
      description: "Adoption rate, daily active users, feature usage"
    - label: "Efficiency gains"
      description: "Time saved, tasks completed, throughput increased"
    - label: "Quality improvement"
      description: "Error rates down, satisfaction up, support tickets reduced"
    - label: "Custom KPI"
      description: "Tell me what your team actually measures"
```

### Phase 2: Persona Deep-Dive

If multiple personas mentioned, interview each separately:

```claude
AskUserQuestion:
  header: "Persona"
  question: "Let's focus on [persona]. What's their typical day like before they use this feature?"
  multiSelect: false
  options:
    - label: "Frustrated with current process"
      description: "Walk me through what frustrates them"
    - label: "Working around limitations"
      description: "Tell me about their workarounds"
    - label: "Missing information/tools"
      description: "What do they lack that this provides?"
```

**Explore all emotional dimensions:**
- Frustration points: "What makes them angry about the current state?"
- Delight opportunities: "What would make them say 'finally!'?"
- Confidence/trust: "Where do they feel uncertain or out of control?"

### Phase 3: Activity Discovery (Backbone)

Identify the main activities (columns in the story map):

```claude
AskUserQuestion:
  header: "Activities"
  question: "What are the main things [persona] needs to accomplish? List 3-5 major activities."
  multiSelect: true
  options:
    - label: "Setup/Configuration"
      description: "Initial preparation before main workflow"
    - label: "Core Action"
      description: "The main thing they're trying to do"
    - label: "Review/Validation"
      description: "Checking that results are correct"
    - label: "Integration/Handoff"
      description: "Passing work to next step/person"
```

For each activity identified, ask:
1. What triggers this activity?
2. What does success look like for THIS activity? (Activity-level success criteria)
3. What could go wrong? (Error states & recovery)
4. What makes this different/better than alternatives? (Unique value)

### Phase 4: Task Discovery (Rows under Activities)

For each activity, discover user tasks:

```claude
AskUserQuestion:
  header: "Tasks"
  question: "Within '[Activity]', what specific tasks does the user perform? Order them by when they happen."
  multiSelect: true
  options:
    - label: "T1: [First task]"
      description: "Start of activity"
    - label: "T2: [Second task]"
      description: "Following T1"
    - label: "T3: [Third task]"
      description: "Following T2"
    - label: "More tasks needed"
      description: "There are additional steps to discuss"
```

### Phase 5: Story Discovery (Cards under Tasks)

For each task, elicit user stories:

**Template questions (rotate through):**

1. **Business Impact:** "How does this connect to your Q2 goals? Your team's capacity?"
2. **Error Handling:** "What happens when this fails? How does the user recover?"
3. **Acceptance Criteria:** Offer concrete examples: "Success might look like '<2s load time' - does that fit?"
4. **Dependencies:** "What must exist before this can work?" (Capture explicit links)
5. **Effort:** "Is this simple (hours), standard (days), or complex (week+)?"

**Priority assignment:**
```claude
AskUserQuestion:
  header: "Priority"
  question: "Is 'US-X.Y.Z: [story]' MVP, Nice-to-have, or Future?"
  multiSelect: false
  options:
    - label: "MVP"
      description: "Must have for first release"
    - label: "Nice-to-have"
      description: "Include if time permits"
    - label: "Future"
      description: "Defer to later phase"
```

### Phase 6: Non-Obvious Deep Questions

**Ask these throughout, not just at the end:**

**Broader Context Questions:**
- "How does this fit with your team's roadmap for this quarter?"
- "What happens to the rest of the workflow when this ships?"
- "Who else in the organization cares about this feature succeeding?"
- "What's the opportunity cost of building this vs. something else?"

**Hidden Assumption Questions:**
- "You said users want X - have you validated that with user research?"
- "You're assuming Y is available - what if it's not?"
- "This depends on Z working correctly - what's the fallback?"

**Second-Order Effect Questions:**
- "If this succeeds wildly, what new problems does it create?"
- "How does this change support load? Training needs? Documentation?"
- "What happens in 6 months when usage grows 10x?"

**Constraint Discovery:**
- "What can't change here? What's technically off-limits?"
- "What's politically sensitive about this feature?"
- "Are there compliance, security, or performance constraints I should know about?"

**Missing Piece Detection:**
- "I notice you didn't mention error handling - intentional?"
- "Most features like this need X - should we include it?"
- "What about [common capability in this domain]?"

**Jargon Clarification:**
- When user uses unfamiliar terms, IMMEDIATELY ask: "Can you define '[term]'? I want to make sure I understand exactly what you mean."

### Phase 7: Conflict Resolution (Socratic Method)

When scope creep or conflicting requirements emerge:

**Do NOT say "These conflict."**

**Instead, ask Socratic questions:**
- "If you had to choose between [A] and [B] for the first release, which would you pick?"
- "What would happen if we shipped with only [A]?"
- "Which of these gets you closer to [success metric you mentioned]?"
- "Is there a way to get 80% of the value with 20% of the scope?"

**For low-ROI stories:**
- "This seems like a lot of effort for [benefit]. What am I missing?"
- "How often does this scenario actually happen?"
- "What's the cost of NOT having this in v1?"

### Phase 8: Walking Skeleton Identification

After story collection, propose the critical path:

```claude
AskUserQuestion:
  header: "Skeleton"
  question: "I think the Walking Skeleton (minimum viable path) is: [Activity A → Task A1 → US-1.1.1] → [Activity B → Task B2 → US-2.1.1]. Does this capture the core value?"
  multiSelect: false
  options:
    - label: "Yes, that's the critical path"
      description: "Proceed with this as MVP scope"
    - label: "Close, but adjust"
      description: "Let me modify the critical path"
    - label: "Wrong, let me explain"
      description: "The real MVP is different"
```

### Phase 9: Review & Output

After completing all phases for all personas:

**Show the evolving map after each activity.** Format:

```
┌─────────────────────────────────────────────────────────────────┐
│                        BACKBONE (Activities)                     │
├──────────────────┬──────────────────┬──────────────────────────┤
│    [ACTIVITY 1]  │    [ACTIVITY 2]  │    [ACTIVITY 3]          │
│                  │                  │                          │
│    Description   │    Description   │    Description           │
└──────────────────┴──────────────────┴──────────────────────────┘
```

**Then ask about pending questions (things user said "I need to think about"):**
- "Earlier you deferred [question]. Ready to answer now?"

**Migration section (only if replacing something):**
```claude
AskUserQuestion:
  header: "Migration"
  question: "Does this feature replace existing functionality?"
  multiSelect: false
  options:
    - label: "Yes, full replacement"
      description: "I'll add a migration guide section"
    - label: "Partial replacement"
      description: "Tell me what's changing"
    - label: "No, it's new"
      description: "Skip migration section"
```

**Final format choice:**
```claude
AskUserQuestion:
  header: "Format"
  question: "Which output format do you want?"
  multiSelect: false
  options:
    - label: "Full story map (Recommended)"
      description: "Tables, backbone visualization, all sections"
    - label: "Simplified cards"
      description: "Just stories with acceptance criteria"
    - label: "Both"
      description: "Full map + exportable story cards"
```

## Output Structure

Write to `docs/user-stories/<feature-name>.md`:

```markdown
# User Story Map: <Feature Name>

**Date:** <today>
**Personas:** <list>
**Methodology:** Jeff Patton's User Story Mapping

---

## Story Map Overview

┌───────────────────────────────────────────────────────────┐
│                    BACKBONE (Activities)                   │
├────────────────┬────────────────┬────────────────────────┤
│   ACTIVITY 1   │   ACTIVITY 2   │   ACTIVITY 3           │
│                │                │                        │
│   Description  │   Description  │   Description          │
└────────────────┴────────────────┴────────────────────────┘

---

## 1. [ACTIVITY 1]

### User Tasks

| Task | Description |
|------|-------------|
| **T1.1** Name | What it does |

### User Stories

#### T1.1 [Task Name]

| ID | Story | Priority | Effort | Dependencies |
|----|-------|----------|--------|--------------|
| **US-1.1.1** | As a [persona], I want [action] so that [benefit] | MVP | Standard | None |

**Success Criteria (Activity Level):** <what success looks like>

---

## Walking Skeleton

The minimum viable path through the system:

```
ACTIVITY 1     →  ACTIVITY 2      →  ACTIVITY 3
[Task/Story]       [Task/Story]       [Task/Story]
```

---

## Persona Reference

| Persona | Primary Activities | Key Stories |
|---------|-------------------|-------------|
| [Name]  | A1, A2           | US-1.1.1, US-2.1.1 |

---

## Breaking Changes (if any)

Simple list of what this affects:
- [Affected area 1]
- [Affected area 2]

---

## Migration Guide (if replacing)

### Before
<how it works today>

### After
<how it will work>

---

## Plan Integration

This story map can be used with `/dev-workflow:write-plan` to create an implementation plan.

Story → Task mapping will be added when plan is created.
```

## Interview Pacing

- **2-3 questions per round** before offering to move forward
- Show evolving map after each activity is complete
- If user says "I need to think about this" → Move to next topic, add to Pending Questions
- Save progress after every significant answer

## Handoff

After writing the story map:

```claude
AskUserQuestion:
  header: "Next"
  question: "Story map saved. What next?"
  multiSelect: false
  options:
    - label: "Create implementation plan (Recommended)"
      description: "Use /dev-workflow:write-plan to create plan from MVP stories"
    - label: "Add another persona"
      description: "Interview a different user type"
    - label: "Refine stories"
      description: "Dive deeper into specific stories"
    - label: "Done"
      description: "Story map is complete"
```

**If "Create implementation plan":**
```text
/dev-workflow:write-plan @docs/user-stories/<feature-name>.md
```

This creates an implementation plan with story traceability:
- Task 1 → US-1.1.1
- Task 2 → US-1.1.2

## Error Recovery

**If session file corrupted:**
```bash
# Check git history
git log --oneline docs/user-stories/<session>.session.md
# Restore from commit
git checkout <commit>^ -- docs/user-stories/<session>.session.md
```

**If user wants to start over:**
```bash
rm docs/user-stories/<session>.session.md
# Then run /dev-workflow:user-story <feature> again
```
