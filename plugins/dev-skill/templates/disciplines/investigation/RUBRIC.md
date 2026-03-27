# Investigation Validation Rubric

This rubric is read by the `skill-reviewer` agent. Follow these verifiable checks — do not substitute subjective assessment.

## Decision Tree Completeness (check every tree)

For each decision tree file in `references/{symptom}-tree.md`:

1. **No dead ends.** Trace every path from root to leaf. Does every path terminate in an action? (Fix, escalate, or dismiss). If any path ends without a terminal action, it's a dead end — FAIL.
2. **Actions are concrete.** At each terminal node: is the action specific enough to execute? "Escalate to the database team" is OK. "Look into it" is not.
3. **Decision points have criteria.** At each branch: is the criterion measurable? "Is latency > 200ms" is good. "Is the database slow" is vague — what threshold?
4. **Tool references exist.** Every node that says "check X" or "run Y" — does the referenced query/command exist in `references/queries/`?
5. **Expected outcomes documented.** At each check: does the tree say what "normal" looks like vs "abnormal"? The investigator needs to know what they're comparing against.

Record each finding: tree file, path traced, result (PASS/FAIL), specific dead end or vague node.

## Query Pattern Validity (check every query)

For each file in `references/queries/`:

1. **Header present.** Does the file have a comment header explaining purpose and usage?
2. **Syntactic validity.** For SQL: are the queries syntactically valid SQL? For shell: does `bash -n` pass? For Python: does `python -c "import ast; ast.parse(open('{file}').read())"` pass?
3. **Parameters documented.** Are all variable placeholders (e.g., `{threshold}`, `{user_id}`) documented with description and default values?
4. **Expected output described.** Does the header or inline comment explain what the output looks like and how to interpret it?

## Symptom Catalog Consistency

1. **Coverage.** Does `references/symptoms.md` list all symptoms that have decision trees? Are there trees without corresponding catalog entries (orphaned)?
2. **Severity calibration.** Are severity levels (P1/P2/P3) consistent? A P1 symptom should genuinely require immediate attention.
3. **Entry points.** Does each symptom entry point to the correct decision tree file?

## Report Template

1. **All fields present.** Does `assets/templates/report.md` include: summary, timeline, root cause, resolution, and action items sections?
2. **Actionable output.** Would the report be useful to someone who wasn't involved in the investigation? Would they understand what happened and what to do next?

## Configuration

1. **Service references.** Does `config.json` include all external endpoints, dashboard IDs, and service URLs referenced in the queries and trees?
2. **Graceful fallback.** If config is missing, does the skill detect this and ask the user, rather than failing with cryptic errors?

## Verdict

- **SHIP**: All decision tree paths terminate. Queries pass syntax check. Symptom catalog matches trees. Report template is complete.
- **NEEDS WORK**: Some dead-end paths or vague decision criteria. Queries valid but missing documentation. Specific fixes identified.
- **REJECT**: Multiple dead-end paths. Queries don't execute. Symptom catalog doesn't match trees. Unreliable for real investigations.
