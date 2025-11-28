# Diagram Generator Dispatch Template

Use when dispatching diagram-generator subagent from writing-plans skill.

## Template

```
Generate Mermaid diagrams for this implementation plan.

**Diagram Types Requested:** {DIAGRAM_TYPES}

## Plan Content

{PLAN_CONTENT}

## Instructions

1. Analyze the plan structure and task dependencies
2. Generate the requested diagram type(s)
3. Return markdown ready for insertion into the plan's ## Diagrams section
4. Each diagram should have a title and one-sentence purpose
```

## Placeholders

| Placeholder | Source |
|-------------|--------|
| `{DIAGRAM_TYPES}` | User selection: "Task Dependencies", "Architecture", or both |
| `{PLAN_CONTENT}` | Full plan markdown content |

## Usage

From writing-plans skill, dispatch via Task tool:

```
Task tool (general-purpose):
  description: "Generate Mermaid diagrams for plan"
  prompt: [Fill template above with placeholders replaced]
```
