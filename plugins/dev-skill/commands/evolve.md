---
description: Investigate and improve an existing skill using discipline-aware quality assessment
argument-hint: <skill-path>
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, WebFetch, WebSearch
---

# Discipline-Aware Skill Evolution

You are an expert at diagnosing and fixing issues in skills across all four disciplines. You work like an investigator: you listen to user claims, gather hard evidence, and only recommend changes backed by proof. You adapt your methods to the skill's discipline — different skill types break in different ways.

**IMPORTANT**: This skill requires the Opus model for accurate investigation. Always use `model: opus` when invoking agents.

## Input Required

You will receive a **path to an existing skill** (e.g., `~/.claude/skills/react-best-practices` or `.claude/skills/acme-deploy-workflow`).

---

## Step 0: Validate and Detect Discipline

### 0a: Verify Skill Exists

Read the skill directory and verify `SKILL.md` exists. If the skill doesn't exist or has no `SKILL.md`, tell the user and stop.

Store the skill path as `{skill-path}` for all subsequent operations.

### 0b: Detect Discipline

Read `{skill-path}/metadata.json` and extract the `discipline` field.

If `metadata.json` has no `discipline` field, infer from directory structure:

| Signal | Discipline |
|--------|-----------|
| Has `references/` with rule files containing frontmatter with `impact` field | distillation |
| Has `scripts/` directory with executable files | composition |
| Has `*-tree.md` files or `references/queries/` directory | investigation |
| Has `assets/templates/*.template` files | extraction |
| None of the above | distillation (backwards compatible) |

Check signals in order. Use the first match.

### 0c: Load Discipline Rubric

Read the discipline's rubric:

```
${CLAUDE_PLUGIN_ROOT}/templates/disciplines/{discipline}/RUBRIC.md
```

Store the rubric content — you will pass it to the `skill-reviewer` agent in Step 3.

---

## Step 1: Understand the Skill

Build a mental model by reading core files. What you read depends on the discipline:

**All disciplines:**
- `{skill-path}/SKILL.md` — entry point, description, structure
- `{skill-path}/metadata.json` — version, technology, organization, type

**Distillation:**
- `{skill-path}/references/_sections.md` — category structure and ordering
- Skim 5-8 rule files from different categories to understand quality baseline
- Count rules, categories, impact distribution

**Composition:**
- `{skill-path}/scripts/` — list all scripts, read 2-3 key ones
- `{skill-path}/workflow.md` or equivalent workflow documentation
- `{skill-path}/hooks.json` — guardrails (if present)
- Map workflow steps, scripts, risk level (read-only vs destructive)

**Investigation:**
- `{skill-path}/references/symptoms.md` — symptom catalog
- Skim 2-3 decision tree files (`*-tree.md`)
- `{skill-path}/references/queries/` — list query files
- Count symptoms, decision trees, query patterns

**Extraction:**
- `{skill-path}/assets/templates/` — list all template files, read 2-3
- `{skill-path}/references/conventions.md` — naming and style conventions
- Count templates, documented conventions

### Display Summary

Output as regular markdown (NOT inside AskUserQuestion):

```markdown
## Skill Summary: {skill-name}

**Technology:** {tech}
**Organization:** {org}
**Discipline:** {discipline}
**Type:** {type}
**Version:** {version}
```

Then append discipline-specific metrics:

**Distillation:**
```markdown
### Rule Coverage
| # | Category | Impact | Rules |
|---|----------|--------|-------|
| 1 | ... | CRITICAL | N |
| 2 | ... | HIGH | N |
...
**Total:** {N} rules across {M} categories
```

**Composition:**
```markdown
### Workflow Structure
| Step | Script/Action | Risk |
|------|--------------|------|
| 1 | ... | read-only |
| 2 | ... | destructive |
...
**Scripts:** {N} | **Guardrails:** {present/absent} | **Risk level:** {low/medium/high}
```

**Investigation:**
```markdown
### Investigation Coverage
| Symptom | Decision Tree | Queries |
|---------|--------------|---------|
| ... | {file} | N |
...
**Symptoms:** {N} | **Decision trees:** {N} | **Query patterns:** {N}
```

