# Skill Creator

Create effective Claude Code skills that extend capabilities with specialized knowledge and workflows.

## Skills

| Skill | Purpose |
|-------|---------|
| skill-creator | Comprehensive skill authoring guide |

## Core Principles

**Concise is Key**
Only add context Claude doesn't already have. Challenge each piece: "Does this justify its token cost?"

**Progressive Disclosure**
- Metadata (name + description): ~100 words, always loaded
- SKILL.md body: <5k words, loaded when triggered
- Bundled resources: loaded as needed

**Set Appropriate Freedom**
- High freedom: Multiple approaches valid
- Medium freedom: Preferred pattern with variation
- Low freedom: Fragile operations requiring specific steps

## Skill Anatomy

```
skill-name/
├── SKILL.md            # Required
├── scripts/            # Executable code
├── references/         # Documentation loaded as needed
└── assets/             # Files used in output
```

## Creation Process

1. **Understand** with concrete examples
2. **Plan** reusable contents (scripts, references, assets)
3. **Initialize** with `scripts/init_skill.py`
4. **Edit** SKILL.md and bundled resources
5. **Package** with `scripts/package_skill.py`
6. **Iterate** based on real usage

## Usage

Ask Claude to create a skill:

```
Create a skill for PDF editing
```

The skill guides through the full creation process, from planning to packaging.
