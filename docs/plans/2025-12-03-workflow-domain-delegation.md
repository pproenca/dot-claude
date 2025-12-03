# Workflow-to-Domain Agent Delegation Design

> **For Claude:** REQUIRED SUB-SKILL: Use workflow:executing-plans to implement this plan task-by-task.

**Goal:** Enable workflow commands to delegate code writing tasks to specialized domain agents based on file types.

**Architecture:** Plan-time detection with explicit annotation. `writing-plans` detects file extensions and annotates each task with the appropriate agent. `executing-plans` and `subagent-dev` parse annotations and dispatch to domain specialists.

**Tech Stack:** Claude Code plugins, SKILL.md files, agent dispatch

---

## Overview

### The Problem

Currently, `executing-plans` and `subagent-dev` dispatch all code-writing tasks to `general-purpose` agents. This misses domain expertise from specialized agents like `python:python-expert` and `shell:shell-expert`.

### The Solution

Add an `**Agent:**` annotation to each task in the plan document. The annotation specifies which agent should handle:

- **Code writing** (implementing the task)
- **Code review** (reviewing the implementation)
- **Testing guidance** (framework-specific test patterns)

### Architecture Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  writing-plans  │───▶│  Plan Document   │───▶│ executing-plans │
│                 │    │  with **Agent:** │    │  or subagent-dev│
│  - Detect files │    │  annotations     │    │                 │
│  - Map to agent │    │                  │    │  - Parse agent  │
│  - Split tasks  │    │                  │    │  - Dispatch     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                       │
                              ┌─────────────────────────┼───────────────────────┐
                              ▼                         ▼                       ▼
                    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
                    │ python:python-  │     │ shell:shell-    │     │ general-purpose │
                    │ expert          │     │ expert          │     │ (fallback)      │
                    └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Key Principles

1. **Single detection point**: `writing-plans` detects once, annotates plan
2. **Explicit over implicit**: Agent is visible in the plan document
3. **Graceful fallback**: Missing annotation → `general-purpose`
4. **Task splitting**: Multi-file tasks split by domain

---

## File Extension to Agent Mapping

### Mapping Table

| Extension | Domain Agent | Review Agent | Notes |
|-----------|--------------|--------------|-------|
| `.py` | `python:python-expert` | `review:code-reviewer` | Expert handles framework detection internally |
| `.sh` | `shell:shell-expert` | `shell:shell-expert` (REVIEW mode) | Shell expert has built-in review mode |
| `.md` (code docs) | `doc:docs-architect` | `review:code-reviewer` | For technical documentation |
| Other | `general-purpose` | `review:code-reviewer` | Fallback for unknown types |

### Detection Logic

```python
# Pseudocode for file-to-agent mapping
AGENT_MAP = {
    ".py": "python:python-expert",
    ".sh": "shell:shell-expert",
    ".md": "doc:docs-architect",
}
DEFAULT_AGENT = "general-purpose"

def get_agent_for_task(files: list[str]) -> str:
    """Determine agent from primary file extension."""
    for file in files:
        ext = get_extension(file)
        if ext in AGENT_MAP:
            return AGENT_MAP[ext]
    return DEFAULT_AGENT
```

### Multi-File Task Splitting

When a task involves multiple file types, `writing-plans` splits it:

**Original task:** "Add user validation with deployment script"

- Files: `src/validators/user.py`, `deploy/validate.sh`

**Split into:**

1. **Task 3a:** Python implementation (`**Agent:** python:python-expert`)
2. **Task 3b:** Shell deployment script (`**Agent:** shell:shell-expert`)

### Extension Points

New domains can be added by:

1. Creating `plugins/domain/<name>/agents/<name>-expert.md`
2. Adding extension mapping to `AGENT_MAP` in `writing-plans`

---

## Changes to `writing-plans` Skill

### New Section: Domain Agent Detection

Add after "Python Project Detection" section:

```markdown
## Domain Agent Detection

Before writing each task, detect the appropriate agent based on file types.

### File Extension Mapping

| Extension | Agent | Review Mode |
|-----------|-------|-------------|
| `.py` | `python:python-expert` | `review:code-reviewer` |
| `.sh` | `shell:shell-expert` | `shell:shell-expert` (REVIEW) |
| `.md` | `doc:docs-architect` | `review:code-reviewer` |
| Other | `general-purpose` | `review:code-reviewer` |

### Multi-File Task Splitting

When a task involves files with different extensions:
1. Group files by extension
2. Create subtasks for each group (3a, 3b, 3c...)
3. Each subtask gets its own `**Agent:**` annotation
4. Add dependency note if subtasks must be sequential
```

