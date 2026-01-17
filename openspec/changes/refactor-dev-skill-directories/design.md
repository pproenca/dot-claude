# Design: dev-skill Generated Output Structure

## Context

The `dev-skill` plugin generates performance best practices skills. Each generated skill contains:
- Reference documentation (individual rule files with examples)
- Templates for extending the skill
- A compiled AGENTS.md for easy agent consumption
- SKILL.md as entry point

## Goals

- **Clarity**: Directory names clearly indicate purpose (`references/` for docs, `assets/templates/` for scaffolding)
- **Discoverability**: Markdown links make navigation easy for humans and agents
- **Consistency**: All file references use markdown link format

## Non-Goals

- Changing the structure of the dev-skill plugin itself (only its output changes)
- Changing validation or build logic fundamentals
- Modifying rule file content format

## Decisions

### Decision 1: Generated skills use `references/` for rule files

**What**: Rule files like `async-parallel.md`, `bundle-imports.md` go in `references/` instead of `rules/`.

**Why**:
- `references/` better describes documentation that agents reference
- Aligns with how other Claude plugins organize reference material
- `rules/` can be confused with linting rules or strict enforcement

**Generated structure**:
```
{skill}/
├── SKILL.md
├── AGENTS.md
├── metadata.json
├── README.md
├── references/
│   ├── _sections.md
│   ├── async-parallel.md
│   ├── bundle-imports.md
│   └── ...
└── assets/
    └── templates/
        ├── _template.md
        └── RULE.md.template
```

### Decision 2: Templates go in `assets/templates/`

**What**: Scaffolding files (`_template.md`, rule templates) go in `assets/templates/`.

**Why**:
- Clear separation: `references/` = documentation, `assets/` = scaffolding/resources
- `_sections.md` stays in `references/` because it's a reference doc, not a template
- Template files are for creating new rules, not for reading

### Decision 3: Markdown links in SKILL.md

**What**: All file references in SKILL.md use markdown link format.

**Before**:
```markdown
Read individual rule files for detailed explanations:
rules/async-parallel.md
rules/_sections.md
```

**After**:
```markdown
Read individual rule files for detailed explanations:
- [Section definitions](references/_sections.md)
- [Async parallelization](references/async-parallel.md)

For the complete guide: [AGENTS.md](AGENTS.md)
```

### Decision 4: AGENTS.md includes navigation links

**What**: The generated AGENTS.md includes a footer with links to source files.

**Example footer**:
```markdown
---

## Source Files

This document was compiled from individual reference files:
- [Section definitions](references/_sections.md)
- [Rule template](assets/templates/_template.md)
```

### Decision 5: build-agents-md.js reads from `references/`

**What**: The build script looks for rule files in `references/` instead of `rules/`.

**Migration**:
1. Update path constants in build-agents-md.js
2. Look for `_sections.md` in `references/`
3. Rule files are `references/{prefix}-{slug}.md`

## Risks / Trade-offs

**Risk**: Existing skills using `rules/` won't work with updated build script.
**Mitigation**: This is expected. Users regenerate skills or manually rename directories.

**Risk**: Documentation references may become stale.
**Mitigation**: Validation script checks for broken links.

## Migration Plan

1. Update templates first (no runtime impact)
2. Update build-agents-md.js path references
3. Update commands/new.md documentation
4. Regenerate example skill in references/ to validate
5. Run full validation

## Open Questions

None - scope is well-defined.
