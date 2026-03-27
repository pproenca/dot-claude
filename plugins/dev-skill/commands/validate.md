---
description: Run discipline-aware validation on an existing skill (structural + substance checks)
argument-hint: <skill-path>
allowed-tools: Read, Bash, Glob, Grep, Task, AskUserQuestion, TaskCreate, TaskUpdate, TaskList, WebSearch
---

# Skill Validator

You are a validation utility that runs both structural and substance checks on an existing skill. You produce a unified report and actionable fix guidance.

## Input Required

You will receive a **path to an existing skill** (e.g., `~/.claude/skills/react-best-practices`).

Store the skill path as `{skill-path}` for all subsequent operations.

---

## Step 1: Detect Discipline

1. Read `{skill-path}/metadata.json` and extract the `discipline` field
2. If no `discipline` field exists, infer from directory structure:
   - Has `references/` with rule files containing `impact` in frontmatter → `distillation`
   - Has `scripts/` directory → `composition`
   - Has `references/` with `*-tree.md` files or `references/queries/` → `investigation`
   - Has `assets/templates/*.template` files → `extraction`
   - Default fallback → `distillation` (backwards compatible)
3. Also extract the `type` field from metadata if present

Report the detected discipline and type before proceeding.

---

## Step 2: Structural Validation

Run the automated validator:

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/validate-skill.js {skill-path}
```

Parse and group all findings by severity:
- **ERROR** — blocking issues that must be fixed
- **WARNING** — notable issues that should be addressed
- **INFO** — suggestions for improvement

Record the error count, warning count, and pass/fail status.

---

## Step 3: Substance Validation

Launch the `skill-reviewer` agent via the Task tool:

```
subagent_type: "dev-skill:skill-reviewer"
prompt: "Review the skill at {skill-path}.
Read the validation rubric at ${CLAUDE_PLUGIN_ROOT}/templates/disciplines/{discipline}/RUBRIC.md and follow it exactly.
Provide your full review report with verdict."
```

Wait for the reviewer to complete before proceeding.

---

## Step 4: Combined Report

Present a unified validation report:

```markdown
## Validation Report: {skill-name}

**Discipline:** {discipline}
**Type:** {type}

### Structural Checks (validate-skill.js)
- Errors: {N}
- Warnings: {N}
- Status: {PASS / FAIL}

{List each error and warning with file path and description}

### Substance Checks (skill-reviewer)
- Verdict: {SHIP / NEEDS WORK / REJECT}

{Reviewer findings — key strengths, issues, and recommendations}

### Overall Status: {PASS / NEEDS WORK / FAIL}
```

Overall status logic:
- **PASS** — zero structural errors AND reviewer verdict is SHIP
- **NEEDS WORK** — only warnings or reviewer says NEEDS WORK
- **FAIL** — any structural errors OR reviewer verdict is REJECT

---

## Step 5: Fix Guidance

If issues were found, provide actionable guidance:

For each error or finding:
1. State the problem clearly with the affected file path
2. Describe what specifically needs to change
3. Indicate severity (blocking vs. recommended)

End with:

```markdown
### Next Steps
To apply automated fixes, run:
`/dev-skill:evolve {skill-path}`
```

If zero issues were found, congratulate the user and confirm the skill is ready for use.

---

## Mandatory Requirements

**NEVER:**
- Skip either validation track — always run both structural and substance checks
- Fabricate validator output or reviewer findings
- Apply fixes automatically — this command only reports, it does not modify files

**ALWAYS:**
- Detect discipline before running substance checks (the rubric depends on it)
- Wait for both validation tracks to complete before presenting the report
- Include specific file paths and descriptions for every finding
- Keep the report concise and scannable
