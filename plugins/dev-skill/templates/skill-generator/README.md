# Skill Generator Templates

Templates for generating high-quality performance best practices skills, extracted from reverse-engineering `react-best-practices`.

## Files

| File | Purpose |
|------|---------|
| `MENTAL_MODEL.md` | Core principles, patterns, and appendices for skill creation |
| `INPUT_SCHEMA.yaml` | YAML schema for skill generation inputs |
| `SKILL.md.template` | Entry point template (~120 lines) |
| `RULE.md.template` | Individual rule file template |
| `_sections.md.template` | Category definitions template |
| `_template.md.template` | Rule authoring template for skill authors |
| `metadata.json.template` | Build metadata template |
| `AGENTS.md.template` | Compiled document template |
| `QUALITY_CHECKLIST.md` | Pre-release validation checklist |

## Usage

### Step 1: Define Input Configuration

Copy `INPUT_SCHEMA.yaml` and fill in:

1. **Technology definition** - name, slug, organization
2. **Execution lifecycle** - stages from input to output
3. **Performance categories** - derived from lifecycle, ordered by impact
4. **References** - authoritative documentation and tools

### Step 2: Create Skill Directory

```
skills/{technology}-best-practices/
├── SKILL.md              # From SKILL.md.template
├── metadata.json         # From metadata.json.template
└── rules/
    ├── _sections.md      # From _sections.md.template
    ├── _template.md      # From _template.md.template
    └── {prefix}-{slug}.md # From RULE.md.template (one per rule)
```

### Step 3: Write Rules

For each category, create 3-7 rules following `RULE.md.template`:

1. Identify common performance mistakes
2. Create incorrect + correct examples
3. Quantify impact where data exists
4. Add authoritative references

### Step 4: Compile AGENTS.md

Compile from `rules/*.md` following the algorithm in `MENTAL_MODEL.md` Appendix B.

### Step 5: Validate

Use `QUALITY_CHECKLIST.md` to verify:

- [ ] <5% structural deviation
- [ ] All required sections present
- [ ] No vague language
- [ ] Impact quantified where possible

## Key Principles

From `MENTAL_MODEL.md`:

1. **Cascade Effect**: Earlier lifecycle problems have multiplicative impact
2. **Frequency × Severity = Priority**: Common mistakes may outrank rare severe ones
3. **Actionable Over Theoretical**: Show specific code, not abstract advice
4. **Quantify When Possible**: "2-10× improvement" beats "significant improvement"
5. **Show Both States**: Always include incorrect→correct transformation

## Technology Adaptation

See `MENTAL_MODEL.md` Appendix C for reference hierarchies:

- Systems Languages (C++, Rust, Go)
- Web Frameworks (React, Vue, Angular)
- Database/Query Systems
- Mobile Development (iOS, Android)
- Backend Services (Node.js, Python, Java)

## Reference

Full analysis: `output/skill-reverse-engineer-output.md`
