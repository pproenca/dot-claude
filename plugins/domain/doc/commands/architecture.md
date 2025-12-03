---
description: Create comprehensive system architecture documentation
allowed-tools: Task, Read, Glob, Grep, Write, Edit, AskUserQuestion
---

# Architecture Documentation

Generate long-form technical documentation using the specialized docs-architect agent.

## What This Command Does

Dispatches the `docs-architect` agent to create:
- System architecture documentation (10-100+ pages)
- Design decision rationale ("why" documentation)
- Component relationship documentation
- Onboarding guides for new engineers

## Before Dispatching

Gather the following from the user:
1. **Scope**: Single system, microservice, or entire platform
2. **Audience**: New engineers, architects, or external stakeholders
3. **Focus Areas**: What aspects need most attention (data flow, security, scalability)
4. **Existing Docs**: Any current documentation to build upon

## Dispatch the Agent

Use the Task tool to dispatch the docs-architect agent:

```
Task(
  subagent_type="doc:docs-architect",
  prompt="[Include gathered requirements and any relevant file paths]"
)
```

## When NOT to Use

- For exhaustive parameter tables → use `/doc:reference`
- For step-by-step tutorials → use `/doc:tutorial`
- For OpenAPI specs → use `/doc:api-spec`
- For diagrams only → use `doc:mermaid-expert` agent
