---
description: Refactor a shell script to follow Google Shell Style Guide
argument-hint: path/to/script.sh
allowed-tools: [Bash, Read, Edit, Glob, AskUserQuestion, Task]
---

# Refactor Shell Script to Google Style Guide

Refactor the specified shell script to follow Google Shell Style Guide.

## Progress Tracking

Create TodoWrite with each step as a todo item:
1. Identify target script
2. Read script and analyze
3. Run parallel analysis (shellcheck + shell-expert dispatch)
4. Load style guide
5. Collect results and identify violations
6. Propose changes
7. Apply refactoring
8. Verify refactored script
9. Expert review (optional)
10. Final report

Mark each step `in_progress` when starting, `completed` when done.

## Step 1: Identify Target Script

If `$ARGUMENTS` is provided, use it as the target script path. Store this path for use in all subsequent steps.

Otherwise, find shell scripts in the project and prompt user:

```bash
fd -e sh -e bash --type f 2>/dev/null | head -20
```

Use AskUserQuestion to let user select which file to refactor:

### File Selection
- Header: "Script"
- Question: "Which shell script would you like to refactor?"
- Options: [dynamically populated from fd results, up to 4 scripts]

**Important:** Store the selected/provided script path. You will need this exact path for shellcheck, verification, and dispatching the shell-expert agent.

## Step 2: Read Script and Analyze

Read the target script content to understand its structure and identify style issues.

## Step 3: Run Parallel Analysis

Run shellcheck and dispatch shell-expert in parallel for faster analysis.

### 3a: Shellcheck (immediate)

```bash
shellcheck -f gcc "<target_script_path>" 2>&1 || true
```

If shellcheck is not installed, warn the user:
> Note: shellcheck is not installed. Consider installing it for better analysis:
> - macOS: `brew install shellcheck`
> - Linux: `apt install shellcheck`

Parse shellcheck output to:
- Identify error codes (SC1xxx = parsing, SC2xxx = quoting/expansion, SC3xxx = bashisms)
- Map issues to Google Style Guide rules
- Prioritize critical issues:
  - SC2086: Double quote to prevent globbing and word splitting
  - SC2046: Quote this to prevent word splitting
  - SC2006: Use $(...) notation instead of legacy backticks

### 3b: Shell-expert dispatch (parallel)

In the same response as shellcheck, dispatch shell-expert to analyze the original script:

```
Use Task tool with:
- subagent_type: "shell:shell-expert"
- prompt: "REVIEW the shell script at <target_script_path>"
```

**Do not wait for shell-expert to complete.** Continue to Step 4 while the agent runs in parallel. Results will be collected in Step 5.

## Step 4: Load Style Guide

Load the google-shell-style skill for comprehensive style rules:

```
Use Skill tool with: skill: "shell:google-shell-style"
```

This provides formatting, quoting, naming, and anti-pattern rules for the refactoring.

## Step 5: Collect Results and Identify Violations

### 5a: Collect shell-expert results

The shell-expert agent dispatched in Step 3b should now have results. Collect and incorporate:
- Critical issues identified by the expert
- Important issues (should fix)
- Minor suggestions

### 5b: Combine all findings

Merge findings from:
1. Shellcheck output (Step 3a)
2. Shell-expert analysis (Step 5a)
3. Manual style guide analysis (using rules from Step 4)

For each violation found, note:
- Line number
- Current code
- Recommended fix
- Rule reference (shellcheck code or style guide section)

## Step 6: Propose Changes

Present a summary of proposed changes:

**Summary format:**
- Total violations found: N
- Critical fixes (must apply): N
- Style improvements: N
- Estimated lines affected: N

Then use AskUserQuestion to confirm:

### Change Approval
- Header: "Refactor"
- Question: "How would you like to proceed with these changes?"
- Options:
  - Apply all: Apply all changes at once
  - Review each: Show me each change before applying
  - Critical only: Only apply critical fixes, skip style improvements
  - Cancel: Do not make any changes

## Step 7: Apply Refactoring

Use the Edit tool to apply approved changes to the script.

Apply changes in order:
1. Critical fixes first (security, correctness)
2. Structural changes (main function, function organization)
3. Formatting changes (indentation, line length)
4. Style improvements (variable braces, quoting)

## Step 8: Verify Refactored Script

After applying changes, run verification.

### Syntax Check
```bash
bash -n "<target_script_path>"
```
If syntax check fails, fix the issue before proceeding.

### Shellcheck Comparison
```bash
shellcheck -f gcc "<target_script_path>" 2>&1 || true
```

Compare with baseline from Step 3:
- Count errors/warnings before and after
- Refactoring should reduce issues, not add them
- If new issues appeared, investigate and fix

### Test Depth Selection

Use AskUserQuestion to ask how thoroughly to test:

**Header:** "Test"
**Question:** "How would you like to verify the script still works?"
**Options:**
- Syntax only: Syntax check passed, proceed to expert review
- Dry run: Also run --help or --dry-run if script supports it
- Manual: I'll test it myself before continuing

If user selects "Dry run" and script appears to support it:
```bash
"<target_script_path>" --help 2>&1 | head -20 || "<target_script_path>" --dry-run 2>&1 | head -20 || echo "Script does not support --help or --dry-run"
```

## Step 9: Expert Review (Optional)

Post-refactor expert review is **optional** since shell-expert already analyzed the original script in Step 3b.

### Skip if ALL of these are true:
- Shellcheck shows improvement (fewer issues than baseline)
- No Critical issues found in Step 5
- Syntax check passed in Step 8

If skipping, note in final report: "Expert review: Skipped (improvements confirmed by shellcheck)"

### Run if ANY of these are true:
- Critical issues were found in Step 5
- Shellcheck shows no improvement or regression
- User explicitly requests additional validation

When running, use **QUICK_REVIEW mode** for fast validation:

**Use the Task tool with these parameters:**
- `subagent_type`: `"shell:shell-expert"`
- `prompt`: Use QUICK_REVIEW trigger

**Example Task prompt:**
```
QUICK REVIEW the shell script at /Users/example/scripts/deploy.sh

This script was just refactored. Validate no Critical issues remain.
```

**IMPORTANT:** The file path in the prompt must be the actual path you stored in Step 1, not a placeholder.

## Step 10: Final Report

Present final results:

```
## Refactoring Complete

**File:** [actual path from Step 1]

### Changes Applied
- [List of key changes made, grouped by category]

### Shellcheck Comparison
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Errors | N | N | -N |
| Warnings | N | N | -N |
| Info | N | N | -N |

### Verification Results
- Syntax check: [PASS/FAIL]
- Shellcheck delta: [Improved/Same/Regressed]
- Test run: [PASS/SKIPPED/N/A]

### Shell Expert Assessment
- **Initial Review (Step 3b):** [Summary of issues found on original script]
- **Post-Refactor (Step 9):** [PASS/NEEDS_FIXES/SKIPPED]
- **Confidence:** [HIGH/MODERATE/LOW]

### Remaining Items (if any)
- [Any issues that still need attention]
```
