# Mermaid Syntax Reference

Reference guide for Mermaid diagram syntax. Load when generating diagrams.

## Diagram Type Selection Guide

| Visualization Need | Recommended Type | Alternative |
|--------------------|------------------|-------------|
| Process/workflow steps | `flowchart` | `stateDiagram-v2` |
| API call sequences | `sequenceDiagram` | `flowchart` |
| Database schema | `erDiagram` | `classDiagram` |
| Class/object structure | `classDiagram` | `erDiagram` |
| State machine/lifecycle | `stateDiagram-v2` | `flowchart` |
| Project timeline | `gantt` | `timeline` |
| User journey/experience | `journey` | `flowchart` |
| Git branching | `gitGraph` | N/A |
| Distribution/proportion | `pie` | `quadrantChart` |
| Comparison matrix | `quadrantChart` | N/A |
| Historical events | `timeline` | `gantt` |
| System architecture | `flowchart` with subgraphs | `C4Context` |

---

## Diagram Type Examples

### flowchart (graph)
Most versatile. Use for processes, architectures, decision trees, data flows.
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
    B -->|No| D[Other Action]
```

### sequenceDiagram
Use for time-ordered interactions between actors/systems.
```mermaid
sequenceDiagram
    Client->>Server: Request
    Server-->>Client: Response
```

### erDiagram
Use for database relationships with cardinality.
```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
```

### classDiagram
Use for OOP class structures with methods and inheritance.
```mermaid
classDiagram
    Animal <|-- Dog
    Animal : +name
    Animal : +makeSound()
```

### stateDiagram-v2
Use for finite state machines with transitions.
```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Active : approve
    Active --> [*] : complete
```

### gantt
Use for project schedules with durations and dependencies.
```mermaid
gantt
    title Project Plan
    section Phase 1
    Task 1: a1, 2024-01-01, 7d
    Task 2: after a1, 5d
```

---

## Syntax Reference

### Node Shapes (flowchart)
```
[Rectangle] - Default process
(Rounded) - Terminal/rounded
([Stadium]) - Pill shape
[[Subroutine]] - Subprocess
[(Database)] - Cylinder
((Circle)) - Circle
{Diamond} - Decision
{{Hexagon}} - Preparation
```

### Arrow Types
```
--> Solid arrow (strong dependency)
-.-> Dashed arrow (weak/optional)
==> Thick arrow (important path)
--o Open circle end
--x Cross end
```

### Styling
```mermaid
graph TD
    A[Node]:::highlight --> B[Other]
    classDef highlight fill:#f9f,stroke:#333,stroke-width:2px
```

### Subgraphs
```mermaid
graph TD
    subgraph Backend
        API[API Server]
        DB[(Database)]
    end
    subgraph Frontend
        UI[Web App]
    end
    UI --> API
    API --> DB
```

---

## Common Syntax Errors to Avoid

| Error | Wrong | Correct |
|-------|-------|---------|
| Case sensitivity | `graph lr` | `graph LR` |
| Spaces in node IDs | `Task 1[Label]` | `T1[Task 1 Label]` |
| Missing brackets | `A --> B[Label` | `A --> B[Label]` |
| Special chars in IDs | `node-1[Label]` | `node1[Label]` |
| Unclosed subgraph | `subgraph X` | `subgraph X ... end` |
| Quote issues | `A["Label's"]` | `A["Label''s"]` |

---

## Edge Cases

### Complex Diagrams (>15 nodes)
- Split into multiple focused diagrams
- Use subgraphs to group related nodes
- Provide overview + detail diagrams

### Bidirectional Relationships
```mermaid
graph LR
    A <--> B
    %% or
    C --> D
    D --> C
```

### Self-Referencing
```mermaid
graph TD
    A[Process] --> A
```

### External Systems
Use dashed styling and external subgraph:
```mermaid
graph TD
    subgraph Internal
        A[Our Service]
    end
    subgraph External
        B[Third Party]:::ext
    end
    A -.-> B
    classDef ext fill:#ddd,stroke:#999,stroke-dasharray: 5 5
```

---

## Examples

### Example 1: Simple Flowchart

**Input:** "Create a flowchart for user login"

```mermaid
graph TD
    A[User Enters Credentials] --> B{Valid?}
    B -->|Yes| C[Dashboard]
    B -->|No| D[Show Error]
    D --> A
```

### Example 2: Database ERD

**Input:** "ERD for Users, Posts, Comments"

```mermaid
erDiagram
    USER ||--o{ POST : writes
    USER ||--o{ COMMENT : makes
    POST ||--o{ COMMENT : has

    USER {
        int id PK
        string username
        string email
    }
    POST {
        int id PK
        int user_id FK
        string title
        text content
    }
    COMMENT {
        int id PK
        int user_id FK
        int post_id FK
        text content
    }
```

### Example 3: Sequence Diagram

**Input:** "OAuth2 authorization code flow"

```mermaid
sequenceDiagram
    participant U as User
    participant A as App
    participant AS as Auth Server

    U->>A: Click Login
    A->>AS: Redirect to /authorize
    AS->>U: Show Login Form
    U->>AS: Enter Credentials
    AS->>A: Redirect with Auth Code
    A->>AS: Exchange Code for Token
    AS->>A: Access Token + Refresh Token
    A->>U: Logged In
```
