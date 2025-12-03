---
description: Generate OpenAPI specs, interactive API docs, and SDK templates
allowed-tools: Task, Read, Glob, Grep, Write, Edit, AskUserQuestion
---

# API Specification Generation

Generate comprehensive API documentation using the specialized api-documenter agent.

## What This Command Does

Dispatches the `api-documenter` agent to create:
- OpenAPI 3.0/3.1 specifications
- Interactive API documentation (Swagger UI, Redoc)
- SDK templates and code samples
- Authentication flow documentation

## Before Dispatching

Gather the following from the user:
1. **API Type**: REST, GraphQL, WebSocket, or AsyncAPI
2. **Target Audience**: Frontend devs, backend devs, third-party integrators
3. **Scope**: Single endpoint, module, or entire API
4. **Output Format**: OpenAPI spec, interactive docs, SDK stubs, or all

## Dispatch the Agent

Use the Task tool to dispatch the api-documenter agent:

```
Task(
  subagent_type="doc:api-documenter",
  prompt="[Include gathered requirements and any relevant file paths]"
)
```

## When NOT to Use

- For parameter lookup tables only → use `/doc:reference`
- For architecture documentation → use `/doc:architecture`
- For step-by-step tutorials → use `/doc:tutorial`
