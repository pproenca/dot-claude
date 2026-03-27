# Extraction Validation Rubric

This rubric is read by the `skill-reviewer` agent. Follow these verifiable checks — do not substitute subjective assessment.

## Template Validity (check every template in assets/templates/)

For each template file:

1. **Parameter documentation.** Are all placeholders (`{name}`, `{type}`, etc.) documented with description, required/optional, and defaults?
2. **Render test.** Mentally substitute realistic parameter values into the template. Does the result look like valid code for the target framework? Would it compile/lint?
3. **Complete output.** Does the template produce all necessary files? (e.g., component + test + types). Are file paths documented?
4. **No hardcoded values.** Are all instance-specific values parameterized? Flag anything that should vary but is hardcoded (e.g., a specific module name, a hardcoded path).
5. **Framework idioms.** Does the generated code follow the target framework's current idioms? (Not deprecated patterns, not third-party alternatives when the framework provides a native solution.)

Record each finding: template file, check performed, result (PASS/FAIL).

## Convention Documentation (check references/conventions.md)

1. **Rationale present.** Does every convention have a "Why" explanation? Conventions without rationale are arbitrary and will be ignored.
2. **Consistency with templates.** Do the templates actually enforce the conventions described? If conventions.md says "kebab-case files" but a template generates `MyComponent.tsx`, that's a contradiction.
3. **Exception guidance.** For conventions with valid exceptions: is there guidance on when to deviate?

## Parameter Design

1. **Naming clarity.** Are parameter names self-explanatory? `name` is OK. `n` is not. `component_type` is better than `type`.
2. **Sensible defaults.** Do optional parameters have reasonable defaults? Would the default produce a valid, useful output?
3. **Validation hints.** For parameters with constraints (e.g., "must be PascalCase"): is the constraint documented?

## Configuration

1. **Project overrides.** Does `config.json` allow overriding output paths, naming conventions, or framework version?
2. **Graceful handling.** If config is missing, does the skill use sensible defaults rather than failing?

## Usefulness Assessment

1. **Boilerplate reduction.** Does this template eliminate meaningful boilerplate? If the template produces <10 lines that the user could type in 30 seconds, it's not worth being a template.
2. **Convention value.** Do the enforced conventions prevent real problems? (Not just aesthetic preferences, but things that cause bugs or inconsistency.)

## Verdict

- **SHIP**: All templates render valid code with realistic parameters. Conventions documented with rationale. Parameters clear and well-defaulted.
- **NEEDS WORK**: Templates render but with minor issues (deprecated patterns, missing test file). Conventions partially documented. Specific fixes identified.
- **REJECT**: Templates produce invalid code. Conventions contradict templates. Parameters undocumented. Not useful for scaffolding.
