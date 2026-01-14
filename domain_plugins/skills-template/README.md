# Skills Template

A comprehensive template for creating language/framework best practices skills for Claude Code and Claude.ai.

## Quick Start

1. Read `SKILL-TEMPLATE.md` for the complete specification
2. Copy the `starter/` directory as your new skill
3. Replace placeholders with language-specific content
4. Validate against the checklist in the template

## Usage with Claude

Ask Claude to generate a new skill:

```
Create a cpp-best-practices skill following the SKILL-TEMPLATE.md specification
```

Or be more specific:

```
Using SKILL-TEMPLATE.md, create a typescript-best-practices skill focused on:
- Async/await patterns
- Type system optimization
- Build performance
- Runtime efficiency
```

## Directory Structure

```
skills-template/
├── README.md                 # This file
├── SKILL-TEMPLATE.md         # Complete specification
└── starter/                  # Minimal starter files
    ├── SKILL.md              # Entry point template
    └── references/
        ├── guidelines.md     # Main documentation template
        └── rules/
            ├── _sections.md  # Category definitions
            └── _template.md  # Rule file template
```

## Template Highlights

- **8 Priority Categories**: CRITICAL → LOW impact levels
- **40-50 Rules**: Distributed across categories
- **Incorrect/Correct Pattern**: Every rule shows anti-pattern and fix
- **Progressive Disclosure**: SKILL.md is concise; details load on-demand
- **Searchable**: Prefix-based naming enables grep discovery

## Validation

Before publishing a skill, verify:

- [ ] 8 categories defined with proper impact levels
- [ ] 40-50 rules with realistic code examples
- [ ] All files follow naming conventions
- [ ] YAML frontmatter is complete
- [ ] Quick reference covers all categories

See `SKILL-TEMPLATE.md` for the full validation checklist.
