# Plugin Consolidation Migration Plan

> **For Claude:** REQUIRED SUB-SKILL: Use super:executing-plans to implement this plan task-by-task.

**Goal:** Consolidate 8 plugins into 3 plugins (core, dev, doc) to reduce cognitive load and management overhead while preserving all functionality.

**Architecture:** Merge `super` + `commit` + `shell` + `debug` into a single `core` plugin. Keep `dev` and `doc` as standalone domain-specific plugins. Archive `analyze` and `blackbox` as optional utilities.

**Tech Stack:** Bash for file operations, Python for hook scripts, JSON for plugin configuration, sed/grep for cross-reference updates.

---

## Pre-Migration Checklist

- [ ] Create git branch: `git checkout -b refactor/plugin-consolidation`
- [ ] Ensure all tests pass: `./scripts/validate-plugins.sh`
- [ ] Backup current state: `git stash` any uncommitted work

---

## Phase 1: Create Core Plugin Scaffold

### Task 1.1: Create core plugin directory structure

**Files:**
- Create: `plugins/core/.claude-plugin/plugin.json`
- Create: `plugins/core/skills/` (directory)
- Create: `plugins/core/agents/` (directory)
- Create: `plugins/core/commands/` (directory)
- Create: `plugins/core/hooks/` (directory)
- Create: `plugins/core/cheatsheets/` (directory)
- Create: `plugins/core/scripts/` (directory)
- Create: `plugins/core/tests/` (directory)

**Step 1: Create directory structure**

```bash
mkdir -p plugins/core/.claude-plugin
mkdir -p plugins/core/skills
mkdir -p plugins/core/agents
mkdir -p plugins/core/commands
mkdir -p plugins/core/hooks
mkdir -p plugins/core/cheatsheets
mkdir -p plugins/core/scripts
mkdir -p plugins/core/tests
mkdir -p plugins/core/lib
mkdir -p plugins/core/references
```

**Step 2: Create plugin.json**

```json
{
  "name": "core",
  "version": "1.0.0",
  "description": "Core workflows for Claude Code: TDD enforcement, verification, debugging, git commits, shell scripting, and distributed systems debugging",
  "homepage": "https://github.com/pedroproenca/dot-claude/tree/main/plugins/core",
  "repository": "https://github.com/pedroproenca/dot-claude",
  "license": "MIT",
  "keywords": [
    "workflows",
    "tdd",
    "debugging",
    "git",
    "commits",
    "shell",
    "verification",
    "best-practices"
  ],
  "author": {
    "name": "Pedro Proenca"
  }
}
```

**Step 3: Verify structure**

Run: `ls -la plugins/core/`
Expected: All directories created

**Step 4: Commit scaffold**

```bash
git add plugins/core/
git commit -m "feat(core): create plugin scaffold for consolidation"
```

---

## Phase 2: Migrate Super Plugin to Core

### Task 2.1: Copy super skills to core

**Files:**
- Copy: `plugins/super/skills/*` → `plugins/core/skills/`

**Step 1: Copy all skill directories**

```bash
cp -r plugins/super/skills/* plugins/core/skills/
```

**Step 2: Verify copy**

