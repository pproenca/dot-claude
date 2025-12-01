---
name: writing-plans
description: Use when design is complete and you need detailed implementation tasks for engineers with zero codebase context - creates comprehensive implementation plans with exact file paths, complete code examples, and verification steps assuming engineer has minimal domain knowledge
allowed-tools: Read, Write, AskUserQuestion, Glob, Grep
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

## Python Project Detection

Before writing a plan, detect if this is a Python project and what framework it uses:

**Detection signals:**
- `pyproject.toml` or `setup.py` → Python project
- `fastapi` in dependencies → FastAPI project
- `django` in dependencies → Django project
- `asyncio` imports or `async def` → Async code
- `.python-version` or `uv.lock` → Uses uv package manager

**When Python detected:**
1. Use Skill tool to load `python:python-testing-patterns`
2. Use Skill tool to load `python:uv-package-manager`
3. Use patterns from loaded skills in plan tasks
4. Use `uv run` prefix for all Python commands

**When async code detected:**
- Use Skill tool to load `python:async-python-patterns`

**When FastAPI/Django detected:**
- Dispatch `python:python-expert` agent for framework-specific patterns

## Optional: Track Plan Writing Phases

For complex plans (5+ tasks), use TodoWrite to track progress:
- Research existing architecture
- Define high-level approach
- Break down into tasks
- Add code examples
- Generate diagrams (if applicable)
- Execution handoff

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use super:executing-plans to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

**Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
```

## Remember
- Exact file paths always
- Complete code in plan (not "add validation")
- Exact commands with expected output
- Reference relevant skills with @ syntax
- DRY, YAGNI, TDD, frequent commits

## Python-Specific Patterns

When Python detected, load patterns from the python plugin instead of duplicating them here.

**Step 1: Load relevant skill**

```
Use Skill tool: python:python-testing-patterns
```

**Step 2: Copy patterns into plan tasks**

- Fixtures from skill → conftest.py setup task
- Parameterized tests from skill → test task examples
- Mocking patterns from skill → integration test examples

**For async code detected:**

```
Use Skill tool: python:async-python-patterns
```

**For FastAPI/Django detected:**

```
Task tool (python:python-expert):
  prompt: "Provide [framework] test patterns for [feature]"
```

## Diagram Generation Phase

After completing the plan content, offer diagram generation.

### Step 1: Ask About Diagrams

Use AskUserQuestion:

```
Question: "Would you like me to generate diagrams for this plan?"
Header: "Diagrams"
multiSelect: true
Options:
- Task Dependencies: Flowchart showing task order and parallelization
- Architecture: Component diagram showing system structure
- No diagrams: Skip diagram generation
```

### Step 2: Generate Diagrams (if requested)

If user selects diagram types, dispatch diagram-generator subagent:

```
Task tool (general-purpose):
  description: "Generate Mermaid diagrams for plan"
  prompt: Use template at writing-plans/diagram-prompt-template.md

  DIAGRAM_TYPES: [user's selection]
  PLAN_CONTENT: [full plan text]
```

### Step 3: Insert Diagrams

Add `## Diagrams` section to the plan document after the header block, before first task:

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL...

**Goal:** ...
**Architecture:** ...
**Tech Stack:** ...

---

## Diagrams

[Insert agent output here]

---

### Task 1: ...
```

### When to Skip Diagrams

Skip the diagram question when:
- Plan has < 4 tasks with linear sequence
- Single-file refactoring
- No multi-component architecture

## Execution Handoff

After saving the plan (with or without diagrams), offer execution choice:

**"Plan complete and saved to `docs/plans/<filename>.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?"**

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use super:subagent-driven-development
- Stay in this session
- Fresh subagent per task + code review

**If Parallel Session chosen:**
- Guide them to open new session in worktree
- **REQUIRED SUB-SKILL:** Use super:executing-plans

## Workflow Integration

### Python Development Skills

When writing Python plans, integrate these `python` plugin skills:

| Skill | When to Reference | What It Provides |
|-------|-------------------|------------------|
| `python:python-testing-patterns` | All Python test code | Fixtures, mocking, parameterized tests, markers |
| `python:uv-package-manager` | Python commands, dependencies | `uv run`, `uv add`, `uv sync` patterns |
| `python:async-python-patterns` | Async code detected | asyncio, gather(), error handling, timeouts |
| `python:python-packaging` | Creating packages/CLIs | pyproject.toml, entry points, publishing |
| `python:python-performance-optimization` | Performance-critical code | Profiling, caching, optimization patterns |

### Agent Dispatch

For complex Python plans, dispatch specialized agents:

```
Task tool (python:python-expert):
  description: "Get FastAPI/Django patterns for [feature]"
  prompt: "Analyze [feature requirements] and provide:
    1. Framework-specific implementation pattern
    2. Test fixtures and patterns
    3. Common pitfalls to avoid"
```

### Plan Header with Python Context

For Python projects, enhance the header:

```markdown
# [Feature Name] Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use super:executing-plans to implement this plan task-by-task.
> **Python Skills:** Reference python:python-testing-patterns for tests, python:uv-package-manager for commands.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** Python 3.12+, pytest, [framework if applicable]

**Commands:** All Python commands use `uv run` prefix

---
```
