/**
 * Validation Schemas
 *
 * Schema validation functions for skill components.
 */

import {
  IMPACT_LEVELS_SET,
  IMPACT_ORDER,
  MIN_SKILL_DESCRIPTION_LENGTH,
  MIN_ABSTRACT_LENGTH,
  MIN_PREFIX_LENGTH,
  MAX_PREFIX_LENGTH,
  MIN_SECTION_DESCRIPTION_LENGTH,
  MIN_RULE_EXPLANATION_LENGTH,
  MAX_EXAMPLE_LINES,
  TAG_ALIAS_MAP,
  VALIDATION_MESSAGES,
  VAGUE_PATTERNS,
  MARKETING_PATTERNS,
  QUANTIFIED_PATTERNS,
  VALID_TITLE_PATTERNS,
  VAGUE_ANNOTATION_PATTERNS,
  GENERIC_NAME_PATTERNS,
  REQUIRED_README_SECTIONS,
  REQUIRED_README_COMMANDS,
} from './constants.js';
import { createError, createWarning } from './types.js';
import { extractCodeBlocksWithContext } from './markdown-parser.js';

// Regex patterns for validation
const KEBAB_CASE_REGEX = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;
const SEMVER_REGEX = /^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?(?:\+[a-zA-Z0-9.]+)?$/;
const H1_REGEX = /^#\s+(.+)$/m;
const H2_REGEX = /^## (.+)/m;
const INCORRECT_ANNOTATION_REGEX = /\*\*Incorrect(\s*\([^)]*(?:\([^)]*\)[^)]*)*\))?\s*:\*\*/i;
const CORRECT_ANNOTATION_REGEX = /\*\*Correct(\s*\([^)]*(?:\([^)]*\)[^)]*)*\))?\s*:\*\*/i;
const CODE_FENCE_REGEX = /```/g;
const CODE_FENCE_WITH_LANG_REGEX = /^```[a-zA-Z]+/gm;
const CODE_FENCE_OPENING_REGEX = /^```/gm;
const EXPLANATION_REGEX = /^## .+\n+([^#\n][^\n]+)/m;
const TOC_SECTION_REGEX = /## Table of Contents\n([\s\S]*?)(?=\n##[^#]|\n---|\n$)/;
const NOTE_BLOCK_REGEX = />\s*\*\*Note:\*\*\s*([^\n]+)/i;
const WHITESPACE_SPLIT_REGEX = /\s+/;

function isKebabCase(str) {
  return KEBAB_CASE_REGEX.test(str);
}

function isSemVer(str) {
  return SEMVER_REGEX.test(str);
}

function getFirstLine(content) {
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      return trimmed;
    }
  }
  return null;
}

/**
 * Validate SKILL.md frontmatter
 * @param {Object} frontmatter - Parsed frontmatter object
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateSkillFrontmatter(frontmatter, filepath) {
  const issues = [];

  // Required: name
  if (!frontmatter.name) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.SKILL_MISSING_NAME));
  } else if (!isKebabCase(frontmatter.name)) {
    issues.push(createError(filepath,
      `${VALIDATION_MESSAGES.SKILL_NAME_NOT_KEBAB}. ${VALIDATION_MESSAGES.GUIDE_KEBAB_CASE}`
    ));
  }

  // Required: description
  if (!frontmatter.description) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.SKILL_MISSING_DESCRIPTION));
  } else if (frontmatter.description.length < MIN_SKILL_DESCRIPTION_LENGTH) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.SKILL_DESCRIPTION_TOO_SHORT));
  }

  return issues;
}

/**
 * Validate metadata.json content
 * @param {Object} metadata - Parsed metadata object
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateMetadata(metadata, filepath) {
  const issues = [];

  // Required: version (semver format)
  if (!metadata.version) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.METADATA_MISSING_FIELD('version')));
  } else if (!isSemVer(metadata.version)) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.METADATA_INVALID_VERSION));
  }

  // Required: organization
  if (!metadata.organization) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.METADATA_MISSING_FIELD('organization')));
  }

  // Required: date
  if (!metadata.date) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.METADATA_MISSING_FIELD('date')));
  }

  // Required: abstract (min length)
  if (!metadata.abstract) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.METADATA_MISSING_FIELD('abstract')));
  } else if (metadata.abstract.length < MIN_ABSTRACT_LENGTH) {
    issues.push(createWarning(filepath, VALIDATION_MESSAGES.METADATA_ABSTRACT_TOO_SHORT));
  }

  // Required: references (array)
  if (!metadata.references) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.METADATA_MISSING_FIELD('references')));
  } else if (!Array.isArray(metadata.references)) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.METADATA_REFERENCES_NOT_ARRAY));
  } else if (metadata.references.length === 0) {
    issues.push(createWarning(filepath, VALIDATION_MESSAGES.METADATA_EMPTY_REFERENCES));
  }

  return issues;
}

/**
 * Validate a single section definition
 * @param {import('./types.js').Section} section - Section to validate
 * @param {number} expectedIndex - Expected section index
 * @param {import('./types.js').Section|null} prevSection - Previous section for ordering
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateSection(section, expectedIndex, prevSection, filepath) {
  const issues = [];

  // Check index is sequential
  if (section.index !== expectedIndex) {
    issues.push(createError(filepath,
      VALIDATION_MESSAGES.SECTION_NUMBERING_GAP(section.name, expectedIndex, section.index)
    ));
  }

  if (!IMPACT_LEVELS_SET.has(section.impact)) {
    issues.push(createError(filepath,
      `${VALIDATION_MESSAGES.SECTION_INVALID_IMPACT(section.name, section.impact)}. ${VALIDATION_MESSAGES.GUIDE_IMPACT_LEVELS}`
    ));
  }

  // Check prefix length
  if (section.prefix.length < MIN_PREFIX_LENGTH) {
    issues.push(createError(filepath,
      VALIDATION_MESSAGES.SECTION_PREFIX_TOO_SHORT(section.name, section.prefix)
    ));
  }
  if (section.prefix.length > MAX_PREFIX_LENGTH) {
    issues.push(createError(filepath,
      VALIDATION_MESSAGES.SECTION_PREFIX_TOO_LONG(section.name, section.prefix)
    ));
  }

  // Check description exists
  if (!section.description || section.description.length < MIN_SECTION_DESCRIPTION_LENGTH) {
    issues.push(createWarning(filepath,
      `Section "${section.name}" has a brief or missing description`
    ));
  }

  return issues;
}

/**
 * Validate impact ordering across sections
 * @param {import('./types.js').Section[]} sections - All sections
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateImpactOrdering(sections, filepath) {
  const issues = [];

  let lastOrder = -1;
  let lastSection = null;

  for (const section of sections) {
    const order = IMPACT_ORDER[section.impact];
    if (order !== undefined && order < lastOrder) {
      issues.push(createError(filepath,
        `${VALIDATION_MESSAGES.SECTION_IMPACT_ORDER(section.name, lastSection?.name)}. ${VALIDATION_MESSAGES.GUIDE_IMPACT_ORDERING}`
      ));
    }
    if (order !== undefined) {
      lastOrder = order;
      lastSection = section;
    }
  }

  return issues;
}

/**
 * Validate rule file frontmatter
 * @param {Object} frontmatter - Parsed frontmatter object
 * @param {string} expectedPrefix - Expected first tag (category prefix)
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateRuleFrontmatter(frontmatter, expectedPrefix, filepath) {
  const issues = [];

  // Required: title
  if (!frontmatter.title) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.RULE_MISSING_TITLE));
  }

  if (!frontmatter.impact) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.RULE_MISSING_IMPACT));
  } else if (!IMPACT_LEVELS_SET.has(frontmatter.impact)) {
    issues.push(createError(filepath,
      `${VALIDATION_MESSAGES.RULE_INVALID_IMPACT(frontmatter.impact)}. ${VALIDATION_MESSAGES.GUIDE_IMPACT_LEVELS}`
    ));
  }

  // Required: tags (first must match prefix or be an alias)
  if (!frontmatter.tags) {
    issues.push(createError(filepath,
      `${VALIDATION_MESSAGES.RULE_MISSING_TAGS}. ${VALIDATION_MESSAGES.GUIDE_FIRST_TAG}`
    ));
  } else {
    const firstTag = frontmatter.tags.split(',')[0].trim();
    if (expectedPrefix) {
      // Check if first tag matches prefix directly or via alias
      const aliasedPrefix = TAG_ALIAS_MAP[firstTag];
      const matches = firstTag === expectedPrefix || aliasedPrefix === expectedPrefix;
      if (!matches) {
        issues.push(createError(filepath,
          `${VALIDATION_MESSAGES.RULE_WRONG_FIRST_TAG(firstTag, expectedPrefix)}. ${VALIDATION_MESSAGES.GUIDE_FIRST_TAG}`
        ));
      }
    }
  }

  // Optional but recommended: impactDescription (should be quantified)
  if (frontmatter.impactDescription) {
    const isQuantified = QUANTIFIED_PATTERNS.some(p => p.test(frontmatter.impactDescription));
    if (!isQuantified) {
      issues.push(createWarning(filepath,
        `${VALIDATION_MESSAGES.RULE_UNQUANTIFIED_IMPACT}. ${VALIDATION_MESSAGES.GUIDE_QUANTIFIED_IMPACT}`
      ));
    }
  }

  return issues;
}

/**
 * Validate rule content structure
 * @param {string} body - Rule content after frontmatter
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateRuleContent(body, filepath) {
  const issues = [];

  // Check for example patterns - rules can use:
  // 1. **Incorrect (desc):** + **Correct (desc):** pair
  // 2. **Example (desc):** or **Usage:** for single-example rules
  // 3. **CSS:** or **Implementation:** for implementation-only rules
  const incorrectMatch = body.match(INCORRECT_ANNOTATION_REGEX);
  const correctMatch = body.match(CORRECT_ANNOTATION_REGEX);
  const hasExamplePattern = /\*\*Example\s*(?:\([^)]+\))?\s*:\*\*/i.test(body);
  const hasUsagePattern = /\*\*Usage\s*:\*\*/i.test(body);
  const hasCSSPattern = /\*\*CSS\s*:\*\*/i.test(body);
  const hasImplementationPattern = /\*\*Implementation\s*:\*\*/i.test(body);
  const hasAltEmoji = body.includes('**❌') || body.includes('**✓') || body.includes('**✅');
  const hasAlternativePattern = hasExamplePattern || hasUsagePattern || hasCSSPattern || hasImplementationPattern;

  // If using Incorrect/Correct pattern, validate the pair
  if (incorrectMatch || correctMatch) {
    if (!incorrectMatch && !hasAltEmoji) {
      issues.push(createError(filepath,
        `${VALIDATION_MESSAGES.RULE_MISSING_INCORRECT}. ${VALIDATION_MESSAGES.GUIDE_CODE_EXAMPLES}`
      ));
    } else if (incorrectMatch && !incorrectMatch[1]) {
      issues.push(createError(filepath, VALIDATION_MESSAGES.RULE_INCORRECT_NO_DESCRIPTION));
    }

    if (!correctMatch && !hasAltEmoji) {
      issues.push(createError(filepath,
        `${VALIDATION_MESSAGES.RULE_MISSING_CORRECT}. ${VALIDATION_MESSAGES.GUIDE_CODE_EXAMPLES}`
      ));
    } else if (correctMatch && !correctMatch[1]) {
      issues.push(createError(filepath, VALIDATION_MESSAGES.RULE_CORRECT_NO_DESCRIPTION));
    }
  } else if (!hasAlternativePattern && !hasAltEmoji) {
    // No recognized example pattern found
    issues.push(createError(filepath,
      `${VALIDATION_MESSAGES.RULE_MISSING_INCORRECT}. ${VALIDATION_MESSAGES.GUIDE_CODE_EXAMPLES}`
    ));
  }

  for (const pattern of VAGUE_ANNOTATION_PATTERNS) {
    pattern.lastIndex = 0;
    const vagueMatch = body.match(pattern);
    if (vagueMatch) {
      issues.push(createError(filepath, VALIDATION_MESSAGES.RULE_ANNOTATION_TOO_VAGUE(vagueMatch[0])));
    }
  }

  CODE_FENCE_REGEX.lastIndex = 0;
  const codeBlockMatches = body.match(CODE_FENCE_REGEX) || [];
  if (codeBlockMatches.length < 2) { // At least 1 code block = 2 ``` markers
    issues.push(createError(filepath,
      VALIDATION_MESSAGES.RULE_INSUFFICIENT_CODE_BLOCKS(codeBlockMatches.length)
    ));
  }

  CODE_FENCE_WITH_LANG_REGEX.lastIndex = 0;
  const fencesWithLang = (body.match(CODE_FENCE_WITH_LANG_REGEX) || []).length;
  CODE_FENCE_OPENING_REGEX.lastIndex = 0;
  const totalFences = (body.match(CODE_FENCE_OPENING_REGEX) || []).length;
  const expectedOpeningFences = Math.floor(totalFences / 2);
  const openingWithoutLang = expectedOpeningFences - fencesWithLang;
  if (openingWithoutLang > 0) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.RULE_CODE_BLOCK_NO_LANGUAGE));
  }

  return issues;
}

