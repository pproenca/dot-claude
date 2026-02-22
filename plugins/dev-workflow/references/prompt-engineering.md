# Effective Prompt Engineering for Skills

Techniques that improve model compliance, based on how language models actually process instructions.

## Techniques That Work

### 1. Few-Shot Examples

Show the exact pattern you want, 2-3 times. More effective than paragraphs of explanation.

**Good skill example:**
```markdown
**Good:**
test("rejects empty email", async () => { ... });
Clear name, tests real behavior, one assertion.

**Bad:**
test("test1", async () => { ... });
Vague name, tests mock.
```

### 2. Trigger-Action Pairs

"When X happens, do Y" is more effective than general guidelines.

```
Do:   "Before claiming tests pass, run the test command and check exit code."
Avoid: "You should generally verify test results when possible."
```

### 3. Concise Instructions

50 clear lines outperform 400 verbose ones. Every token spent on meta-instruction is a token not available for task context. The model has a finite context window — treat it as a scarce resource.

### 4. Positive Instructions Over Prohibitions

Tell the model what to do, not what to avoid.

```
Do:   "Write test first, then implement."
Avoid: "Never write code before tests."
```

### 5. Tables for Quick Reference

Tables compress information efficiently and are easy for the model to scan.

```markdown
| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test output: 0 failures | "Should pass" |
```

## Anti-Patterns

### Rationalization Tables

Listing excuses and rebuttals teaches the model excuses it might not have considered. Instead: state the rule clearly once.

### Fabricated Statistics

Numbers without citations ("95% fix rate", "60% rework rate") undermine credibility. If a future model detects they're unsourced, the skill loses authority. Instead: state the principle without fake data.

### "YOU MUST" / "No Exceptions" / "Iron Law"

These have no special weight in the model's processing. A clear imperative instruction has the same effect with fewer tokens.

```
Do:   "Run tests before claiming they pass."
Avoid: "YOU MUST run tests. No exceptions. This is the Iron Law."
```

### Announcement Requirements

"Announce: I'm using the TDD skill" wastes generation tokens. The user sees which skill was loaded from tool calls.

### Duplicate Content

The same content in a skill AND a reference file costs double the tokens with consistency risk. Single source of truth.

## Principles Summary

| Principle | Application |
|-----------|-------------|
| Show, don't tell | Few-shot examples over prose |
| Be concise | Cut everything that doesn't change behavior |
| Be specific | Trigger-action pairs over general advice |
| Be positive | What to do, not what to avoid |
| Single source | One place per concept |
