---
description: Create exhaustive parameter and configuration reference documentation
allowed-tools: Task, Read, Glob, Grep, Write, Edit, AskUserQuestion
---

# Reference Documentation

Generate comprehensive lookup-optimized documentation using the specialized reference-builder agent.

## What This Command Does

Dispatches the `reference-builder` agent to create:
- Exhaustive parameter tables
- Configuration matrices with defaults and constraints
- Error code references
- CLI flag documentation
- Environment variable references

## Before Dispatching

Gather the following from the user:
1. **Scope**: Single endpoint, module, entire API, or CLI
2. **Format**: Tables, structured lists, or searchable index
3. **Categories**: How to organize parameters (by function, by type, alphabetical)
4. **Include**: Defaults, types, constraints, examples

## Dispatch the Agent

Use the Task tool to dispatch the reference-builder agent:

```
Task(
  subagent_type="doc:reference-builder",
  prompt="[Include gathered requirements and any relevant file paths]"
)
```

## When NOT to Use

- For narrative architecture docs → use `/doc:architecture`
- For step-by-step tutorials → use `/doc:tutorial`
- For OpenAPI specs → use `/doc:api-spec`
- For conceptual explanations → use `/doc:explain`
