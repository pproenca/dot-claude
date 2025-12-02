# Measuring Improvements

How to prove changes are better, inspired by "How to Measure Anything" by Douglas Hubbard.

## Table of Contents

- [Core Principle](#core-principle)
- [The Measurement Framework](#the-measurement-framework)
- [Quantitative Metrics](#quantitative-metrics)
- [Qualitative Proxies](#qualitative-proxies)
- [User Testing Scenarios](#user-testing-scenarios)
- [Improvement Validation Template](#improvement-validation-template)
- [Common Measurement Mistakes](#common-measurement-mistakes)
- [Quick Reference](#quick-reference)

## Core Principle

**If it matters, it's measurable. If it's measurable, we can measure it.**

Even "intangible" qualities like elegance or developer experience can be measured through:
- Decomposition into observable components
- Proxy metrics that correlate with value
- Before/after comparisons
- User feedback on specific aspects

## The Measurement Framework

### Step 1: Define What "Better" Means

Before measuring, clarify:
- What specific improvement are we claiming?
- How would we know if we achieved it?
- What would change in the real world?

**Example:**
- Claim: "This skill is easier to trigger"
- Observable: Users find the skill more often
- Test: Try 5 different phrasings, count hits

### Step 2: Identify Proxy Metrics

Not everything can be measured directly. Use proxies:

| Value | Direct Measure | Proxy Metric |
|-------|----------------|--------------|
| Elegance | - | Line count, component count, explanation length |
| Usability | - | Time to first success, error rate |
| Maintainability | - | Cyclomatic complexity, coupling score |
| Discoverability | - | Trigger hit rate across phrasings |

### Step 3: Establish Baseline

Before changing anything:
1. Measure current state
2. Document the metrics
3. Save for comparison

```markdown
## Baseline: plugin-x
- Skills: 3
- Total lines: 847
- Average SKILL.md: 282 lines
- Trigger phrases: 8 total
- Components: 7
```

### Step 4: Measure After Change

Apply the same metrics:
```markdown
## After: plugin-x
- Skills: 2
- Total lines: 512
- Average SKILL.md: 256 lines
- Trigger phrases: 12 total
- Components: 5

## Delta
- Skills: -1 (33% reduction)
- Lines: -335 (40% reduction)
- Trigger phrases: +4 (50% increase)
- Components: -2 (29% reduction)
```

### Step 5: Validate with Users

Metrics tell part of the story. User validation confirms:
- Does it feel better?
- Is anything missing?
- Would you use this over the old version?

## Quantitative Metrics

Use `scripts/analyze-metrics.sh` for automated metric collection:

```bash
./scripts/analyze-metrics.sh plugins/
```

This script provides:
- Plugin and component counts
- SKILL.md line counts
- Files over 500 lines (red flags)
- Trigger phrase metrics

### Manual Metrics (when needed)

**Component count:**
```bash
find plugins -path "*/skills/*/SKILL.md" | wc -l
find plugins -path "*/agents/*.md" | wc -l
```

**Example coverage:**
```bash
grep -c "<example>" plugins/*/agents/*.md
```

## Qualitative Proxies

### Fresh Eyes Test

Ask someone unfamiliar:
- "What does this skill do?" (Should answer correctly in <30 seconds)
- "When would you use this?" (Should match intended triggers)
- "How would you invoke this?" (Should guess correctly)

**Scoring:**
- 3/3 correct: Excellent
- 2/3 correct: Good
- 1/3 correct: Needs work
- 0/3 correct: Major revision needed

### Self-Explanation Test

Can you explain the component in:
- One sentence? (If not, too complex)
- Without jargon? (If not, unclear naming)
- To a new developer? (If not, missing context)

### Deletion Test

Try removing the component:
- Does anything break?
- Is something missing?
- Did anyone notice?

If nothing changes, the component may not be needed.

## User Testing Scenarios

### Trigger Testing

Generate test prompts to verify skill/agent triggers:

```markdown
## Test: hook-development skill
Prompts to try:
1. "I want to create a hook that validates commits"
2. "How do I add a PreToolUse hook?"
3. "Can you help me implement hooks?"
4. "I need to validate tool usage"
5. "Tell me about PostToolUse events"

Expected: All 5 trigger hook-development skill
Actual: [Record results]
```

### Workflow Testing

Test complete workflows:

```markdown
## Test: Create a simple hook
1. User asks to create a commit validation hook
2. Skill should trigger
3. User should be guided through process
4. Result should be valid hooks.json

Expected duration: <5 minutes
Actual duration: [Record]
```

### Edge Case Testing

Test boundaries:

```markdown
## Test: Ambiguous trigger
Prompt: "I need help with my plugin"
Expected: Ask for clarification OR suggest relevant skills
Actual: [Record response]
```

## Improvement Validation Template

Use this template for every change:

```markdown
## Change: [Description]

### Baseline
- Metric A: [value]
- Metric B: [value]
- User feedback: [summary]

### After Change
- Metric A: [new value] ([delta])
- Metric B: [new value] ([delta])
- User feedback: [summary]

### Validation
- [ ] Quantitative improvement shown
- [ ] No regression in other metrics
- [ ] User confirms improvement
- [ ] Test scenarios pass

### Conclusion
[Is it better? Evidence summary]
```

## Common Measurement Mistakes

### Vanity Metrics

Metrics that look good but don't matter:
- Total lines of documentation (more ≠ better)
- Number of features (more ≠ better)
- Component count (more ≠ better)

**Fix**: Focus on value delivered, not volume

### Measuring the Wrong Thing

Optimizing what's easy to measure:
- Line count (but ignoring readability)
- File count (but ignoring coherence)
- Trigger count (but ignoring quality)

**Fix**: Measure what matters, even if harder

### No Baseline

Claiming improvement without comparison:
- "This is cleaner" (than what?)
- "This is faster" (by how much?)
- "This is better" (prove it)

**Fix**: Always measure before and after

### Confirmation Bias

Only looking for evidence of improvement:
- Ignoring metrics that got worse
- Testing only happy paths
- Asking leading questions

**Fix**: Actively seek disconfirming evidence

## Quick Reference

### Must Measure
- Before/after comparison on key metrics
- User feedback on specific changes
- Test scenarios covering main use cases

### Should Measure
- Line count / component count
- Trigger phrase quality
- Example coverage

### Nice to Measure
- Time to first success
- Error rate
- User preference in A/B scenarios

### Always Ask Users
- "Is anything missing from the old version?"
- "Does this feel simpler or more complex?"
- "Would you use this over what we had before?"
