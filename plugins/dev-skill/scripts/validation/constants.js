/**
 * Validation Constants
 *
 * Centralized thresholds, patterns, and messages for skill validation.
 * Modeled after OpenSpec's validation/constants.ts
 */

// Valid disciplines and types
const VALID_DISCIPLINES = ['distillation', 'composition', 'extraction', 'investigation'];
const VALID_TYPES = [
  'library-reference', 'verification', 'automation', 'scaffolding',
  'code-quality', 'cicd', 'runbook', 'data-analysis', 'infra-ops'
];

// Thresholds for content length validation
const MIN_PURPOSE_LENGTH = 50;
const MIN_RULE_EXPLANATION_LENGTH = 30;
const MIN_SECTION_DESCRIPTION_LENGTH = 20;
const MIN_ABSTRACT_LENGTH = 100;
const MIN_SKILL_DESCRIPTION_LENGTH = 50;
const MAX_SKILL_MD_LINES = 300;
const MIN_SKILL_MD_LINES = 50;
const MIN_RULE_COUNT = 10;
const MAX_RULE_COUNT = 100;
const MAX_RULES_PER_CATEGORY = 15;
const TARGET_QUANTIFIED_PERCENT = 40;
const MIN_CODE_BLOCKS_PER_RULE = 4;
const MIN_PREFIX_LENGTH = 2;
const MAX_PREFIX_LENGTH = 10;
const MIN_EXAMPLE_LINES = 3;
const MAX_EXAMPLE_LINES = 50;
const RECOMMENDED_MAX_EXAMPLE_LINES = 20;

/**
 * Tag alias mapping for common prefixes.
 * Maps full tag names to their prefix equivalents.
 * When a rule file has prefix X, the first tag can be X or any tag that maps to X.
 */
const TAG_ALIAS_MAP = {
  'javascript': 'js',
  'typescript': 'ts',
  'react': 'rerender',       // rerender-*.md files often use "react" as first tag
  'server': 'server',
  'client': 'client',
  'bundle': 'bundle',
  'async': 'async',
  'api-routes': 'async',     // async-api-routes.md uses "api-routes" as first tag
  'rendering': 'rendering',
  'rerender': 'rerender',
  'advanced': 'advanced',
};

// Impact levels in priority order (CRITICAL = highest priority)
const IMPACT_LEVELS = ['CRITICAL', 'HIGH', 'MEDIUM-HIGH', 'MEDIUM', 'LOW-MEDIUM', 'LOW'];
const IMPACT_LEVELS_SET = new Set(IMPACT_LEVELS);
const IMPACT_ORDER = Object.fromEntries(IMPACT_LEVELS.map((level, i) => [level, i]));

// Vague language patterns that should be avoided in documentation
const VAGUE_PATTERNS = [
  // Note: "consider" removed - commonly used appropriately to suggest alternatives
  { pattern: /\bmight\s+want\b/gi, term: 'might want' },
  { pattern: /\bperhaps\b/gi, term: 'perhaps' },
  { pattern: /\bpotentially\b/gi, term: 'potentially' },
  { pattern: /\bprobably\b/gi, term: 'probably' },
  { pattern: /\bcould\s+possibly\b/gi, term: 'could possibly' },
  { pattern: /\bmaybe\b/gi, term: 'maybe' },
  { pattern: /\bit\s+depends\b/gi, term: 'it depends' },
  { pattern: /\bin\s+some\s+cases\b/gi, term: 'in some cases' },
  { pattern: /\bcan\s+be\s+(?:helpful|useful|beneficial)\b/gi, term: 'can be helpful/useful' },
  { pattern: /\byou\s+may\s+want\b/gi, term: 'you may want' },
  { pattern: /\bit\s+is\s+recommended\b/gi, term: 'it is recommended' },
];

// Marketing/hyperbolic language patterns
const MARKETING_PATTERNS = [
  { pattern: /\bamazing\b/gi, term: 'amazing' },
  { pattern: /\bincredible\b/gi, term: 'incredible' },
  { pattern: /\brevolutionary\b/gi, term: 'revolutionary' },
  { pattern: /\bblazing[\s-]*fast\b/gi, term: 'blazing fast' },
  { pattern: /\bgame[\s-]*chang(?:er|ing)\b/gi, term: 'game changer' },
  { pattern: /\bsuper[\s-]*easy\b/gi, term: 'super easy' },
  { pattern: /\bmagic(?:al)?\b/gi, term: 'magic/magical' },
  { pattern: /\bpowerful\b/gi, term: 'powerful' },
  { pattern: /\bseamless(?:ly)?\b/gi, term: 'seamless' },
];

