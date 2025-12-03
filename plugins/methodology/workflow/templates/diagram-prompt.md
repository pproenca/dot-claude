# Diagram Generation Template

Use this template when dispatching diagram generation for implementation plans.

**Key insight:** Diagrams help Claude maintain context during complex plan execution. They're execution aids, not just visual documentation.

## Dispatch Format

### Auto-Detect Mode (Recommended)

Let the agent decide IF and WHAT diagrams would help:

```
Task tool with subagent_type="doc:diagram-generator":
  description: "Auto-detect useful diagrams for plan"
  prompt: |
    MODE: auto-detect

    ## Plan Content
    {PLAN_CONTENT}

    Analyze this plan and decide:
    1. Would any diagrams help Claude execute this plan better?
    2. If yes, which type(s) would be most useful?
    3. Generate only what adds value - skip if plan is straightforward.
```

### Specific Mode

Request specific diagram types:

```
Task tool with subagent_type="doc:diagram-generator":
  description: "Generate [TYPE] diagram for plan"
  prompt: |
    MODE: specific
    DIAGRAM_TYPES: {USER_SELECTION}

    ## Plan Content
    {PLAN_CONTENT}

    Generate the requested diagram type(s).
```

## Available Diagram Types

The diagram-generator agent can create these types:

### Task Dependencies (graph LR/TD)

Shows task execution order and parallelization opportunities.

```mermaid
graph LR
    T1[Task 1] --> T2[Task 2]
    T1 --> T3[Task 3]
    T2 --> T4[Task 4]
    T3 --> T4
```

### Architecture (graph TB + subgraphs)

Shows system components, data flow, and module relationships.

```mermaid
graph TB
    subgraph Frontend
        UI[User Interface]
    end
    subgraph Backend
        API[API Server]
        DB[(Database)]
    end
    UI --> API
    API --> DB
```

### Sequence (sequenceDiagram)

Shows API flows, service interactions, and request/response patterns.

```mermaid
sequenceDiagram
    Client->>+Server: Request
    Server->>+Database: Query
    Database-->>-Server: Results
    Server-->>-Client: Response
```

### State (stateDiagram-v2)

Shows workflow states, object lifecycle, and state transitions.

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review
    Review --> Approved
    Review --> Draft: Needs changes
    Approved --> [*]
```

### Entity-Relationship (erDiagram)

Shows database schema and entity relationships.

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    PRODUCT ||--o{ LINE-ITEM : "ordered in"
```

### Class (classDiagram)

Shows OOP design, interfaces, and inheritance.

```mermaid
classDiagram
    class Animal {
        +String name
        +makeSound()
    }
    class Dog {
        +fetch()
    }
    Animal <|-- Dog
```

### Flowchart (flowchart TD)

Shows decision logic, algorithms, and process flows.

```mermaid
flowchart TD
    A[Start] --> B{Condition?}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

### Git Graph (gitGraph)

Shows branch strategy and merge plans.

```mermaid
gitGraph
    commit
    branch feature
    checkout feature
    commit
    commit
    checkout main
    merge feature
```

### Mindmap (mindmap)

Shows feature breakdowns and concept organization.

```mermaid
mindmap
    root((Feature))
        Backend
            API
            Database
        Frontend
            Components
            Styling
```

## Diagram Selection Guidelines

**How diagrams help Claude execute:**

| Diagram Type | Execution Benefit |
|--------------|-------------------|
| **Task Dependencies** | Prevents starting blocked tasks, shows parallelization |
| **Architecture** | Clarifies component boundaries during multi-file changes |
| **Sequence** | Tracks message order, helps debug integration |
| **State** | Prevents invalid state transitions |
| **ER Diagram** | Shows relationships, prevents FK violations |
| **Flowchart** | Ensures all decision paths are covered |

**Auto-detect will skip diagrams when:**

- Plan has < 5 tasks with linear sequence
- Single-file changes (bug fix, refactor)
- No inter-component dependencies
- Configuration-only changes

**Auto-detect will generate diagrams when:**

- 5+ tasks with non-linear dependencies
- Multiple components/services that interact
- State machines with 3+ states
- Database schema with 3+ related entities
- API integrations with request/response cycles

## Output Format

### When generating:

```markdown
### [Diagram Title]

**Purpose:** [How this helps Claude execute the plan]

\`\`\`mermaid
[diagram code]
\`\`\`
```

### When skipping:

```markdown
**Diagrams:** Skipped - [reason, e.g., "linear 4-task plan doesn't benefit from visualization"]
```

## Example

```markdown
### Task Execution Flow

**Purpose:** Shows which tasks can run in parallel (T1 & T2) and what blocks T3

\`\`\`mermaid
graph LR
    T1[Setup Database] --> T3[Create API]
    T2[Setup Auth] --> T3
    T3 --> T4[Add Frontend]
    T4 --> T5[Write Tests]
\`\`\`
```