Run: `ls plugins/core/skills/ | wc -l`
Expected: 20 (matching super's skill count)

**Step 3: Commit**

```bash
git add plugins/core/skills/
git commit -m "feat(core): migrate super skills"
```

---

### Task 2.2: Copy super agents to core

**Files:**
- Copy: `plugins/super/agents/*` → `plugins/core/agents/`

**Step 1: Copy all agent files**

```bash
cp plugins/super/agents/*.md plugins/core/agents/
```

**Step 2: Verify copy**

Run: `ls plugins/core/agents/`
Expected: code-reviewer.md, diagram-generator.md, security-reviewer.md

**Step 3: Commit**

```bash
git add plugins/core/agents/
git commit -m "feat(core): migrate super agents"
```

---

### Task 2.3: Copy super commands to core

**Files:**
- Copy: `plugins/super/commands/*` → `plugins/core/commands/`

**Step 1: Copy all command files**

```bash
cp plugins/super/commands/*.md plugins/core/commands/
```

**Step 2: Verify copy**

Run: `ls plugins/core/commands/`
Expected: brainstorm.md, context.md, exec.md, notes.md, plan.md

**Step 3: Commit**

```bash
git add plugins/core/commands/
git commit -m "feat(core): migrate super commands"
```

---

### Task 2.4: Copy super hooks to core

**Files:**
- Copy: `plugins/super/hooks/*` → `plugins/core/hooks/`

**Step 1: Copy hook files**

```bash
cp plugins/super/hooks/*.sh plugins/core/hooks/
cp plugins/super/hooks/hooks.json plugins/core/hooks/hooks.json
```

**Step 2: Verify copy**

Run: `ls plugins/core/hooks/`
Expected: hooks.json, session-start.sh, tdd-guard.sh, worktree-guard.sh

**Step 3: Commit**

```bash
git add plugins/core/hooks/
git commit -m "feat(core): migrate super hooks"
```

---

### Task 2.5: Copy super lib to core

**Files:**
- Copy: `plugins/super/lib/*` → `plugins/core/lib/`

**Step 1: Copy lib files**

```bash
cp -r plugins/super/lib/* plugins/core/lib/ 2>/dev/null || echo "No lib files to copy"
```

**Step 2: Commit if files exist**

```bash
git add plugins/core/lib/ 2>/dev/null && git commit -m "feat(core): migrate super lib" || echo "No lib to commit"
```

---

## Phase 3: Merge Commit Plugin into Core

### Task 3.1: Copy commit skills to core

**Files:**
- Copy: `plugins/commit/skills/*` → `plugins/core/skills/`

**Step 1: Copy skill directories**

```bash
cp -r plugins/commit/skills/* plugins/core/skills/
```

**Step 2: Verify**

Run: `ls plugins/core/skills/git-commit/`
Expected: SKILL.md

**Step 3: Commit**

```bash
git add plugins/core/skills/
git commit -m "feat(core): migrate commit skills"
```

---

### Task 3.2: Copy commit agents to core

**Files:**
- Copy: `plugins/commit/agents/*` → `plugins/core/agents/`

**Step 1: Copy agent files**

```bash
cp plugins/commit/agents/*.md plugins/core/agents/
```

**Step 2: Verify**

Run: `ls plugins/core/agents/commit-organizer.md`
Expected: File exists

**Step 3: Commit**

```bash
git add plugins/core/agents/
git commit -m "feat(core): migrate commit agents"
```

---

### Task 3.3: Copy commit commands to core

**Files:**
- Copy: `plugins/commit/commands/*` → `plugins/core/commands/`

**Step 1: Copy command files**

```bash
cp plugins/commit/commands/*.md plugins/core/commands/
```

**Step 2: Verify**

Run: `ls plugins/core/commands/ | grep -E "new|pr|reset"`
Expected: new.md, pr.md, reset.md

**Step 3: Commit**

```bash
git add plugins/core/commands/
git commit -m "feat(core): migrate commit commands"
```

---

### Task 3.4: Merge commit hooks into core hooks.json

**Files:**
- Modify: `plugins/core/hooks/hooks.json`
- Copy: `plugins/commit/hooks/*.py` → `plugins/core/hooks/`

**Step 1: Copy Python hook scripts**

```bash
cp plugins/commit/hooks/*.py plugins/core/hooks/
```

**Step 2: Merge hooks.json manually**

Read both files and merge the hook arrays. The merged hooks.json should contain:
- All SessionStart hooks from both
- All PreToolUse hooks from both
- All PostToolUse hooks from commit
- All Stop hooks from super

The merged `plugins/core/hooks/hooks.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh"
          }
        ]
      },
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 -S ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py",
            "timeout": 5
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/tdd-guard.sh",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/worktree-guard.sh",
            "timeout": 3
          }
        ]
      },
      {
        "matcher": "Bash(git:*)",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -S ${CLAUDE_PLUGIN_ROOT}/hooks/pretooluse_safety.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash(git commit:*)",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -S ${CLAUDE_PLUGIN_ROOT}/hooks/posttooluse_validate.py",
            "timeout": 10
          },
          {
            "type": "prompt",
            "prompt": "Review the commit that was just created. Run: git log -1 --format='%B' && git diff --stat HEAD~1..HEAD\n\nEvaluate the commit against Conventional Commits standards:\n\n1. **Subject line**: Is it imperative mood? Specific about WHAT changed? 50-72 chars?\n\n2. **Body (if present)**: Does it explain WHY, not just repeat WHAT the code shows?\n\n3. **Scope**: Is this ONE logical change? Are tests included with their feature/fix?\n\n4. **Separation**: Is refactoring mixed with features/fixes? (violation)\n\nIf ANY issue found, output 'ISSUE: [description]' and suggest amending.\n\nIf the commit is good, output 'VALIDATED: Commit follows Conventional Commits standards.'"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review the conversation for two conditions:\n\n1. VERIFICATION: If the agent claimed work is 'complete', 'fixed', 'passing', or 'done', check if verification commands (test, build, lint) were run with actual output shown BEFORE the claim.\n\n2. FINISHING WORKFLOW: If the conversation involved executing a plan (look for 'executing-plans', 'subagent-driven-development', or similar workflow language), check if 'finishing-a-development-branch' skill was used to present the 4 options (merge, PR, keep, discard).\n\nReturn {\"decision\": \"block\", \"reason\": \"Missing verification evidence (super:verification-before-completion)\"} if condition 1 fails.\nReturn {\"decision\": \"block\", \"reason\": \"Plan execution detected but finishing-a-development-branch not used. Use the skill to present merge/PR/keep/discard options.\"} if condition 2 fails.\nReturn {\"decision\": \"approve\"} if all conditions pass or don't apply.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**Step 3: Verify JSON is valid**

Run: `jq . plugins/core/hooks/hooks.json`
Expected: Valid JSON output, no errors

**Step 4: Commit**

```bash
git add plugins/core/hooks/
git commit -m "feat(core): merge commit hooks into core"
```

---

### Task 3.5: Copy commit cheatsheets to core

**Files:**
- Copy: `plugins/commit/cheatsheets/*` → `plugins/core/cheatsheets/`

**Step 1: Copy cheatsheet files**

```bash
cp -r plugins/commit/cheatsheets/* plugins/core/cheatsheets/
```

**Step 2: Verify**

Run: `ls plugins/core/cheatsheets/`
Expected: conventional-commits.md

**Step 3: Commit**

```bash
git add plugins/core/cheatsheets/
git commit -m "feat(core): migrate commit cheatsheets"
```

---

### Task 3.6: Copy commit scripts to core

**Files:**
- Copy: `plugins/commit/scripts/*` → `plugins/core/scripts/`

**Step 1: Copy script files**

```bash
cp plugins/commit/scripts/* plugins/core/scripts/
```

**Step 2: Verify**

Run: `ls plugins/core/scripts/`
Expected: analyze_branch.py, commit.sh

**Step 3: Commit**

```bash
git add plugins/core/scripts/
git commit -m "feat(core): migrate commit scripts"
```

---

### Task 3.7: Copy commit tests to core

**Files:**
- Copy: `plugins/commit/tests/*` → `plugins/core/tests/`

**Step 1: Copy test files**

```bash
cp -r plugins/commit/tests/* plugins/core/tests/
```

**Step 2: Verify**

Run: `ls plugins/core/tests/`
Expected: __init__.py, fixtures/, test_*.py files

**Step 3: Commit**

```bash
git add plugins/core/tests/
git commit -m "feat(core): migrate commit tests"
```

---

## Phase 4: Merge Shell Plugin into Core

### Task 4.1: Copy shell skills to core

**Files:**
- Copy: `plugins/shell/skills/*` → `plugins/core/skills/`

**Step 1: Copy skill directories**

```bash
cp -r plugins/shell/skills/* plugins/core/skills/
```

**Step 2: Verify**

Run: `ls plugins/core/skills/ | grep -E "man|google-shell"`
Expected: google-shell-style, man

**Step 3: Commit**

```bash
git add plugins/core/skills/
git commit -m "feat(core): migrate shell skills"
```

---

### Task 4.2: Copy shell agents to core

**Files:**
- Copy: `plugins/shell/agents/*` → `plugins/core/agents/`

**Step 1: Copy agent files**

```bash
cp plugins/shell/agents/*.md plugins/core/agents/
```

**Step 2: Verify**

Run: `ls plugins/core/agents/shell-expert.md`
Expected: File exists

**Step 3: Commit**

```bash
git add plugins/core/agents/
git commit -m "feat(core): migrate shell agents"
```

---

### Task 4.3: Copy shell commands to core

**Files:**
- Copy: `plugins/shell/commands/*` → `plugins/core/commands/`

**Step 1: Copy command files**

```bash
cp plugins/shell/commands/*.md plugins/core/commands/
```

**Step 2: Verify**

Run: `ls plugins/core/commands/refactor.md`
Expected: File exists

**Step 3: Commit**

```bash
git add plugins/core/commands/
git commit -m "feat(core): migrate shell commands"
```

---

### Task 4.4: Merge shell hooks into core hooks.json

**Files:**
- Modify: `plugins/core/hooks/hooks.json`
- Copy: `plugins/shell/hooks/shell-validate.sh` → `plugins/core/hooks/`

**Step 1: Copy shell hook script**

```bash
cp plugins/shell/hooks/shell-validate.sh plugins/core/hooks/
```

**Step 2: Add shell PreToolUse hook to core hooks.json**

Add this entry to the PreToolUse array:

```json
{
  "matcher": "Write|Edit",
  "hooks": [
    {
      "type": "command",
      "command": "${CLAUDE_PLUGIN_ROOT}/hooks/shell-validate.sh",
      "timeout": 10
    }
  ]
}
```

**Step 3: Add shell PreCompact hook to core hooks.json**

Add new PreCompact section:

```json
"PreCompact": [
  {
    "matcher": "*",
    "hooks": [
      {
        "type": "prompt",
        "prompt": "Before compacting, preserve key shell plugin context: current script path being refactored and any pending style fixes. Include these in the compaction summary.",
        "timeout": 10
      }
    ]
  }
]
```

**Step 4: Verify JSON is valid**

Run: `jq . plugins/core/hooks/hooks.json`
Expected: Valid JSON output

**Step 5: Commit**

```bash
git add plugins/core/hooks/
git commit -m "feat(core): merge shell hooks into core"
```

---

## Phase 5: Merge Debug Plugin into Core

### Task 5.1: Copy debug agents to core

**Files:**
- Copy: `plugins/debug/agents/*` → `plugins/core/agents/`

**Step 1: Copy agent files**

```bash
cp plugins/debug/agents/*.md plugins/core/agents/
```

**Step 2: Verify**

Run: `ls plugins/core/agents/ | grep -E "devops|error"`
Expected: devops-troubleshooter.md, error-detective.md

**Step 3: Commit**

```bash
git add plugins/core/agents/
git commit -m "feat(core): migrate debug agents"
```

---

### Task 5.2: Copy debug commands to core

**Files:**
- Copy: `plugins/debug/commands/*` → `plugins/core/commands/`

**Step 1: Copy command files**

```bash
cp plugins/debug/commands/*.md plugins/core/commands/
```

**Step 2: Verify**

Run: `ls plugins/core/commands/trace.md`
Expected: File exists

**Step 3: Commit**

```bash
git add plugins/core/commands/
git commit -m "feat(core): migrate debug commands"
```

---

### Task 5.3: Copy debug references to core

**Files:**
- Copy: `plugins/debug/references/*` → `plugins/core/references/`

**Step 1: Copy reference files**

```bash
cp plugins/debug/references/*.md plugins/core/references/
```

**Step 2: Verify**

Run: `ls plugins/core/references/`
Expected: distributed-tracing.md, ide-debugging.md, logging-framework.md, performance-profiling.md, production-debugging.md

**Step 3: Commit**

```bash
git add plugins/core/references/
git commit -m "feat(core): migrate debug references"
```

---

## Phase 6: Update Cross-References

### Task 6.1: Update super: references to core:

**Files:**
- Modify: All files in `plugins/core/` containing `super:`

**Step 1: Find all super: references in core**

```bash
grep -r "super:" plugins/core/ --include="*.md" -l
```

**Step 2: Replace super: with core: in all core files**

```bash
find plugins/core -name "*.md" -exec sed -i '' 's/super:/core:/g' {} \;
```

**Step 3: Verify replacements**

Run: `grep -r "super:" plugins/core/ --include="*.md" | wc -l`
Expected: 0 (or only legitimate references to external super concepts)

**Step 4: Commit**

```bash
git add plugins/core/
git commit -m "refactor(core): update super: references to core:"
```

---

### Task 6.2: Update commit: references to core:

**Files:**
- Modify: All files in `plugins/core/` containing `commit:`

**Step 1: Replace commit: with core: in core files**

```bash
find plugins/core -name "*.md" -exec sed -i '' 's/commit:/core:/g' {} \;
```

**Step 2: Verify**

Run: `grep -r "commit:" plugins/core/ --include="*.md" | grep -v "git commit" | wc -l`
Expected: 0

**Step 3: Commit**

```bash
git add plugins/core/
git commit -m "refactor(core): update commit: references to core:"
```

---

### Task 6.3: Update shell: references to core:

**Files:**
- Modify: All files in `plugins/core/` containing `shell:`

**Step 1: Replace shell: with core: in core files**

```bash
find plugins/core -name "*.md" -exec sed -i '' 's/shell:/core:/g' {} \;
```

**Step 2: Verify**

Run: `grep -r "shell:" plugins/core/ --include="*.md" | wc -l`
Expected: 0

**Step 3: Commit**

```bash
git add plugins/core/
git commit -m "refactor(core): update shell: references to core:"
```

---

### Task 6.4: Update debug: references to core:

**Files:**
- Modify: All files in `plugins/core/` containing `debug:`

**Step 1: Replace debug: with core: in core files**

```bash
find plugins/core -name "*.md" -exec sed -i '' 's/debug:/core:/g' {} \;
```

**Step 2: Verify**

Run: `grep -r "debug:" plugins/core/ --include="*.md" | wc -l`
Expected: 0 (excluding legitimate "debug" words)

**Step 3: Commit**

```bash
git add plugins/core/
git commit -m "refactor(core): update debug: references to core:"
```

---

### Task 6.5: Update references in dev plugin

**Files:**
- Modify: All files in `plugins/dev/` containing `super:`

**Step 1: Replace super: with core: in dev plugin**

```bash
find plugins/dev -name "*.md" -exec sed -i '' 's/super:/core:/g' {} \;
```

**Step 2: Verify**

Run: `grep -r "super:" plugins/dev/ --include="*.md" | wc -l`
Expected: 0

**Step 3: Commit**

```bash
git add plugins/dev/
git commit -m "refactor(dev): update super: references to core:"
```

---

### Task 6.6: Update references in doc plugin

**Files:**
- Modify: All files in `plugins/doc/` containing references to merged plugins

**Step 1: Replace any super: references in doc plugin**

```bash
find plugins/doc -name "*.md" -exec sed -i '' 's/super:/core:/g' {} \;
```

**Step 2: Commit if changes made**

```bash
git add plugins/doc/ 2>/dev/null && git commit -m "refactor(doc): update references to core:" || echo "No doc changes"
```

---

### Task 6.7: Update references in analyze plugin

**Files:**
- Modify: All files in `plugins/analyze/` containing `super:`

**Step 1: Replace super: with core: in analyze plugin**

```bash
find plugins/analyze -name "*.md" -exec sed -i '' 's/super:/core:/g' {} \;
```

**Step 2: Commit**

```bash
git add plugins/analyze/
git commit -m "refactor(analyze): update super: references to core:"
```

---

## Phase 7: Update Hook Script Paths

### Task 7.1: Update session-start.sh skill path

**Files:**
- Modify: `plugins/core/hooks/session-start.sh`

**Step 1: Update the SKILL_DIR path**

The script references `using-superpowers` skill. Update any hardcoded paths:

```bash
# Change from:
SKILL_DIR="${CLAUDE_PLUGIN_ROOT}/skills/using-superpowers"
# No change needed if using CLAUDE_PLUGIN_ROOT (it will resolve correctly)
```

**Step 2: Verify script works**

Run: `bash -n plugins/core/hooks/session-start.sh`
Expected: No syntax errors

**Step 3: Commit if changed**

```bash
git add plugins/core/hooks/
git commit -m "fix(core): update hook script paths" || echo "No path changes needed"
```

---

## Phase 8: Delete Old Plugins

### Task 8.1: Remove super plugin directory

**Step 1: Delete super plugin**

```bash
rm -rf plugins/super
```

**Step 2: Commit**

```bash
git add -A plugins/super
git commit -m "refactor: remove super plugin (merged into core)"
```

---

### Task 8.2: Remove commit plugin directory

**Step 1: Delete commit plugin**

```bash
rm -rf plugins/commit
```

**Step 2: Commit**

```bash
git add -A plugins/commit
git commit -m "refactor: remove commit plugin (merged into core)"
```

---

### Task 8.3: Remove shell plugin directory

**Step 1: Delete shell plugin**

```bash
rm -rf plugins/shell
```

**Step 2: Commit**

```bash
git add -A plugins/shell
git commit -m "refactor: remove shell plugin (merged into core)"
```

---

### Task 8.4: Remove debug plugin directory

**Step 1: Delete debug plugin**

```bash
rm -rf plugins/debug
```

**Step 2: Commit**

```bash
git add -A plugins/debug
git commit -m "refactor: remove debug plugin (merged into core)"
```

---

## Phase 9: Update Documentation

### Task 9.1: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update plugin table**

Replace the plugins table with:

```markdown
### Plugins

| Plugin | Purpose |
|--------|---------|
| **core** | Core workflows: TDD, verification, debugging, git commits, shell scripting |
| **dev** | Python: uv, async, FastAPI, Django, testing patterns |
| **doc** | Documentation: API docs, tutorials, Amazon-style memos, Mermaid |
| **analyze** | (Optional) Marketplace plugin analyzer |
| **blackbox** | (Optional) Flight recorder hooks for telemetry |
```

**Step 2: Update any super/commit/shell/debug references to core**

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for plugin consolidation"
```

---

### Task 9.2: Update marketplace.json

**Files:**
- Modify: `.claude-plugin/marketplace.json`

**Step 1: Update plugin list to reflect new structure**

Remove entries for super, commit, shell, debug. Add entry for core.

**Step 2: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "docs: update marketplace.json for plugin consolidation"
```

---

## Phase 10: Validation

### Task 10.1: Run plugin validation

**Step 1: Run validation script**

```bash
./scripts/validate-plugins.sh
```

**Step 2: Expected output**

All plugins should validate successfully:
- core: PASS
- dev: PASS
- doc: PASS
- analyze: PASS (if kept)
- blackbox: PASS (if kept)

---

### Task 10.2: Test core plugin functionality

**Step 1: Verify skill loading**

```bash
ls plugins/core/skills/*/SKILL.md | wc -l
```
Expected: 23 (20 from super + 1 from commit + 2 from shell)

**Step 2: Verify hook JSON is valid**

```bash
jq . plugins/core/hooks/hooks.json > /dev/null && echo "Valid JSON"
```

**Step 3: Verify no broken cross-references**

```bash
grep -r "super:\|commit:\|shell:\|debug:" plugins/core plugins/dev plugins/doc --include="*.md" | grep -v "git commit" | head -20
```
Expected: No results (or only false positives like "debug" in prose)

---

### Task 10.3: Final commit

**Step 1: Create summary commit**

```bash
git add -A
git commit -m "refactor: complete plugin consolidation (8 → 3 plugins)

Merged into core:
- super (20 skills, 3 agents, 5 commands, hooks)
- commit (1 skill, 1 agent, 3 commands, hooks)
- shell (2 skills, 1 agent, 1 command, hooks)
- debug (2 agents, 1 command, references)

Kept as standalone:
- dev (Python-specific workflows)
- doc (Documentation generation)

Optional (unchanged):
- analyze (Meta-plugin for quality analysis)
- blackbox (Telemetry/flight recorder)"
```

---

## Post-Migration

After completing all tasks:

1. **Test in fresh session**: Start new Claude Code session to verify hooks load correctly
2. **Update any external references**: If you have other repos referencing `super:` skills, update them
3. **Consider aliases**: For backward compatibility, you could create symbolic links or aliases

---

## Rollback Plan

If issues arise:

```bash
git checkout master -- plugins/
git branch -D refactor/plugin-consolidation
```

This restores the original 8-plugin structure.