### Updated Task Structure

```markdown
### Task N: [Component Name]

**Complexity:** [TRIVIAL | SIMPLE | MODERATE | COMPLEX]
**Agent:** [domain:agent-name | general-purpose]

**Files:**
- Create: `exact/path/to/file.py`
...
```

### Implementation Notes

1. **Agent field is REQUIRED** for all new plans
2. **Position:** After `**Complexity:**`, before `**Files:**`
3. **Format:** `plugin-name:agent-name` (e.g., `python:python-expert`)
4. **Fallback:** If detection fails, use `general-purpose`

---

## Changes to `executing-plans` Skill

### Updated Step 2: Execute Batch

Read `**Agent:**` annotation before dispatching:

1. Read task from plan
2. Extract `**Agent:**` value (e.g., `python:python-expert`)
3. If missing, default to `general-purpose`

### Dispatch by Complexity + Agent

**TRIVIAL Tasks:** Execute directly (no agent dispatch - unchanged)

**SIMPLE Tasks:**

```
Task tool ([agent from plan]):
  model: haiku
  description: "Implement Task N: [task name]"
  prompt: |
    You are implementing Task N from [plan-file]. This is a SIMPLE task.
    [... rest unchanged ...]
```

**MODERATE/COMPLEX Tasks:**

```
Task tool ([agent from plan]):
  model: sonnet
  description: "Implement Task N: [task name]"
  prompt: |
    You are implementing Task N from [plan-file].
    [... rest unchanged ...]
```

### Key Changes

1. Replace hardcoded `general-purpose` with parsed agent
2. Add parsing helper to extract `**Agent:** value` from task text
3. Maintain fallback: If no agent annotation, use `general-purpose`

---

## Changes to `subagent-dev` Skill

Same pattern as `executing-plans`:

1. Parse `**Agent:**` field at start of Step 2
2. Replace `general-purpose` with parsed agent in dispatch
3. TRIVIAL tasks still execute directly by parent (no change)

Both skills use the same parsing logic for consistency.

---

## Backward Compatibility

**Existing plans without `**Agent:**` annotation:**

- Both skills fall back to `general-purpose`
- No breaking changes for existing plan documents
- Old plans continue to work exactly as before

**Gradual adoption:**

- New plans get agent annotations automatically
- Old plans can be updated manually if desired
- No migration required

---

## Testing Strategy

**Unit tests for agent detection:**

```python
def test_get_agent_for_py_files():
    assert get_agent_for_files(["src/foo.py"]) == "python:python-expert"

def test_get_agent_for_sh_files():
    assert get_agent_for_files(["deploy.sh"]) == "shell:shell-expert"

def test_get_agent_fallback():
    assert get_agent_for_files(["config.yaml"]) == "general-purpose"

def test_task_splitting_multi_extension():
    files = ["src/main.py", "deploy.sh"]
    tasks = split_by_domain(files)
    assert len(tasks) == 2
    assert tasks[0]["agent"] == "python:python-expert"
    assert tasks[1]["agent"] == "shell:shell-expert"
```

**Integration testing:**

1. Create a plan with mixed file types
2. Verify tasks are split correctly
3. Execute plan and verify correct agents are dispatched

---

## Implementation Tasks

### Task 1: Update `writing-plans` skill

**Complexity:** MODERATE
**Agent:** general-purpose

**Files:**

- Modify: `plugins/methodology/workflow/skills/writing-plans/SKILL.md`

**Changes:**

1. Add "Domain Agent Detection" section after "Python Project Detection"
2. Add file extension mapping table
3. Update "Task Structure" section to include `**Agent:**` field
4. Add multi-file task splitting guidance

### Task 2: Update `executing-plans` skill

**Complexity:** MODERATE
**Agent:** general-purpose

**Files:**

- Modify: `plugins/methodology/workflow/skills/executing-plans/SKILL.md`

**Changes:**

1. Add agent parsing logic to Step 2
2. Update dispatch examples to use `[agent from plan]`
3. Document fallback behavior

### Task 3: Update `subagent-dev` skill

**Complexity:** MODERATE
**Agent:** general-purpose

**Files:**

- Modify: `plugins/methodology/workflow/skills/subagent-dev/SKILL.md`

**Changes:**

1. Add agent parsing logic to Step 2
2. Update dispatch examples to use `[agent from plan]`
3. Ensure consistency with `executing-plans`