/**
 * Validate rule language quality
 * @param {string} body - Rule content after frontmatter
 * @param {string} title - Rule title for pattern checking
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateRuleLanguage(body, title, filepath) {
  const issues = [];

  for (const { pattern, term } of VAGUE_PATTERNS) {
    pattern.lastIndex = 0;
    if (pattern.test(body)) {
      issues.push(createWarning(filepath,
        `${VALIDATION_MESSAGES.RULE_VAGUE_LANGUAGE(term)}. ${VALIDATION_MESSAGES.GUIDE_VAGUE_LANGUAGE}`
      ));
    }
  }

  for (const { pattern, term } of MARKETING_PATTERNS) {
    pattern.lastIndex = 0;
    if (pattern.test(body)) {
      issues.push(createWarning(filepath,
        VALIDATION_MESSAGES.RULE_MARKETING_LANGUAGE(term)
      ));
    }
  }

  if (title) {
    const hasImperativeTitle = VALID_TITLE_PATTERNS.some(p => p.test(title));
    if (!hasImperativeTitle) {
      issues.push(createWarning(filepath,
        VALIDATION_MESSAGES.RULE_TITLE_NOT_IMPERATIVE(title)
      ));
    }
  }

  const explanationMatch = body.match(EXPLANATION_REGEX);
  if (explanationMatch) {
    const explanation = explanationMatch[1].trim();
    if (explanation.length < MIN_RULE_EXPLANATION_LENGTH) {
      issues.push(createWarning(filepath,
        VALIDATION_MESSAGES.RULE_SHORT_EXPLANATION(explanation.length)
      ));
    }
  }

  return issues;
}

/**
 * Extract code blocks from markdown content using AST parser
 * @param {string} content - Markdown content
 * @returns {Array<{code: string, lines: number, isIncorrect: boolean, isCorrect: boolean, isWarning: boolean}>}
 */
