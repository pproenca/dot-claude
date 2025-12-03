# Diagram Generation Template

Use this template when dispatching diagram generation for implementation plans.

## Dispatch Format

```
Task tool (doc:diagram-generator):
  description: "Generate diagrams for implementation plan"
  prompt: |
    Generate Mermaid diagrams for the following implementation plan.

    ## Requested Diagram Types
    {DIAGRAM_TYPES}

    ## Plan Content
    {PLAN_CONTENT}

    Generate clean, readable Mermaid code for each requested diagram type.
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

**Use Task Dependencies when:**
- Plan has 4+ tasks
- Some tasks can run in parallel
- Task order matters

**Use Architecture when:**
- Plan involves multiple components
- Data flows between systems
- New modules/services are created

**Use Sequence when:**
- Plan involves API integrations
- Multiple services communicate
- Request/response patterns matter

**Use State when:**
- Objects have lifecycle states
- Workflow has defined transitions
- Status changes are important

**Skip diagrams when:**
- Plan has < 4 tasks with linear sequence
- Single-file refactoring
- No multi-component architecture

## Output Format

Each diagram should include:
1. **Title** - What the diagram shows
2. **Type** - Which Mermaid diagram type
3. **Purpose** - Why this diagram helps
4. **Code** - Clean Mermaid syntax

Example:
```markdown
### Task Execution Flow

**Type:** Task Dependencies (graph LR)
**Purpose:** Shows which tasks can run in parallel and dependencies

```mermaid
graph LR
    T1[Setup Database] --> T3[Create API]
    T2[Setup Auth] --> T3
    T3 --> T4[Add Frontend]
    T4 --> T5[Write Tests]
```
```
