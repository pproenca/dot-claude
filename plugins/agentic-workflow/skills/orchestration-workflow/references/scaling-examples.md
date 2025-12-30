# Scaling Examples by Complexity

## Trivial Example: Fix Typo in Error Message

**Assessment**: Single file, single string change, < 5 minutes

**Approach**: Direct guidance
- Read the file
- Edit the string
- Done

No orchestration needed.

---

## Small Example: Add Logging to Existing Function

**Assessment**: 1-2 files, clear scope, ~1 hour

**Approach**: 1 subagent + verification
- Create single task packet for implementation
- Spawn task-executor
- Run integration-tester to verify

---

## Medium Example: Add User Authentication Endpoint

**Assessment**: 5-8 files, multiple layers, ~4 hours

**Plan**:
```
Wave 1 (Parallel):
├── Task A: Token generation service (src/auth/token.py)
└── Task B: Session management (src/auth/session.py)

Wave 2:
└── Task C: Auth API endpoint (src/api/auth.py) - depends on A, B

Wave 3:
└── Integration tests
```

**Subagents**: 3 task-executors + 3 verification agents

---

## Large Example: Implement New Payment System

**Assessment**: 15+ files, new module, external integration, ~3 days

**Plan**:
```
Milestone 1: Core Payment Domain
├── Wave 1: Payment entity models
├── Wave 2: Payment repository
└── Wave 3: Payment service layer

Milestone 2: External Integration
├── Wave 4: Stripe SDK wrapper
├── Wave 5: Webhook handlers
└── Wave 6: Error handling

Milestone 3: API Layer
├── Wave 7: Payment endpoints
├── Wave 8: Admin endpoints
└── Wave 9: Full integration tests

Milestone 4: Documentation
└── Wave 10: API docs, README updates
```

**Subagents**: 10+ task-executors, staged milestone reviews

---

## Huge Example: Migrate Monolith to Microservices

**Assessment**: Entire system, multi-week, architectural

**Approach**: Phased delivery with human checkpoints

```
Phase 1: Analysis (Week 1)
- Service boundary identification
- Dependency mapping
- Data ownership analysis
- Human review checkpoint

Phase 2: Foundation (Week 2)
- Shared library extraction
- Service template creation
- CI/CD pipeline setup
- Human review checkpoint

Phase 3: First Service (Week 3)
- Extract User Service
- Integration with monolith
- Testing strategy validation
- Human review checkpoint

Phase 4-N: Remaining Services
- One service per phase
- Continuous human oversight
```

Each phase uses full orchestration workflow internally.

---

## Context Budget by Role

| Role | Token Budget | Includes |
|------|--------------|----------|
| Orchestrator | ~50K | Full plan, all artifacts, coordination state |
| Implementation Agent | ~15-20K | Single task packet, interfaces, relevant existing code |
| Verification Agent | ~25K | Implementation code, tests, requirements |
| Integration Agent | ~30K | All interfaces, API layer, integration context |

**80% Rule**: Never exceed 80% of context window. When approaching limit, prioritize and compress.