function extractCodeBlocks(content) {
  const astBlocks = extractCodeBlocksWithContext(content);

  return astBlocks.map(block => ({
    code: block.code,
    lines: block.code.split('\n').filter(l => l.trim()).length,
    isIncorrect: block.isIncorrect,
    isCorrect: block.isCorrect,
    // Check if annotation description includes 'warning' for Warning blocks
    isWarning: block.annotation?.description?.toLowerCase().includes('warning') || false
  }));
}

/**
 * Count comment lines in code
 * @param {string} code - Code content
 * @returns {number}
 */
function countComments(code) {
  const lines = code.split('\n');
  let count = 0;
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('//') || trimmed.startsWith('/*') || trimmed.startsWith('*')) {
      count++;
    }
  }
  return count;
}

/**
 * Strip comments from code to avoid false positives in generic name detection.
 * Handles single-line (//) and multi-line (/* *​/) style comments.
 * @param {string} code - Code content
 * @returns {string} - Code with comments removed
 */
function stripComments(code) {
  // Remove single-line comments
  let stripped = code.replace(/\/\/.*$/gm, '');
  // Remove multi-line comments (non-greedy)
  stripped = stripped.replace(/\/\*[\s\S]*?\*\//g, '');
  // Remove JSDoc-style comments
  stripped = stripped.replace(/\/\*\*[\s\S]*?\*\//g, '');
  return stripped;
}

/**
 * Strip string literals from code to avoid false positives.
 * Handles single quotes, double quotes, and template literals.
 * @param {string} code - Code content
 * @returns {string} - Code with string literals removed
 */
function stripStrings(code) {
  // Remove template literals (backticks) - non-greedy
  let stripped = code.replace(/`[^`]*`/g, '""');
  // Remove double-quoted strings
  stripped = stripped.replace(/"(?:[^"\\]|\\.)*"/g, '""');
  // Remove single-quoted strings
  stripped = stripped.replace(/'(?:[^'\\]|\\.)*'/g, "''");
  return stripped;
}

/**
 * Validate code example quality
 * @param {string} body - Rule content after frontmatter
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateCodeExampleQuality(body, filepath) {
  const issues = [];
  const codeBlocks = extractCodeBlocks(body);

  let incorrectComments = 0;
  let correctComments = 0;
  let incorrectBlockCount = 0;
  let correctBlockCount = 0;

  for (const block of codeBlocks) {
    // Skip generic name and syntax comment checks for Warning blocks
    // Warning blocks may contain demo code (like "foo") for illustration
    const isMainExample = block.isIncorrect || block.isCorrect;

    // Check for generic names in code (only in main Incorrect/Correct examples)
    // Strip comments and strings first to reduce false positives
    if (isMainExample) {
      const codeForCheck = stripStrings(stripComments(block.code));
      for (const { pattern, term } of GENERIC_NAME_PATTERNS) {
        pattern.lastIndex = 0;
        if (pattern.test(codeForCheck)) {
          issues.push(createWarning(filepath, VALIDATION_MESSAGES.RULE_GENERIC_NAME(term)));
          break; // Only report first generic name per block
        }
      }
    }

    // Check line count
    if (block.lines > MAX_EXAMPLE_LINES) {
      issues.push(createWarning(filepath, VALIDATION_MESSAGES.RULE_EXAMPLE_TOO_LONG(block.lines)));
    }

    // Track comments for balance check
    const comments = countComments(block.code);
    if (block.isIncorrect) {
      incorrectComments += comments;
      incorrectBlockCount++;
    } else if (block.isCorrect) {
      correctComments += comments;
      correctBlockCount++;
    }

    // Note: Syntax comment checks and comment balance checks are disabled
    // These are too noisy and context-dependent for automated validation
    // They're documented in QUALITY_CHECKLIST.md for manual review
  }

  return issues;
}

/**
 * Validate frontmatter title matches H2 in body
 * @param {string} frontmatterTitle - Title from frontmatter
 * @param {string} body - Rule content
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateTitleMatch(frontmatterTitle, body, filepath) {
  const issues = [];

  if (!frontmatterTitle) return issues;

  const h2Match = body.match(H2_REGEX);
  if (h2Match) {
    const h2Title = h2Match[1].trim();
    if (frontmatterTitle !== h2Title) {
      issues.push(createWarning(filepath,
        VALIDATION_MESSAGES.RULE_TITLE_MISMATCH(frontmatterTitle, h2Title)
      ));
    }
  }

  return issues;
}

/**
 * Check for duplicated consecutive words in a string
 * @param {string} text - Text to check
 * @returns {string|null} - The duplicated word or null
 */
function findDuplicatedWord(text) {
  const words = text.toLowerCase().split(WHITESPACE_SPLIT_REGEX);
  for (let i = 1; i < words.length; i++) {
    if (words[i] === words[i - 1] && words[i].length > 2) {
      return words[i];
    }
  }
  return null;
}

/**
 * Validate no duplicated words in title
 * @param {string} title - Title to check
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateNoDuplicatedWords(title, filepath) {
  const issues = [];
  if (!title) return issues;

  const duplicated = findDuplicatedWord(title);
  if (duplicated) {
    issues.push(createError(filepath,
      VALIDATION_MESSAGES.RULE_DUPLICATED_WORDS(title, duplicated)
    ));
  }

  return issues;
}

/**
 * Validate SKILL.md H1 format includes organization name
 * @param {string} content - Full SKILL.md content
 * @param {string} organization - Organization name from metadata
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateSkillH1Format(content, organization, filepath) {
  const issues = [];

  const h1Match = content.match(H1_REGEX);
  if (!h1Match) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.SKILL_H1_MISSING));
    return issues;
  }

  const h1 = h1Match[1].trim();

  // H1 should include "Best Practices" and ideally the organization name
  if (!h1.includes('Best Practices')) {
    issues.push(createError(filepath, VALIDATION_MESSAGES.SKILL_H1_WRONG_FORMAT(h1)));
  } else if (organization) {
    // Check if H1 includes org name or first word of org name (e.g., "Vercel" matches "Vercel Engineering")
    const orgWords = organization.split(/\s+/);
    const h1Lower = h1.toLowerCase();
    const hasOrgReference = orgWords.some(word => h1Lower.includes(word.toLowerCase()));
    if (!hasOrgReference) {
      issues.push(createWarning(filepath,
        `SKILL.md: H1 "${h1}" should include organization name "${organization}"`
      ));
    }
  }

  return issues;
}

/**
 * Validate README.md has required sections
 * @param {string} content - README.md content
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateReadmeSections(content, filepath) {
  const issues = [];

  // Check required sections
  for (const section of REQUIRED_README_SECTIONS) {
    const found = section.patterns.some(p => p.test(content));
    if (!found) {
      issues.push(createError(filepath, VALIDATION_MESSAGES.README_MISSING_SECTION(section.name)));
    }
  }

  // Check required commands in Getting Started
  for (const cmd of REQUIRED_README_COMMANDS) {
    if (!content.includes(cmd)) {
      issues.push(createError(filepath, VALIDATION_MESSAGES.README_MISSING_COMMAND(cmd)));
    }
  }

  return issues;
}

/**
 * Validate AGENTS.md TOC completeness
 * @param {string} content - AGENTS.md content
 * @param {import('./types.js').Section[]} sections - Expected sections
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateAgentsTocCompleteness(content, sections, filepath) {
  const issues = [];

  // Extract TOC section
  const tocMatch = content.match(TOC_SECTION_REGEX);
  if (!tocMatch) return issues;

  const toc = tocMatch[1];

  // Check each section is in TOC
  for (const section of sections) {
    if (!toc.includes(section.name)) {
      issues.push(createError(filepath,
        VALIDATION_MESSAGES.AGENTS_TOC_INCOMPLETE(1) + ` - missing "${section.name}"`
      ));
    }
  }

  return issues;
}

/**
 * Validate AGENTS.md Note block mentions specific technology
 * @param {string} content - AGENTS.md content
 * @param {string} technology - Technology name from metadata
 * @param {string} filepath - Path for error reporting
 * @returns {import('./types.js').ValidationIssue[]}
 */
function validateAgentsNoteSpecific(content, technology, filepath) {
  const issues = [];

  // Find the Note block
  const noteMatch = content.match(NOTE_BLOCK_REGEX);
  if (!noteMatch) return issues;

  const noteText = noteMatch[1].toLowerCase();

  // Should mention specific technology, not just "codebases"
  if (noteText.includes('codebases') && !technology) {
    issues.push(createWarning(filepath, VALIDATION_MESSAGES.AGENTS_NOTE_NOT_SPECIFIC));
  } else if (technology && !noteText.includes(technology.toLowerCase())) {
    issues.push(createWarning(filepath,
      `AGENTS.md: Note block should mention "${technology}" specifically`
    ));
  }

  return issues;
}

export {
  isKebabCase,
  isSemVer,
  getFirstLine,
  findDuplicatedWord,
  validateSkillFrontmatter,
  validateMetadata,
  validateSection,
  validateImpactOrdering,
  validateRuleFrontmatter,
  validateRuleContent,
  validateRuleLanguage,
  validateCodeExampleQuality,
  validateTitleMatch,
  validateNoDuplicatedWords,
  validateSkillH1Format,
  validateReadmeSections,
  validateAgentsTocCompleteness,
  validateAgentsNoteSpecific,
};
