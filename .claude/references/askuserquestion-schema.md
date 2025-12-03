# AskUserQuestion Tool Schema

Official schema reference for the Claude Code `AskUserQuestion` tool.

## Purpose

Use this tool when you need to ask the user questions during execution:
- Gather user preferences or requirements
- Clarify ambiguous instructions
- Get decisions on implementation choices
- Offer choices about what direction to take

## Schema

```typescript
interface AskUserQuestion {
  questions: Question[];             // 1-4 questions (required)
  answers?: Record<string, string>;  // Collected user answers (returned)
}

interface Question {
  question: string;       // Complete question text (required)
  header: string;         // Short label, max 12 chars (required)
  multiSelect: boolean;   // Allow multiple selections (required)
  options: Option[];      // 2-4 available choices (required)
}

interface Option {
  label: string;          // Display text, 1-5 words (required)
  description: string;    // Explanation of choice (required)
}
```

## Constraints

| Field | Constraint |
|-------|------------|
| `questions` | 1-4 items |
| `options` | 2-4 items per question |
| `header` | Max 12 characters |
| `label` | 1-5 words, concise |
| `multiSelect` | Boolean, required |

**Note:** Users always see an "Other" option for custom text input.

## Skill Instruction Format

When instructing Claude to use AskUserQuestion in a skill, use this format:

```markdown
**Use the AskUserQuestion tool** (do NOT output as plain text):

Question: "What is your preference?"
Header: "Decision"
Options:
- Option A: Description of option A
- Option B: Description of option B
multiSelect: false
```

**Key principles:**
- Make instruction imperative and explicit
- Include "(do NOT output as plain text)" to prevent text-only output
- Use bullet format for options: `- Label: Description`
- Always include `multiSelect` field

## When to Use vs. Conversational Questions

**Use AskUserQuestion for:**
- Scope and constraint gathering
- Approach selection (after presenting options)
- Design section validation
- Documentation and implementation handoff
- Any decision with 2-4 clear choices

**Use conversational questions for:**
- Context-specific clarifications
- Deep-dive questions unique to a problem
- Exploring edge cases and nuances
- Open-ended exploration

**Principle:** Structured questions for decisions, conversational for discovery.

## Example

```markdown
**Use the AskUserQuestion tool** (do NOT output as plain text):

Question: "Plan saved. How would you like to execute it?"
Header: "Execute"
Options:
- Subagent-Driven: Execute in this session with fresh subagent per task
- Parallel Session: Open new session in worktree, batch execution
- Skip: I'll execute manually later
multiSelect: false
```

## Sources

- [Internal Claude Code tools implementation](https://gist.github.com/bgauryy/0cdb9aa337d01ae5bd0c803943aa36bd)
- [Missing documentation issue #10346](https://github.com/anthropics/claude-code/issues/10346)
- [Bug report #9846](https://github.com/anthropics/claude-code/issues/9846)

---
*Last updated: 2025-12-03*
