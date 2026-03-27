# Investigation Recipe

Investigation maps a domain's symptom space to diagnostic decision trees, query patterns, and report templates. This is the production method for **Runbook** and **Data Fetching & Analysis** skills.

## What Investigation Produces

```
{skill-name}/
├── SKILL.md              # Symptom overview + trigger phrases
├── metadata.json         # discipline: "investigation"
├── config.json           # Service URLs, dashboard IDs, query endpoints
├── gotchas.md            # Diagnostic dead-ends discovered over time
├── references/
│   ├── symptoms.md       # Symptom catalog with entry points
│   ├── {symptom}-tree.md # Decision tree per symptom class
│   └── queries/          # Reusable query patterns
│       ├── {name}.sql    # SQL query templates
│       ├── {name}.sh     # CLI investigation commands
│       └── {name}.py     # Data analysis scripts (optional)
└── assets/
    └── templates/
        └── report.md     # Investigation report template
```

## Inputs Needed

1. **Domain/service map**: What system or domain does this investigate? What are its components?
2. **Symptom catalog**: What are the common symptoms or questions? What triggers an investigation?
3. **Tool/query inventory**: What tools, dashboards, databases, or APIs are used to investigate?
4. **Report format**: What does the output of an investigation look like?

## Discovery Workflow

### Step 1: Interview

Ask the user with `AskUserQuestion`:

```
Question: "What type of investigation skill are you creating?"
Header: "Investigation Type"
Options:
- "Runbook — diagnose and resolve operational issues for a service/system"
- "Data Analysis — connect to data sources, run queries, answer business questions"
```

Then ask free-form:
- "What system or domain does this cover? What are its main components?"
- "What are the top 5-10 symptoms or questions that trigger an investigation?"
- "What tools do you use to investigate? (dashboards, SQL, CLI commands, APIs, log systems)"

### Step 2: Map the Symptom Space

Structure the user's symptoms into a catalog:

```markdown
## Symptom Catalog

| # | Symptom / Question | Entry Point | Severity |
|---|-------------------|-------------|----------|
| 1 | High latency on /api/checkout | latency-tree.md | P1 |
| 2 | Error rate spike in payment service | error-rate-tree.md | P1 |
| 3 | "Why did conversion drop this week?" | conversion-tree.md | P2 |
```

For each symptom, identify:
- **Entry point**: The first thing to check
- **Investigation tools**: What you query/check at each decision point
- **Terminal states**: Resolution (fix it), Escalation (hand off), or False alarm (not a problem)

### Step 3: Design Decision Trees

Each symptom class gets a decision tree:

```
Symptom: High latency on /api/checkout
│
├── Check: Is it all endpoints or just checkout?
│   ├── All endpoints → Check: Is the database responding?
│   │   ├── DB slow → Check: queries/slow-queries.sql
│   │   │   ├── Long-running query found → Kill query, investigate lock
│   │   │   └── No slow queries → Check connection pool exhaustion
│   │   └── DB fine → Check: Is it upstream dependency?
│   └── Just checkout → Check: Recent deploy?
│       ├── Yes → Compare error rates before/after deploy
│       └── No → Check: Payment provider status page
```

Rules for decision trees:
- **Every path must terminate.** Dead ends are bugs.
- **Terminal states are actions.** "Escalate to {team}", "Run {fix}", or "Not a problem because {reason}".
- **Each node references a specific tool or query.** Not "check the database" but "run queries/slow-queries.sql"
- **Include the expected output at each node.** What does "DB slow" look like? (>200ms p99)

### Step 4: Inventory Query Patterns

Collect reusable queries the agent can compose:

```sql
-- queries/slow-queries.sql
-- Find queries running longer than {threshold}ms
-- Usage: Replace {threshold} with desired ms (default: 1000)
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
  AND now() - pg_stat_activity.query_start > interval '{threshold} milliseconds'
ORDER BY duration DESC;
```

Query patterns must:
- Have a comment header explaining purpose and usage
- Use named parameters (not hardcoded values)
- Be syntactically valid for the target system
- Include expected output format

### Step 5: Design Report Template

The output of an investigation:

```markdown
# Investigation Report: {symptom}

**Date:** {date}
**Investigator:** {agent/user}
**Severity:** {P1/P2/P3}
**Duration:** {time spent}

## Summary
{1-2 sentence finding}

## Timeline
- {HH:MM} — Symptom detected: {description}
- {HH:MM} — Checked: {what}, found: {what}
- {HH:MM} — Root cause identified: {description}

## Root Cause
{Detailed explanation}

## Resolution
{What was done to fix it, or escalation path}

## Action Items
- [ ] {Preventive measure 1}
- [ ] {Preventive measure 2}
```

### Step 6: Planning Checkpoint

Display symptom catalog, decision tree summaries, and query inventory. Ask user to approve before generating.

## Generation Pipeline

After user approval:

1. **Generate SKILL.md** — Symptom overview, trigger phrases, quick reference to trees
2. **Generate references/symptoms.md** — Full symptom catalog with entry points
3. **Generate references/{symptom}-tree.md** — One decision tree per symptom class
4. **Generate references/queries/** — Reusable query patterns
5. **Generate assets/templates/report.md** — Investigation report template
6. **Generate config.json** — Service URLs, dashboard IDs, endpoints
7. **Generate metadata.json** with `discipline: "investigation"`
8. **Validate** with investigation RUBRIC.md

## Type-Specific Guidance

### Runbook Skills

Focus on: symptom → investigation → resolution.

- Every decision tree path terminates in an action (fix, escalate, or dismiss)
- Include severity assessment at each node (is this getting worse?)
- Reference specific dashboards and alert thresholds
- Include "usual suspects" — the top 3 causes for each symptom, ordered by frequency
- Store investigation history in `${CLAUDE_PLUGIN_DATA}/investigations.log` — the agent can detect recurring patterns

Runbook SKILL.md should include:
```markdown
## Common Symptoms

| Symptom | Usual Cause | Quick Check |
|---------|-------------|-------------|
| High latency | Database locks | `queries/slow-queries.sql` |
| Error spike | Failed deploy | `git log --oneline -5` |
| OOM kills | Memory leak in {service} | `queries/memory-usage.sh` |
```

### Data Analysis Skills

Focus on: query composition and data access patterns.

- Provide helper functions/queries the agent can compose for complex analysis
- Include table/schema documentation (what columns exist, what they mean)
- Define canonical IDs (which table has the authoritative `user_id`?)
- Include common joins and aggregation patterns
- Store query results in structured format for cross-query analysis

Data Analysis SKILL.md should include:
```markdown
## Available Data Sources

| Source | Access | Key Tables |
|--------|--------|------------|
| Analytics DB | `queries/analytics-*.sql` | events, users, sessions |
| Billing API | `queries/billing-*.sh` | invoices, subscriptions |
```

## Investigation vs Distillation: Key Differences

| Aspect | Distillation | Investigation |
|--------|-------------|---------------|
| Core output | Reference rules | Decision trees + query patterns |
| Value lives in | Knowledge and code examples | Diagnostic logic and tool mapping |
| Validation focus | Factual accuracy of claims | Path completeness, query validity |
| Bootstrap depth | Full (40+ rules) | Seed branches (grows through incidents) |
| Growth pattern | Add rules as patterns emerge | Add branches as new symptoms/resolutions discovered |
