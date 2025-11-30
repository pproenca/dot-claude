---
description: Refactor a shell script to follow Google Shell Style Guide
argument-hint: "<path/to/script.sh>"
allowed-tools: [Bash, Read, Edit, Glob, AskUserQuestion, Task, Skill]
---

# Refactor Shell Script to Google Style Guide

Refactor the specified shell script to follow Google Shell Style Guide.

## Progress Tracking

Create TodoWrite with each step:
1. Identify and read target script
2. Analyze (shellcheck + shell-expert in parallel)
3. Propose changes
4. Apply refactoring
5. Verify and report

## Step 1: Identify and Read Target Script

If `$ARGUMENTS` is provided, use it as the target script path.

Otherwise, find shell scripts and prompt user:

```bash
fd -e sh -e bash --type f 2>/dev/null | head -20
```

Use AskUserQuestion:
- Header: "Script"
- Question: "Which shell script would you like to refactor?"
- Options: [up to 4 scripts from fd results]

Read the script content to understand its structure.

## Step 2: Analyze

Run these in parallel:

### Shellcheck
```bash
shellcheck -f gcc "<target_script_path>" 2>&1 || true
```

If shellcheck not installed, note: `brew install shellcheck` (macOS) or `apt install shellcheck` (Linux).

### Shell-expert dispatch
```
Task tool with:
- subagent_type: "shell:shell-expert"
- prompt: "REVIEW the shell script at <target_script_path>"
```

### Load style guide
```
Skill tool with: skill: "shell:google-shell-style"
```

Combine findings from shellcheck and shell-expert. For each violation note:
- Line number
- Current code
- Recommended fix
- Rule reference

## Step 3: Propose Changes

Present summary:
- Total violations: N
- Critical fixes: N
- Style improvements: N

Use AskUserQuestion:
- Header: "Refactor"
- Question: "How would you like to proceed?"
- Options:
  - Apply all: Apply all changes
  - Critical only: Only apply critical fixes
  - Cancel: Do not make changes

## Step 4: Apply Refactoring

Use Edit tool to apply approved changes in order:
1. Critical fixes (security, correctness)
2. Structural changes (main function, organization)
3. Style improvements (formatting, quoting)

## Step 5: Verify and Report

### Syntax check
```bash
bash -n "<target_script_path>"
```

### Shellcheck comparison
```bash
shellcheck -f gcc "<target_script_path>" 2>&1 || true
```

Compare with baseline - refactoring should reduce issues.

### Final Report

```
## Refactoring Complete

**File:** [path]

### Changes Applied
- [key changes by category]

### Shellcheck Comparison
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Errors | N | N | -N |
| Warnings | N | N | -N |

### Verification
- Syntax check: [PASS/FAIL]
- Shellcheck delta: [Improved/Same/Regressed]

### Shell Expert Assessment
- **Initial Review:** [summary]
- **Recommendation:** [PASS/NEEDS_FIXES]
```