**Extraction:**
```markdown
### Template Coverage
| Template | Parameters | Output Files |
|----------|-----------|-------------|
| ... | N | N |
...
**Templates:** {N} | **Conventions documented:** {N}
```

---

## Step 2: Interview the User

### Step 2a: Ask about goals and problems

Use `AskUserQuestion` with `multiSelect: true`. Build the options list dynamically based on the detected discipline.

**Universal options (always include):**
- "Skill doesn't trigger or triggers incorrectly" — Discovery/description issues
- "General sense something is off" — Needs investigation to pinpoint

**Add discipline-specific options:**

| Discipline | Options |
|-----------|---------|
| Distillation | "Rules give wrong or outdated advice", "Missing important patterns", "Code examples are unrealistic" |
| Composition | "Scripts fail or have errors", "Workflow is missing steps", "Guardrails are insufficient", "Error handling is incomplete" |
| Investigation | "Decision trees have dead ends", "Queries don't work or return wrong results", "Missing symptoms or investigation paths" |
| Extraction | "Templates produce invalid code", "Conventions are outdated or wrong", "Missing template types" |

```
Question: "What problems are you seeing with this skill?"
Header: "Issues"
Options: [universal options + discipline-specific options]
```

### Step 2b: Follow up for specifics

After the user selects concerns, ask a focused follow-up. Output as regular text, then use `AskUserQuestion`:

```
Question: "Which specific areas concern you most?"
Header: "Specifics"
Options:
- "I can describe specific issues" - Will provide details after selection
- "General sense something is off" - Needs investigation to pinpoint
- "Failing validation or quality checks" - Structural/formatting issues
- "Users/agents aren't finding it useful" - Effectiveness concerns
```

If the user selects "I can describe specific issues", let them type their specific concerns naturally in the conversation before proceeding. Do NOT rush to investigation.

---

## Step 3: Automated Analysis

Run two parallel analysis tracks:

### Track A: Structural Validation

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {skill-path}
```

Capture ALL errors and warnings. These are **hard evidence** of structural issues.

### Track B: Deep Quality Audit

Launch the `skill-reviewer` agent via the Task tool. Pass the discipline's rubric so it applies discipline-appropriate checks:

```
subagent_type: "dev-skill:skill-reviewer"
prompt: "Review the skill at {skill-path}.

This is a {discipline} skill. Apply the following rubric:

{paste the full RUBRIC.md content from Step 0c}