// Generic variable/function names that indicate non-production code examples
const GENERIC_NAME_PATTERNS = [
  // Classic placeholder names (foo/bar family)
  { pattern: /\bfoo\b/gi, term: 'foo' },
  { pattern: /\bbar\b/gi, term: 'bar' },
  { pattern: /\bbaz\b/gi, term: 'baz' },
  { pattern: /\bqux\b/gi, term: 'qux' },
  { pattern: /\bquux\b/gi, term: 'quux' },

  // Generic function names
  { pattern: /\bdoStuff\s*\(/gi, term: 'doStuff()' },
  { pattern: /\bdoSomething\s*\(/gi, term: 'doSomething()' },
  { pattern: /\bhandleStuff\s*\(/gi, term: 'handleStuff()' },
  { pattern: /\bprocessData\s*\(/gi, term: 'processData()' },
  { pattern: /\bmyFunction\s*\(/gi, term: 'myFunction()' },
  { pattern: /\bmyMethod\s*\(/gi, term: 'myMethod()' },
  { pattern: /\btestFunction\s*\(/gi, term: 'testFunction()' },

  // Generic variable names (case-insensitive)
  { pattern: /\bthing\b/gi, term: 'thing' },
  { pattern: /\bstuff\b/gi, term: 'stuff' },
  { pattern: /\bdata\d+\b/gi, term: 'data1/data2' },
  { pattern: /\bvalue\d+\b/gi, term: 'value1/value2' },
  { pattern: /\bitem\d+\b/gi, term: 'item1/item2' },
  { pattern: /\bresult\d+\b/gi, term: 'result1/result2' },
  { pattern: /\btmp\b/gi, term: 'tmp' },
  { pattern: /\btemp\b/gi, term: 'temp' },

  // Generic class/type names
  { pattern: /\bMyClass\b/g, term: 'MyClass' },
  { pattern: /\bMyComponent\b/g, term: 'MyComponent' },
  { pattern: /\bMyService\b/g, term: 'MyService' },
  { pattern: /\bExampleComponent\b/g, term: 'ExampleComponent' },
  { pattern: /\bTestComponent\b/g, term: 'TestComponent' },

  // Generic hook names (React-specific)
  { pattern: /\buseMyHook\s*\(/g, term: 'useMyHook()' },
  { pattern: /\buseStuff\s*\(/g, term: 'useStuff()' },
  { pattern: /\buseSomething\s*\(/g, term: 'useSomething()' },

  // Lorem ipsum indicators (documentation placeholders)
  { pattern: /\blorem\b/gi, term: 'lorem' },
  { pattern: /\bipsum\b/gi, term: 'ipsum' },
];

// Syntax explanation comment patterns - comments that state the obvious
const SYNTAX_COMMENT_PATTERNS = [
  { pattern: /\/\/\s*(?:this\s+)?(?:calls?|invokes?|runs?)\s+(?:the\s+)?(?:function|method)/gi, term: 'calls function' },
  { pattern: /\/\/\s*(?:this\s+)?(?:creates?|makes?)\s+(?:a\s+)?new\s+/gi, term: 'creates new' },
  { pattern: /\/\/\s*(?:this\s+)?returns?\s+(?:the\s+)?/gi, term: 'returns' },
  { pattern: /\/\/\s*(?:this\s+)?sets?\s+(?:the\s+)?/gi, term: 'sets' },
  { pattern: /\/\/\s*(?:this\s+)?gets?\s+(?:the\s+)?/gi, term: 'gets' },
];

// Patterns that indicate quantified or descriptive impact
const QUANTIFIED_PATTERNS = [
  // Numeric patterns
  /\d+[-–]\d+[×x]/i,                          // 2-10×
  /\d+[×x]\s*(?:faster|slower|improvement)/i,  // 2x faster
  /\d+\s*ms\b/i,                               // 200ms
  /\d+[-–]\d+\s*ms\b/i,                        // 100-200ms
  /O\([^)]+\)\s*to\s*O\([^)]+\)/i,            // O(n) to O(1)
  /O\([^)]+\)/,                                // O(n)
  /\d+\s*%/,                                   // 30%
  /\d+\s*to\s*\d+/i,                           // 1000 to 10
  /\d+[kKmMgG]?\s*(?:ops|operations)/i,        // 1M ops
  /\d+[-–]\d+\s*seconds?\b/i,                  // 2-3 seconds
  // Outcome verbs (with any following description)
  /\breduces?\s+\w+/i,                         // reduces reflows, reduces lookups
  /\bsaves?\s+\w+/i,                           // saves 200, saves time
  /\bprevents?\s+\w+/i,                        // prevents stale closures
  /\bavoids?\s+\w+/i,                          // avoids re-creation
  /\beliminates?\s+\w+/i,                      // eliminates jank
  /\bfaster\s+\w+/i,                           // faster initial render
  /\benables?\s+\w+/i,                         // enables hardware acceleration
  /\bmaintains?\s+\w+/i,                       // maintains UI responsiveness
  /\bminimizes?\s+\w+/i,                       // minimizes effect re-runs
  /\bpreserves?\s+\w+/i,                       // preserves state/DOM
  /\bdeduplicates?\s+\w+/i,                    // deduplicates within request
  /\bcaches?\s+\w+/i,                          // caches across requests
  /\bloads?\s+\w+/i,                           // loads after hydration
  /\bstable\s+\w+/i,                           // stable subscriptions
  /\bdirectly\s+affects?\s+\w+/i,              // directly affects TTI
  /\bautomatic\s+\w+/i,                        // automatic deduplication
  /\bsingle\s+\w+/i,                           // single listener for N
  /\bwasted\s+\w+/i,                           // wasted computation
];

// Valid title patterns (imperative mood or descriptive technical patterns)
const VALID_TITLE_PATTERNS = [
  // Imperative verbs
  /^Avoid\s+/i,              // Avoid Barrel Imports
  /^Use\s+/i,                // Use SWR for Deduplication
  /^Cache\s+/i,              // Cache Property Access
  /^Batch\s+/i,              // Batch DOM Operations
  /^Defer\s+/i,              // Defer Non-Critical Work
  /^Extract\s+/i,            // Extract Server Components
  /^Implement\s+/i,          // Implement Lazy Loading
  /^Minimize\s+/i,           // Minimize Bundle Size
  /^Optimize\s+/i,           // Optimize Render Cycles
  /^Parallelize\s+/i,        // Parallelize Requests
  /^Prefer\s+/i,             // Prefer Static Generation
  /^Prevent\s+/i,            // Prevent Memory Leaks
  /^Reduce\s+/i,             // Reduce Re-renders
  /^Replace\s+/i,            // Replace forEach with for
  /^Configure\s+/i,          // Configure Thread Pool
  /^Enable\s+/i,             // Enable Compression
  /^Register\s+/i,           // Register Cleanup Hooks
  /^Validate\s+/i,           // Validate Input Types
  // Technical patterns (hooks, APIs, methods)
  /^use[A-Z]/,               // useLatest, useMemo, etc.
  /^Promise\./,              // Promise.all(), Promise.race()
  /^React\./,                // React.cache(), React.memo()
  /^CSS\s+/i,                // CSS content-visibility
  /^[A-Z][\w.()]+\s+for\s+/i, // "X for Y" patterns
  // Descriptive patterns
  /^Per-/i,                  // Per-Request Deduplication
  /^Cross-/i,                // Cross-Request LRU Caching
  /^\w+-Based\s+/i,          // Dependency-Based Parallelization
  /^[A-Z][a-z]+\s+/,         // Generic: Verb + Object
];

// Validation error and warning messages
const VALIDATION_MESSAGES = {
  // File Structure
  MISSING_FILE: (file) => `Missing required file: ${file}`,
  INVALID_JSON: (file, error) => `${file}: Invalid JSON - ${error}`,
  NO_RULES_FOUND: 'No rule files found in references/ (or rules/) directory',
  NO_SECTIONS_DEFINED: 'No sections defined in _sections.md',

  // SKILL.md
  SKILL_MISSING_NAME: 'SKILL.md: Missing required frontmatter field: name',
  SKILL_MISSING_DESCRIPTION: 'SKILL.md: Missing required frontmatter field: description',
  SKILL_NAME_NOT_KEBAB: 'SKILL.md: name must be kebab-case (e.g., "react-best-practices")',
  SKILL_DESCRIPTION_TOO_SHORT: `SKILL.md: description must be at least ${MIN_SKILL_DESCRIPTION_LENGTH} characters`,
  SKILL_TOO_SHORT: (lines) => `SKILL.md is very short (${lines} lines), expected ${MIN_SKILL_MD_LINES}-${MAX_SKILL_MD_LINES}`,
  SKILL_TOO_LONG: (lines) => `SKILL.md is very long (${lines} lines), consider moving detail to references`,
  SKILL_MISSING_SECTION: (section) => `SKILL.md: Missing recommended section: "${section}"`,
  SKILL_H1_MISSING: 'SKILL.md: Missing H1 title',
  SKILL_H1_WRONG_FORMAT: (h1) => `SKILL.md: H1 "${h1}" must follow format "# {Organization} {Technology} Best Practices"`,

  // metadata.json
  METADATA_MISSING_FIELD: (field) => `metadata.json: Missing required field: ${field}`,
  METADATA_REFERENCES_NOT_ARRAY: 'metadata.json: references must be an array',
  METADATA_ABSTRACT_TOO_SHORT: `metadata.json: abstract must be at least ${MIN_ABSTRACT_LENGTH} characters`,
  METADATA_INVALID_VERSION: 'metadata.json: version must be semantic version format (e.g., "1.0.0")',
  METADATA_EMPTY_REFERENCES: 'metadata.json: references array is empty',

  // _sections.md
  SECTION_NUMBERING_GAP: (name, expected, actual) => `_sections.md: Section "${name}" has index ${actual}, expected ${expected}`,
  SECTION_INVALID_IMPACT: (name, impact) => `_sections.md: Section "${name}" has invalid impact level: ${impact}`,
  SECTION_IMPACT_ORDER: (name, prevName) => `_sections.md: Section "${name}" has higher impact than previous section "${prevName}"`,
  SECTION_PREFIX_TOO_SHORT: (name, prefix) => `_sections.md: Section "${name}" prefix "${prefix}" is too short (min ${MIN_PREFIX_LENGTH} chars)`,
  SECTION_PREFIX_TOO_LONG: (name, prefix) => `_sections.md: Section "${name}" prefix "${prefix}" is too long (max ${MAX_PREFIX_LENGTH} chars)`,
  SECTION_NO_RULES: (name, prefix) => `Section "${name}" (prefix: ${prefix}) has no rule files`,

  // Rule Files
  RULE_MISSING_TITLE: 'Missing required frontmatter field: title',
  RULE_MISSING_IMPACT: 'Missing required frontmatter field: impact',
  RULE_MISSING_TAGS: 'Missing required frontmatter field: tags',
  RULE_INVALID_IMPACT: (impact) => `Invalid impact level: ${impact}. Must be one of: ${IMPACT_LEVELS.join(', ')}`,
  RULE_WRONG_FIRST_TAG: (firstTag, expectedPrefix) => `First tag "${firstTag}" must match category prefix "${expectedPrefix}"`,
  RULE_MISSING_INCORRECT: 'Missing "**Incorrect" code example section',
  RULE_MISSING_CORRECT: 'Missing "**Correct" code example section',
  RULE_INSUFFICIENT_CODE_BLOCKS: (count) => `Expected at least 2 code examples but found ${Math.floor(count / 2)}`,
  RULE_TITLE_MISMATCH: (frontmatter, h2) => `Frontmatter title "${frontmatter}" doesn't match H2 title "${h2}"`,
  RULE_INCORRECT_NO_DESCRIPTION: 'Incorrect annotation must have descriptive text in parentheses (e.g., "**Incorrect (blocks event loop):**")',
  RULE_CORRECT_NO_DESCRIPTION: 'Correct annotation must have descriptive text in parentheses (e.g., "**Correct (non-blocking):**")',
  RULE_ANNOTATION_TOO_VAGUE: (annotation) => `Annotation "${annotation}" is too vague - describe the problem/benefit specifically`,
  RULE_DUPLICATED_WORDS: (title, word) => `Title "${title}" has duplicated word: "${word}"`,
  RULE_CODE_BLOCK_NO_LANGUAGE: 'Code block must specify language (e.g., ```typescript, ```cpp)',
  RULE_ORPHAN_PREFIX: (file, prefix) => `Rule "${file}" has prefix "${prefix}" not defined in _sections.md`,
  RULE_VAGUE_LANGUAGE: (term) => `Contains vague language: "${term}"`,
  RULE_MARKETING_LANGUAGE: (term) => `Contains marketing language: "${term}"`,
  RULE_UNQUANTIFIED_IMPACT: 'impactDescription should be quantified (e.g., "2-10× improvement")',
  RULE_SHORT_EXPLANATION: (length) => `Rule explanation is too brief (${length} chars, min ${MIN_RULE_EXPLANATION_LENGTH})`,
  RULE_NO_CODE_LANGUAGE: 'Code block missing language specifier',
  RULE_TITLE_NOT_IMPERATIVE: (title) => `Title "${title}" should start with imperative verb (Avoid, Use, Cache, etc.)`,

  // Code Examples
  RULE_GENERIC_NAME: (term) => `Code example contains generic name "${term}" - use domain-realistic names instead`,
  RULE_EXAMPLE_TOO_SHORT: (lines) => `Code example is very short (${lines} lines) - may be incomplete`,
  RULE_EXAMPLE_TOO_LONG: (lines) => `Code example is too long (${lines} lines, max ${MAX_EXAMPLE_LINES}) - consider splitting`,
  RULE_SYNTAX_COMMENT: (term) => `Code comment explains syntax ("${term}") instead of consequence - describe WHY it matters`,
  RULE_COMMENT_IMBALANCE: 'Correct example has more comments than Incorrect - correct code should be self-explanatory',
  RULE_COULD_BE_SPLIT: (length) => `Rule content is quite long (${length} chars), consider splitting into related rules`,

  // AGENTS.md
  AGENTS_MISSING_ABSTRACT: 'AGENTS.md: Missing "## Abstract" section',
  AGENTS_MISSING_TOC: 'AGENTS.md: Missing "## Table of Contents" section',
  AGENTS_MISSING_REFERENCES: 'AGENTS.md: Missing "## References" section',
  AGENTS_TOC_INCOMPLETE: (missingCount) => `AGENTS.md: Table of Contents is incomplete - missing ${missingCount} subsection(s)`,
  AGENTS_NOTE_NOT_SPECIFIC: 'AGENTS.md: Note block must mention specific technology context (not just "codebases")',
  AGENTS_MISSING_NOTE: 'AGENTS.md: Missing "> **Note:**" block explaining AI/LLM audience',
  AGENTS_NOT_FOUND: 'AGENTS.md not found - run build script to generate',

  // README.md
  README_MISSING_SECTION: (section) => `README.md: Missing required section: "${section}"`,
  README_MISSING_COMMAND: (cmd) => `README.md: Getting Started section missing command: "${cmd}"`,
  HEADING_DUPLICATED_WORDS: (heading, word) => `Heading "${heading}" has duplicated word: "${word}"`,

  // Statistics
  LOW_QUANTIFIED_PERCENT: (percent) => `Only ${percent}% of rules have quantified impact (target: >${TARGET_QUANTIFIED_PERCENT}%)`,
  TOO_FEW_RULES: (count) => `Only ${count} rules found (minimum: ${MIN_RULE_COUNT})`,
  TOO_MANY_RULES_IN_CATEGORY: (name, count) => `Category "${name}" has ${count} rules (maximum: ${MAX_RULES_PER_CATEGORY})`,

  // Guidance
  GUIDE_QUANTIFIED_IMPACT: 'Use quantified metrics like "2-10× improvement", "200ms savings", "O(n) to O(1)", or "prevents stale closures"',
  GUIDE_VAGUE_LANGUAGE: 'Replace vague terms with specific, actionable guidance. Instead of "consider using", say "Use X when Y"',
  GUIDE_CODE_EXAMPLES: 'Each rule needs "**Incorrect (annotation):**" and "**Correct (annotation):**" sections with code blocks',
  GUIDE_FIRST_TAG: 'The first tag must match the rule file prefix (e.g., async-foo.md → first tag "async")',
  GUIDE_KEBAB_CASE: 'Use lowercase letters and hyphens only (e.g., "react-best-practices")',
  GUIDE_IMPACT_LEVELS: `Valid impact levels: ${IMPACT_LEVELS.join(', ')}`,
  GUIDE_IMPACT_ORDERING: 'Categories should be ordered by impact: CRITICAL first, then HIGH, MEDIUM-HIGH, MEDIUM, LOW-MEDIUM, LOW',
  GUIDE_REQUIRED_FILES: 'A complete skill requires: SKILL.md, metadata.json, references/_sections.md (or rules/_sections.md)',
  GUIDE_SKILL_STRUCTURE: 'See QUALITY_CHECKLIST.md in the dev-skill plugin references/ directory for complete skill structure requirements',
};

// Required files and sections for a complete skill
// Note: _sections.md location is validated dynamically (references/ or rules/)
const REQUIRED_FILES = ['SKILL.md', 'metadata.json'];

// Discipline-specific required sections
const REQUIRED_SKILL_SECTIONS_BY_DISCIPLINE = {
  distillation: ['When to Apply', 'Rule Categories', 'Quick Reference'],
  composition: ['When to Apply', 'Workflow Overview'],
  investigation: ['When to Apply', 'Common Symptoms'],
  extraction: ['When to Apply', 'Available Templates'],
};
// Default for backwards compatibility
const REQUIRED_SKILL_SECTIONS = REQUIRED_SKILL_SECTIONS_BY_DISCIPLINE.distillation;

const REQUIRED_METADATA_FIELDS = ['version', 'organization', 'date', 'abstract', 'references'];

const REQUIRED_README_SECTIONS = [
  { name: 'Overview', patterns: [/^#+\s*(?:Overview|Structure)/mi] },
  { name: 'Getting Started', patterns: [/^#+\s*Getting Started/mi] },
  { name: 'Creating a New Rule', patterns: [/^#+\s*Creating a New Rule/mi] },
  { name: 'Rule File Structure', patterns: [/^#+\s*Rule File Structure/mi] },
  { name: 'File Naming Convention', patterns: [/^#+\s*File Naming Convention/mi] },
  { name: 'Impact Levels', patterns: [/^#+\s*Impact Levels/mi] },
  { name: 'Scripts', patterns: [/^#+\s*Scripts/mi] },
  { name: 'Contributing', patterns: [/^#+\s*Contributing/mi] },
];

const REQUIRED_README_COMMANDS = ['pnpm install', 'pnpm build', 'pnpm validate'];

// Vague annotation patterns that are too generic
const VAGUE_ANNOTATION_PATTERNS = [
  /\*\*(?:Incorrect|Correct)\s*\((?:bad|good|wrong|right|better|worse)\)\s*:\*\*/gi,
  /\*\*(?:Incorrect|Correct)\s*\((?:wrong approach|bad approach|better approach|good approach)\)\s*:\*\*/gi,
];

export {
  // Disciplines
  VALID_DISCIPLINES,
  VALID_TYPES,
  REQUIRED_SKILL_SECTIONS_BY_DISCIPLINE,

  // Thresholds
  MIN_PURPOSE_LENGTH,
  MIN_RULE_EXPLANATION_LENGTH,
  MIN_SECTION_DESCRIPTION_LENGTH,
  MIN_ABSTRACT_LENGTH,
  MIN_SKILL_DESCRIPTION_LENGTH,
  MAX_SKILL_MD_LINES,
  MIN_SKILL_MD_LINES,
  MIN_RULE_COUNT,
  MAX_RULE_COUNT,
  MAX_RULES_PER_CATEGORY,
  TARGET_QUANTIFIED_PERCENT,
  MIN_CODE_BLOCKS_PER_RULE,
  MIN_PREFIX_LENGTH,
  MAX_PREFIX_LENGTH,
  MIN_EXAMPLE_LINES,
  MAX_EXAMPLE_LINES,
  RECOMMENDED_MAX_EXAMPLE_LINES,
  TAG_ALIAS_MAP,

  // Impact
  IMPACT_LEVELS,
  IMPACT_LEVELS_SET,
  IMPACT_ORDER,

  // Patterns
  VAGUE_PATTERNS,
  MARKETING_PATTERNS,
  QUANTIFIED_PATTERNS,
  VALID_TITLE_PATTERNS,
  GENERIC_NAME_PATTERNS,
  SYNTAX_COMMENT_PATTERNS,

  // Messages
  VALIDATION_MESSAGES,

  // Required items
  REQUIRED_FILES,
  REQUIRED_SKILL_SECTIONS,
  REQUIRED_METADATA_FIELDS,
  REQUIRED_README_SECTIONS,
  REQUIRED_README_COMMANDS,
  VAGUE_ANNOTATION_PATTERNS,
};
