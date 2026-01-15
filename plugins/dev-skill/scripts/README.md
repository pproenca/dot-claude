# Skill Creator Scripts

Automation tools for generating and validating performance best practices skills.
Modeled after [OpenSpec](https://github.com/Fission-AI/OpenSpec)'s validation architecture.

## Scripts

### validate-skill.js

Comprehensive skill validator with OpenSpec-level scrutiny.

```bash
node validate-skill.js <skill-directory> [options]
node validate-skill.js --all <skills-directory> [options]
```

#### Options

| Option | Description |
|--------|-------------|
| `--strict` | Treat warnings as errors (fail if any warnings) |
| `--json` | Output JSON report format for programmatic use |
| `--all` | Validate all skills in the given directory |
| `--concurrency N` | Number of parallel validations (default: 6) |
| `--help`, `-h` | Show usage information |

#### Examples

```bash
# Validate single skill
node validate-skill.js ./skills/react-best-practices

# Validate with strict mode (warnings fail)
node validate-skill.js ./skills/react-best-practices --strict

# Output JSON report
node validate-skill.js ./skills/react-best-practices --json

# Validate all skills in directory
node validate-skill.js --all ./skills

# Bulk validation with JSON output
node validate-skill.js --all ./skills --json --concurrency 4
```

#### Exit Codes

- `0` - All validations passed
- `1` - Validation errors found (or warnings in strict mode)

#### Environment Variables

- `SKILL_VALIDATOR_CONCURRENCY` - Default concurrency for bulk validation (default: 6)

---

### build-agents-md.js

Compiles individual rule files into a single AGENTS.md document.

```bash
node build-agents-md.js <skill-directory>
```

#### Example

```bash
node build-agents-md.js ./skills/react-best-practices
```

#### Requirements

- `metadata.json` in skill root
- `rules/_sections.md` with category definitions
- `rules/{prefix}-{slug}.md` individual rule files

#### Output

- Generates `AGENTS.md` in the skill directory
- Reports section count, rule count, and line count

---

## Validation Architecture

The validation system is modeled after OpenSpec's approach:

```
scripts/
├── validate-skill.js          # CLI entry point
├── build-agents-md.js         # AGENTS.md compiler
├── README.md                  # This documentation
└── validation/
    ├── constants.js           # Thresholds, patterns, messages
    ├── types.js               # Type definitions and factories
    ├── schemas.js             # Validation schema functions
    └── validator.js           # SkillValidator class
```

### Validation Levels

| Level | Description | Exit Code |
|-------|-------------|-----------|
| ERROR | Blocking issues that fail validation | 1 |
| WARNING | Notable issues (errors in strict mode) | 0 (1 with --strict) |
| INFO | Suggestions for improvement | 0 |

### Validation Checks (~40 rules)

#### Structure Validation
- Required files exist (SKILL.md, metadata.json, rules/_sections.md, rules/_template.md)
- metadata.json is valid JSON with required fields
- SKILL.md has required frontmatter (name, description)
- SKILL.md line count is within expected range

#### Content Validation
- Sections are sequentially numbered
- Section impacts are valid (CRITICAL, HIGH, MEDIUM-HIGH, MEDIUM, LOW-MEDIUM, LOW)
- Sections are ordered by impact (CRITICAL first, LOW last)
- Section prefixes are 2-8 lowercase characters
- Rule files have required frontmatter (title, impact, tags)
- Rule first tag matches category prefix
- Rules have **Incorrect** and **Correct** code examples
- Rules have at least 2 code blocks

#### Language Quality
- No vague language patterns (consider, might want, perhaps, etc.)
- No marketing language (amazing, revolutionary, blazing fast, etc.)
- Impact descriptions are quantified (2-10×, 200ms, O(n) to O(1), etc.)
- Rule titles use imperative mood (Avoid, Use, Cache, etc.)
- Rule explanations meet minimum length

#### Cross-Reference Validation
- All rule prefixes exist in _sections.md
- Each section has at least one rule
- Categories don't exceed maximum rules

#### Statistics Validation
- Total rules meet minimum count (10+)
- Quantified impact percentage meets target (80%+)

---

## JSON Output Format

When using `--json`, the output follows this structure:

```json
{
  "version": "1.0",
  "items": [
    {
      "id": "react-best-practices",
      "type": "skill",
      "valid": false,
      "issues": [
        {
          "level": "ERROR",
          "path": "rules/async-foo.md",
          "message": "Missing required frontmatter field: title"
        },
        {
          "level": "WARNING",
          "path": "rules/async-bar.md",
          "message": "Contains vague language: \"consider\""
        }
      ],
      "durationMs": 123
    }
  ],
  "summary": {
    "totals": {
      "items": 1,
      "passed": 0,
      "failed": 1
    },
    "byType": {
      "skill": {
        "items": 1,
        "passed": 0,
        "failed": 1
      }
    }
  }
}
```

---

## Vague Language Patterns

The validator flags these patterns as vague:

| Pattern | Suggested Replacement |
|---------|----------------------|
| consider | Use X when Y |
| might want | Use X for Y |
| perhaps | X provides Y |
| potentially | X causes Y |
| probably | X results in Y |
| maybe | X or Y depending on Z |
| it depends | For A use X, for B use Y |
| sometimes | When X, use Y |
| in some cases | For scenarios with X |
| can be helpful | X improves Y |

---

## Marketing Language Patterns

The validator flags these patterns:

- amazing, incredible, revolutionary
- blazing fast, super easy
- game changer, game changing
- magic, magical
- powerful, seamless

Replace with specific, quantified claims.

---

## Impact Quantification Patterns

Valid quantification formats:

| Type | Pattern | Example |
|------|---------|---------|
| Multiplier | `N-M×` or `Nx` | 2-10× improvement |
| Time | `Nms` | 200ms reduction |
| Complexity | `O(x) to O(y)` | O(n) to O(1) |
| Percentage | `N%` | 30% reduction |
| Absolute | `N to M` | reduces 1000 to 10 |
| Operations | `N ops` | 1M ops/sec |
| Prevention | `prevents X` | prevents stale closures |
| Elimination | `eliminates X` | eliminates jank |

Invalid (too vague):
- "faster", "better", "improved", "significant"

---

## Usage in Skill Generation Workflow

After generating a new skill:

1. **Build AGENTS.md:**
   ```bash
   node scripts/build-agents-md.js ./skills/my-new-skill
   ```

2. **Validate the skill:**
   ```bash
   node scripts/validate-skill.js ./skills/my-new-skill
   ```

3. **Fix any errors** reported by validation

4. **Re-validate** until all checks pass:
   ```bash
   node scripts/validate-skill.js ./skills/my-new-skill --strict
   ```

5. **Before release**, ensure strict validation passes:
   ```bash
   node scripts/validate-skill.js ./skills/my-new-skill --strict
   ```

---

## Extending the Validator

### Adding New Checks

1. Add patterns/messages to `validation/constants.js`
2. Add validation functions to `validation/schemas.js`
3. Call new validators from `validation/validator.js`

### Adding New Validation Levels

The three levels (ERROR, WARNING, INFO) match OpenSpec's design:

```javascript
const { createError, createWarning, createInfo } = require('./validation/types.js');

// Blocking issue
createError('path', 'message');

// Notable but non-blocking
createWarning('path', 'message');

// Suggestion
createInfo('path', 'message');
```

---

## Comparison with OpenSpec

| Feature | OpenSpec | Skill Validator |
|---------|----------|-----------------|
| Schema validation | Zod | Pure JavaScript |
| Three-level issues | ✅ | ✅ |
| Enriched error messages | ✅ | ✅ |
| Remediation guidance | ✅ | ✅ |
| Strict mode | ✅ | ✅ |
| JSON output | ✅ | ✅ |
| Bulk validation | ✅ | ✅ |
| Concurrency control | ✅ | ✅ |
| Cross-file validation | ✅ | ✅ |
| Next steps guidance | ✅ | ✅ |