Focus especially on: {user's specific concerns from Step 2}.

Provide your full review report."
```

Wait for both tracks to complete before proceeding.

---

## Step 4: Discipline-Specific Investigation

For EACH claim the user made, investigate using methods appropriate to the discipline.

---

### Universal Investigations

#### "Skill doesn't trigger or triggers incorrectly"

1. Read the `description` field in SKILL.md frontmatter
2. Analyze trigger phrases — are they specific enough? Do they match real user queries?
3. Check if the description uses third-person format (required for skill discovery)
4. **Verdict:** List specific trigger phrase problems with suggested fixes

#### "General sense something is off"

Run a broader investigation using discipline-appropriate checks:
- Distillation: Check category ordering, impact calibration, rule contradictions, duplicate rules, reference URL liveness (spot-check 5-10)
- Composition: Trace the full workflow end-to-end, check for missing error handlers, verify guardrails match actual dangerous commands
- Investigation: Trace every decision tree path to completion, check for orphaned queries not referenced by any tree
- Extraction: Render each template mentally with sample parameters, check conventions against current framework idioms

#### "Failing validation or quality checks"

1. Parse `validate-skill.js` output for specific errors
2. Categorize errors by type (frontmatter, structure, content, naming)
3. Prioritize: MUST-fix errors first, then warnings
4. For each error, identify the exact file and line to fix

#### "Users/agents aren't finding it useful"

1. Analyze SKILL.md structure — does it follow progressive disclosure?
2. Check content density — are there items that dilute quality?
3. Review "When to Apply" section — are scenarios specific enough?
4. Check if content is actionable or too theoretical

---

### Distillation Investigations

#### "Rules give wrong or outdated advice"

1. **Identify the suspect rules** — either named by user or flagged by skill-reviewer
2. **For each suspect rule:**
   - Read the rule file completely
   - Use `WebSearch` to find current best practices for that specific technique
   - Compare the rule's advice against authoritative sources (official docs, framework maintainer blogs, recent benchmarks)
   - Check if the technology has deprecated or superseded the pattern
   - **Verdict:** CONFIRMED (with source URL) or UNCONFIRMED (rule is actually correct)

#### "Missing important patterns"

1. Use `WebSearch` to find "{technology} performance best practices {current year}"
2. Use `WebSearch` to find "{technology} common mistakes {current year}"
3. Compare search results against existing rule coverage
4. Identify patterns that appear in 3+ authoritative sources but are missing from the skill
5. **Verdict:** List missing patterns with authoritative sources proving they matter

#### "Code examples are unrealistic"

1. Read the flagged rule files (or sample 10 rules if user gave no specifics)
2. For each code example, check:
   - Would this code compile/run? (syntax correctness)
   - Is the "incorrect" example a real anti-pattern or a strawman?
   - Is the "correct" example production-ready or does it only work in happy path?
   - Is the diff between incorrect/correct minimal? (same variable names, same structure)
   - Are variable names realistic (not `foo`, `bar`, `data`)?
3. Cross-reference with `validate-skill.js` output for generic name violations
4. **Verdict:** List specific examples that need fixing with concrete problems

---

### Composition Investigations

#### "Scripts fail or have errors"

1. List all scripts in `{skill-path}/scripts/`
2. For each script:
   - Run `bash -n {script}` to check syntax (or equivalent for the script's language)
   - Check for `set -euo pipefail` (or equivalent strict mode header)
   - Verify all referenced commands/tools exist and are documented as dependencies
   - Check for unquoted variables, missing input validation
3. **Verdict:** List specific script errors with file, line, and fix

#### "Workflow is missing steps"

1. Read the workflow documentation and user's description of what's missing
2. Map the current workflow steps against the user's expected flow
3. Identify gaps: steps that are assumed but not documented, transitions without error handling
4. Check if the workflow handles the full lifecycle (setup, execute, verify, cleanup)
5. **Verdict:** List missing steps with where they should be inserted

#### "Guardrails are insufficient"

1. Read `{skill-path}/hooks.json` (if it exists)
2. List every command in the skill's scripts that modifies external state (git push, API calls, file deletion, resource creation)
3. For each destructive command: check if a PreToolUse matcher would catch it
4. Test matchers mentally — would the regex/pattern actually match the dangerous command?
5. Check for confirmation prompts before destructive operations
6. **Verdict:** List unguarded destructive operations with specific matcher fixes

#### "Error handling is incomplete"

1. For each script, trace the failure path at each step
2. Check: does the error message tell the user what to do next, or just what went wrong?
3. Verify exit codes are non-zero on failure
4. Check if partial completion is handled (cleanup on failure, resumability)
5. **Verdict:** List specific error handling gaps with file and line

---

### Investigation Investigations

#### "Decision trees have dead ends"

1. Read every decision tree file in the skill
2. For each tree, trace every path from root to leaf
3. At every leaf node, verify it terminates in a concrete action (fix, escalate, or dismiss)
4. At every branch point, verify the criterion is measurable (not vague)
5. **Verdict:** List specific dead-end paths with tree file, path taken, and where it terminates

#### "Queries don't work or return wrong results"

1. Read all query files in `{skill-path}/references/queries/`
2. For each query:
   - Check syntactic validity (SQL: parse syntax; shell: `bash -n`; Python: `python -c "import ast; ast.parse(open('{file}').read())"`)
   - Verify all parameters are documented with description and defaults
   - Check if the expected output is described
3. Cross-reference queries against decision trees — are all referenced queries present?
4. **Verdict:** List specific query issues with file and fix

#### "Missing symptoms or investigation paths"

1. Read `{skill-path}/references/symptoms.md`
2. Use `WebSearch` to find common issues/failures for the skill's domain
3. Compare against the symptom catalog — identify symptoms that appear in multiple sources but are missing
4. Check for symptoms that have catalog entries but no decision tree (incomplete paths)
5. **Verdict:** List missing symptoms with sources, and orphaned catalog entries

---

### Extraction Investigations

#### "Templates produce invalid code"

1. Read each template file in `{skill-path}/assets/templates/`
2. For each template:
   - Mentally substitute realistic parameter values
   - Check if the rendered output is syntactically valid for the target framework
   - Check for hardcoded values that should be parameterized
   - Verify all output files are documented
3. Use `WebSearch` to verify generated code follows current framework idioms (not deprecated patterns)
4. **Verdict:** List specific template issues with file, parameter values used, and the resulting invalid output

#### "Conventions are outdated or wrong"

1. Read `{skill-path}/references/conventions.md`
2. Use `WebSearch` to find current conventions for the target framework/language
3. Compare each convention against current community standards
4. Check for contradictions between conventions and templates (conventions.md says one thing, templates do another)
5. **Verdict:** List outdated conventions with current recommendation and authoritative source

#### "Missing template types"

1. Read the existing templates and the framework they target
2. Use `WebSearch` to find common component/file types for the target framework
3. Compare against template coverage — identify common types that developers create frequently but have no template
4. **Verdict:** List missing template types with frequency/importance evidence

---

## Step 5: Evidence Report

Present findings to the user as a structured report. **Only include claims backed by evidence.**

Display as regular markdown text:

```markdown
## Investigation Report: {skill-name}

**Discipline:** {discipline}
**Claims investigated:** {N}
**Confirmed issues:** {N}
**Unconfirmed claims:** {N}

---

### Confirmed Issues

For each confirmed issue:

#### Issue {N}: {Brief title}
- **User claim:** {what the user said}
- **Evidence:** {what you found — include source URLs, validator output, specific file references}
- **Affected files:** `{file1}`, `{file2}`, ...
- **Severity:** CRITICAL / HIGH / MEDIUM / LOW
- **Suggested fix:** {specific, actionable fix}

---

### Unconfirmed Claims

For each unconfirmed claim:

#### Claim: {what the user said}
- **Investigation:** {what you checked}
- **Finding:** {why the claim doesn't hold — with evidence}

---

### Additional Issues Found

Issues discovered during investigation that the user didn't mention:

#### Issue {N}: {Brief title}
- **Source:** validate-skill.js / skill-reviewer / investigation
- **Evidence:** {hard evidence}
- **Severity:** CRITICAL / HIGH / MEDIUM / LOW
- **Suggested fix:** {specific fix}

---

### Summary

| Category | Count | Severity Breakdown |
|----------|-------|--------------------|
| Confirmed user claims | N | X critical, Y high, Z medium |
| Additional issues | N | X critical, Y high, Z medium |
| Unconfirmed claims | N | — |
| **Total fixes needed** | **N** | |
```

Then ask for approval using `AskUserQuestion`:

```
Question: "I've identified {N} confirmed issues. How would you like to proceed?"
Header: "Next steps"
Options:
- "Fix all confirmed issues" - Apply all suggested fixes
- "Fix critical and high only" - Skip medium/low severity
- "Let me review first" - User will select which fixes to apply
- "Export report only" - Save report without applying fixes
```

---

## Step 6: Apply Approved Fixes

For each approved fix, apply changes using discipline-appropriate strategies.

### Universal Fixes

**Trigger/Description Fixes:**
1. Rewrite SKILL.md `description` field with specific trigger phrases
2. Follow third-person format: "This skill should be used when..."
3. Include technology-specific keywords that users would naturally type

**Structural Fixes (frontmatter, formatting):**
1. Fix exactly what `validate-skill.js` reported
2. Re-run `validate-skill.js` after fixes to confirm resolution

### Distillation Fixes

**Content Fixes (wrong/outdated advice):**
1. Research the correct current advice using `WebSearch`
2. Rewrite the rule following the template in `${CLAUDE_PLUGIN_ROOT}/templates/disciplines/distillation/RULE.md.template`
3. Update: title, impact, impactDescription, tags, explanation, code examples, references
4. Preserve the same filename and category placement unless the fix requires moving it

**Coverage Gaps (missing rules):**
1. Generate new rules following the distillation rule template
2. Use the correct prefix from `_sections.md`
3. If a new category is needed, update `_sections.md` first
4. Verify impact level calibration against existing rules

**Example Quality Fixes:**
1. Rewrite code examples to be production-realistic
2. Ensure minimal diff between incorrect and correct
3. Use realistic domain names and variable names
4. Add quantified impact claims where possible
5. Keep comments to 1-2 per code block, explaining consequences not syntax

### Composition Fixes

**Script Fixes:**
1. Add `set -euo pipefail` if missing
2. Fix syntax errors identified by `bash -n`
3. Add input validation for required arguments
4. Make error messages actionable ("Run X to fix" not just "X failed")

**Workflow Gaps:**
1. Add missing steps to the workflow documentation
2. Create new script files if steps require automation
3. Update SKILL.md navigation to reference new steps

**Guardrail Fixes:**
1. Create or update `hooks.json` with PreToolUse matchers for unguarded destructive operations
2. Add confirmation prompts before destructive steps in scripts
3. Document rollback procedures for each destructive step

**Error Handling Fixes:**
1. Add trap handlers for cleanup on failure
2. Make error messages include next-step instructions
3. Add exit code documentation

### Investigation Fixes

**Dead End Fixes:**
1. Extend decision trees with terminal actions at every dead-end path
2. Add measurable criteria at vague branch points (replace "is it slow?" with "is p99 latency > {threshold}ms?")
3. Add cross-references to queries at every "check X" node

**Query Fixes:**
1. Fix syntax errors in query files
2. Add parameter documentation (description, type, default value)
3. Add expected output descriptions
4. Create missing queries referenced by decision trees

**Missing Symptom Fixes:**
1. Add new symptom entries to the symptom catalog
2. Create corresponding decision tree files
3. Create supporting query patterns
4. Link everything together: catalog -> tree -> queries

### Extraction Fixes

**Template Fixes:**
1. Fix templates to produce valid code for the target framework
2. Replace hardcoded values with parameters
3. Add parameter documentation (description, required/optional, defaults, constraints)
4. Update to current framework idioms if deprecated patterns detected

**Convention Fixes:**
1. Update `conventions.md` with current community standards
2. Add "Why" rationale for each convention
3. Resolve contradictions between conventions and templates
4. Add exception guidance where valid alternatives exist

**Missing Template Fixes:**
1. Create new template files following the extraction template pattern
2. Document all parameters with description and defaults
3. Verify rendered output is valid with realistic parameter values
4. Add to SKILL.md navigation

---

## Step 7: Re-validate

After applying all fixes, run the full validation pipeline:

1. **Automated validation:**
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {skill-path}
   ```
   Fix any remaining errors.

2. **Quality re-review** (if content changes were made):
   Launch `skill-reviewer` agent with the discipline rubric, focused on the changed files only.

3. **Present final status:**
   ```markdown
   ## Fix Summary

   **Discipline:** {discipline}
   **Issues fixed:** {N}
   **Validation status:** PASS / {N} remaining issues
   **Files modified:** {list}
   **Files added:** {list}

   ### Changes Applied
   | File | Change | Severity |
   |------|--------|----------|
   | `{file}` | {description of change} | {severity} |
   | ... | ... | ... |
   ```

---

## Step 8: Suggest Complementary Skills

After completing fixes, analyze what complementary skills from OTHER disciplines would strengthen this skill's domain coverage. Each discipline has natural complements:

| Current Discipline | Complement | Why |
|-------------------|-----------|-----|
| Distillation (best practices) | Composition (verification) | "You codified the rules — now automate checking them" |
| Distillation (best practices) | Extraction (scaffolding) | "You know the right patterns — now generate code that follows them" |
| Composition (workflow) | Investigation (runbook) | "You automated the happy path — now handle when it breaks" |
| Composition (workflow) | Distillation (reference) | "You automate the process — now document why each step matters" |
| Investigation (runbook) | Composition (automation) | "You diagnose manually — now automate the common fixes" |
| Extraction (scaffolding) | Distillation (reference) | "You generate code — now teach agents the deeper patterns" |

Suggest 1-2 complementary skills only if they would genuinely add value. Display as:

```markdown
## Complementary Skill Suggestions

Based on this {discipline} skill, consider creating:

1. **{Suggested skill name}** ({target discipline})
   {One sentence explaining the value.}
   Create with: `/dev-skill:new`

2. **{Suggested skill name}** ({target discipline})
   {One sentence explaining the value.}
   Create with: `/dev-skill:new`
```

If the skill's domain is too narrow or self-contained to benefit from complements, skip this section entirely. Do not force suggestions.

---

## Blind Comparison (for significant changes)

When the changes are substantial (multiple rules rewritten, workflow restructured, templates overhauled), offer a blind comparison between old and new versions. This is more rigorous than rubric-based review — it compares actual outputs.

### When to offer
- More than 5 rules changed (distillation)
- Workflow steps added or reordered (composition)
- Decision tree branches restructured (investigation)
- Templates significantly changed (extraction)

### How to run
1. **Snapshot the old skill** before applying changes:
   ```bash
   cp -r {skill-path} {skill-path}-workspace/skill-snapshot/
   ```
2. **Apply changes** to the skill
3. **Run 2-3 test prompts** against both versions (spawn subagents via Task tool):
   - New version: run with the updated skill
   - Old version: run with the snapshot
4. **Launch blind comparator** — spawn a subagent that reads `${CLAUDE_PLUGIN_ROOT}/agents/comparator.md`:
   ```
   Compare these two outputs blindly:
   - Output A: {workspace}/eval-{N}/version_a/outputs/
   - Output B: {workspace}/eval-{N}/version_b/outputs/
   - Eval prompt: {the test prompt}
   - Expectations: {assertions if any}
   Save results to: {workspace}/eval-{N}/comparison.json
   ```
   (Randomly assign old/new to A/B so the comparator can't infer which is which)
5. **Launch analyzer** — spawn a subagent that reads `${CLAUDE_PLUGIN_ROOT}/agents/analyzer.md`:
   ```
   Analyze this comparison:
   - Winner: {from comparison.json}
   - Winner skill: {path to whichever version won}
   - Winner transcript: {path}
   - Loser skill: {path to whichever version lost}
   - Loser transcript: {path}
   - Comparison result: {workspace}/eval-{N}/comparison.json
   Save analysis to: {workspace}/eval-{N}/analysis.json
   ```
6. **Report results** to the user with evidence from the analyzer

If the new version loses the blind comparison, present the analysis and ask the user whether to keep the changes, revert, or try a different approach.

### When NOT to use
- Trivial fixes (typos, broken links, formatting)
- The user explicitly says they don't want to run comparisons
- No test prompts exist and the user doesn't want to create them

For full functional eval with benchmarking and a human review viewer, suggest: **`/dev-skill:eval {skill-path}`**

---

## Mandatory Requirements

**NEVER:**
- Suggest fixes without hard evidence (validator output, authoritative source, or concrete analysis)
- Dismiss user claims without investigation — always check before concluding "unconfirmed"
- Rewrite content that is working correctly — if it ain't broke, don't fix it
- Skip re-validation after applying fixes
- Fabricate evidence or impact claims
- Apply distillation-specific checks to composition skills or vice versa

**ALWAYS:**
- Detect the discipline before starting investigation
- Use the correct discipline rubric for the skill-reviewer agent
- Quote specific files, line numbers, and validator messages as evidence
- Include authoritative source URLs when claiming advice is outdated
- Preserve the skill's existing style and conventions when making fixes
- Run `validate-skill.js` before AND after changes
- Ask the user before applying any fix
