---
description: Refactor shell script to follow Google Shell Style Guide
argument-hint: <path/to/script.sh>
allowed-tools: Bash, Read, Edit, Glob, AskUserQuestion, Task, Skill, mcp__plugin_serena_serena__activate_project, mcp__plugin_serena_serena__find_symbol, mcp__plugin_serena_serena__find_referencing_symbols, mcp__plugin_serena_serena__get_symbols_overview, mcp__plugin_serena_serena__search_for_pattern, mcp__plugin_serena_serena__read_file, mcp__plugin_serena_serena__list_dir
---

# Shell Script Refactoring

Refactor a shell script to follow Google Shell Style Guide best practices.

## Process

### Step 1: Identify Target Script

If no path provided, search for shell scripts:
```bash
find . -name "*.sh" -type f 2>/dev/null | head -20
```

Then use AskUserQuestion to let user select which script to refactor.

### Step 2: Analyze Script

Load the style guide knowledge:
```
Skill("shell:google-shell-style")
```

Read the target script and perform concurrent analysis:

1. **Run shellcheck** (if available):
   ```bash
   shellcheck --severity=style "${script_path}" 2>&1 || true
   ```

   Install if missing:
   - macOS: `brew install shellcheck`
   - Linux: `apt install shellcheck` or `yum install shellcheck`

2. **Dispatch shell-expert agent** for comprehensive review:
   ```
   Task(subagent_type: "shell:shell-expert", prompt: "Review ${script_path} in REVIEW mode")
   ```

### Step 3: Propose Changes

Present a summary of violations found:

| Category | Count | Examples |
|----------|-------|----------|
| Critical | N | Command injection, unquoted vars |
| Important | N | Missing error handling |
| Minor | N | Style/formatting |

Ask user which level of refactoring they want:

```
AskUserQuestion:
  header: "Scope"
  question: "Which issues should I fix?"
  options:
    - label: "Critical only"
      description: "Fix security issues and bugs only"
    - label: "Critical + Important (Recommended)"
      description: "Fix bugs, error handling, and correctness issues"
    - label: "All issues"
      description: "Full style guide compliance including formatting"
```

### Step 4: Apply Refactoring

Apply fixes in priority order:

1. **Critical fixes first** - Security and data loss risks
2. **Important fixes** - Correctness and reliability
3. **Minor fixes** - Style and formatting

For each fix:
- Show the line number and issue
- Apply the fix using Edit tool
- Move to next issue

### Step 5: Verify and Report

After all fixes applied:

1. **Verify syntax**:
   ```bash
   bash -n "${script_path}"
   ```

2. **Re-run shellcheck** to confirm improvements:
   ```bash
   shellcheck --severity=style "${script_path}" 2>&1 || true
   ```

3. **Present summary**:
   ```markdown
   ## Refactoring Complete

   | Metric | Before | After |
   |--------|--------|-------|
   | Shellcheck issues | X | Y |
   | Critical issues | X | 0 |
   | Script lines | X | X |

   ### Changes Made
   - [List of significant changes]

   ### Remaining Items
   - [Any issues not addressed and why]
   ```

## Tips

- If shellcheck is not available, the shell-expert agent analysis is sufficient
- Prefer atomic, small edits over large rewrites
- Preserve the script's functionality - only improve style and safety
- For very large scripts (500+ lines), consider refactoring in sections
