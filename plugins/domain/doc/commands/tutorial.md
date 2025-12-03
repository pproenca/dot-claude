---
description: Create step-by-step tutorials and educational content
allowed-tools: Task, Read, Glob, Grep, Write, Edit, AskUserQuestion
---

# Tutorial Generation

Generate pedagogically-structured learning content using the specialized tutorial-engineer agent.

## What This Command Does

Dispatches the `tutorial-engineer` agent to create:

- Getting started guides
- Step-by-step tutorials with exercises
- Workshop content with checkpoints
- Deep dive guides for advanced topics
- Cookbook-style solution guides

## Before Dispatching

Gather the following from the user:

1. **Learning Outcome**: What will readers be able to DO after this tutorial?
2. **Format**: Quick start, deep dive, workshop, or cookbook
3. **Audience Level**: Beginner, intermediate, or advanced
4. **Prerequisites**: What knowledge is assumed

## Dispatch the Agent

Use the Task tool to dispatch the tutorial-engineer agent:

```text
Task(
  subagent_type="doc:tutorial-engineer",
  prompt="[Include gathered requirements and any relevant file paths]"
)
```

## When NOT to Use

- For parameter lookup tables → use `/doc:reference`
- For architecture documentation → use `/doc:architecture`
- For OpenAPI specs → use `/doc:api-spec`
- For code explanation → use `/doc:explain`
