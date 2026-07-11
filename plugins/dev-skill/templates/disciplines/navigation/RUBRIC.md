# Navigation Validation Rubric

This rubric is read by the `skill-reviewer` agent. Follow these verifiable checks — do not substitute subjective assessment.

## Staleness Audit (the defining check — run first)

Scan every file in the skill (`SKILL.md`, `references/*.md`) for baked-in technical facts. Apply the litmus test line by line: **would this line need editing when the technology ships a new version?**

- Baked-in facts — FAIL: API signatures, parameter lists, behavior claims ("X returns a promise"), default values, version-specific migration steps, code examples demonstrating the technology's API.
- Navigational content — PASS: URL patterns, version schemes ("docs are versioned via the `/v{N}/` path segment"), repo layout, search operators, source authority scopes, tool invocations.

Record each violation: file, line, the fact stated, and where the skill should route the agent instead. Even one embedded fact is a FAIL for this section — it will be wrong someday and the agent will trust it.

## Source Map Validity (check every source in references/sources.md)

1. **Live URLs.** Spot-check each source's base URL and at least one constructed deep link (fill the URL pattern with a real symbol/module) via WebFetch or WebSearch. A 404 or a redirect to a different product is a FAIL for that source.
2. **Authority scope stated both ways.** Each source declares what it is authoritative for AND what it is not. A source with no "not authoritative for" entry is incomplete.
3. **Access pattern is concrete.** Each source names the tool invocation (WebFetch URL template, `site:` operator, local script, MCP tool) — "check the docs" is not an access pattern.
4. **Authority ranking is defensible.** Official docs/spec/source/changelog outrank maintainer writing, which outranks community content. Community sources may appear only as lead generators with an explicit trace-to-primary instruction.
5. **Currency signals documented.** Each source says how to tell which version a page describes.

## Playbook Completeness (check every references/*-playbook.md)

1. **Steps name tool + query.** Every step has a concrete, executable invocation with a filled or parameterized query. "Search for the error" is vague — FAIL; "WebSearch: `\"{error text}\" site:github.com/{org}/{repo}/issues`" passes.
2. **Hit criteria present.** Each step states what a successful result looks like, so the agent knows stop vs. continue.
3. **Every path terminates.** The final step is an explicit escalation (read source at a named location, or ask the user). A playbook whose last step is another search is a dead end — FAIL.
4. **Verification is the exit.** Each playbook ends by pointing to `references/verification.md` (or embeds equivalent checks). An answer accepted without verification is a FAIL.
5. **Ordering is justified.** Cheap high-precision steps (deep-link fetch) come before broad searches; source-code reading comes last. Flag inversions.

## Verification Rules (references/verification.md)

1. **Currency check present.** Defines how to determine the project's version and the found content's version, and requires they match (or the mismatch be surfaced).
2. **Authority check present.** Ties acceptance back to the source map's ranking; community content requires tracing to a primary source.
3. **Rejection criteria are concrete.** Names the tells of low-authority content (no author, no date, no version, listicle/SEO framing) — not just "avoid bad sources".
4. **Cross-check rule for high-stakes answers.** Destructive or hard-to-reverse actions require two independent primary sources.

## Coverage & Routing

1. **Question types cover the interview.** Every question type the user named has a playbook; no playbook exists without a plausible triggering question.
2. **SKILL.md routes correctly.** The routing table maps each question type to its playbook file, and every playbook file is reachable from SKILL.md.
3. **Description triggers on intent.** The SKILL.md description names the technology and the lookup intents ("finding current API details, upgrade impacts, error causes for X") — not a generic "documentation helper".

## Configuration (if config.json exists)

1. **Referenced tools exist.** Local paths, scripts, and MCP tools named in playbooks appear in config.json (or are standard session tools).
2. **Graceful fallback.** If a local source is missing, the playbook has a public-source alternative or asks the user — it doesn't dead-end.

## Verdict

- **SHIP**: Zero baked-in facts. All spot-checked URLs live. Every playbook step names a tool and query, every path terminates, verification rules are concrete.
- **NEEDS WORK**: Isolated staleness violations or vague steps with specific fixes identified. Sources live but authority scopes incomplete.
- **REJECT**: Multiple embedded technical facts (it's a distillation skill in disguise), dead sources, or playbooks that are restated "search the web" advice. Unreliable as a navigation aid.
