/**
 * Skill Validator
 *
 * Core validation class for performance best practices skills.
 */

import fs from 'fs';
import path from 'path';
import { extractFrontmatter, extractBody } from './markdown-parser.js';
import {
  REQUIRED_FILES,
  REQUIRED_SKILL_SECTIONS,
  VALIDATION_MESSAGES,
  MIN_SKILL_MD_LINES,
  MAX_SKILL_MD_LINES,
  MIN_RULE_COUNT,
  MAX_RULES_PER_CATEGORY,
  TARGET_QUANTIFIED_PERCENT,
  QUANTIFIED_PATTERNS,
} from './constants.js';
import { createError, createWarning, createReport } from './types.js';
import {
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
} from './schemas.js';

const SECTION_HEADER_REGEX = /^## (\d+)\. (.+) \(([a-z]+)\)/;
const IMPACT_REGEX = /^\*\*Impact:\*\* (.+)/;
const DESCRIPTION_REGEX = /^\*\*Description:\*\* (.+)/;
const RULE_FILE_REGEX = /^[a-z]+-.*\.md$/;

/**
 * Parse YAML frontmatter from markdown content
 * @param {string} content - Markdown content
 * @returns {{frontmatter: Object, body: string}}
 */
function parseFrontmatter(content) {
  return {
    frontmatter: extractFrontmatter(content) || {},
    body: extractBody(content)
  };
}

/**
 * Get files matching a pattern in a directory
 * @param {string} dir - Directory path
 * @param {RegExp} pattern - Pattern to match
 * @returns {string[]}
 */
function getFiles(dir, pattern) {
  if (!fs.existsSync(dir)) return [];
  const files = fs.readdirSync(dir);
  const result = [];
  for (const f of files) {
    if (pattern.test(f)) {
      result.push(f);
      pattern.lastIndex = 0;
    }
  }
  return result;
}

/**
 * Parse sections from _sections.md content
 * @param {string} content - Content of _sections.md
 * @returns {import('./types.js').Section[]}
 */
function parseSections(content) {
  const sections = [];
  const lines = content.split('\n');
  let currentSection = null;

  for (const line of lines) {
    // Match: ## 1. Category Name (prefix)
    const sectionMatch = line.match(SECTION_HEADER_REGEX);
    if (sectionMatch) {
      if (currentSection) sections.push(currentSection);
      currentSection = {
        index: parseInt(sectionMatch[1]),
        name: sectionMatch[2],
        prefix: sectionMatch[3],
        impact: '',
        description: ''
      };
      continue;
    }

    if (currentSection) {
      // Match: **Impact:** CRITICAL
      const impactMatch = line.match(IMPACT_REGEX);
      if (impactMatch) {
        currentSection.impact = impactMatch[1].trim();
        continue;
      }

      // Match: **Description:** text
      const descMatch = line.match(DESCRIPTION_REGEX);
      if (descMatch) {
        currentSection.description = descMatch[1].trim();
        continue;
      }
    }
  }

  if (currentSection) sections.push(currentSection);
  return sections;
}

class SkillValidator {
  /**
   * @param {boolean} strictMode - Treat warnings as errors
   */
  constructor(strictMode = false) {
    this.strictMode = strictMode;
  }

  /**
   * Validate a complete skill directory
   * @param {string} skillDir - Path to skill directory
   * @returns {Promise<import('./types.js').ValidationReport>}
   */
  async validateSkill(skillDir) {
    const issues = [];

    const metadata = this.loadMetadata(skillDir);

    issues.push(...this.validateRequiredFiles(skillDir));
    issues.push(...this.validateMetadataFile(skillDir));
    issues.push(...this.validateSkillMd(skillDir, metadata));
    issues.push(...this.validateReadmeMd(skillDir));

    const sections = this.parseSectionsFile(skillDir);
    issues.push(...this.validateSectionsFile(skillDir, sections));
    const ruleStats = this.validateRulesDir(skillDir, sections, issues);
    issues.push(...this.validateAgentsMd(skillDir, sections, metadata));

    issues.push(...this.validateCrossReferences(skillDir, sections, ruleStats));

    issues.push(...this.validateStatistics(ruleStats));

    return createReport(issues, this.strictMode);
  }

  /**
   * Validate only _sections.md for incremental generation workflow.
   * Use this to fail fast before generating individual rules.
   * @param {string} skillDir - Path to skill directory
   * @returns {Promise<import('./types.js').ValidationReport>}
   */
  async validateSectionsOnly(skillDir) {
    const issues = [];

    // Check if references/ or rules/ directory exists (references/ preferred)
    const referencesDir = path.join(skillDir, 'references');
    const rulesDir = path.join(skillDir, 'rules');
    const refDir = fs.existsSync(referencesDir) ? referencesDir : rulesDir;
    const refDirName = fs.existsSync(referencesDir) ? 'references' : 'rules';

    if (!fs.existsSync(refDir)) {
      issues.push(createError('structure', 'references/ or rules/ directory not found'));
      return createReport(issues, this.strictMode);
    }

    // Check if _sections.md exists
    const sectionsPath = path.join(refDir, '_sections.md');
    if (!fs.existsSync(sectionsPath)) {
      issues.push(createError(`${refDirName}/_sections.md`, 'File not found'));
      return createReport(issues, this.strictMode);
    }

    // Parse and validate sections
    const sections = this.parseSectionsFile(skillDir);
    issues.push(...this.validateSectionsFile(skillDir, sections));

    return createReport(issues, this.strictMode);
  }

  /**
   * Load metadata from metadata.json
   * @param {string} skillDir
   * @returns {Object|null}
   */
  loadMetadata(skillDir) {
    const filepath = path.join(skillDir, 'metadata.json');
    if (!fs.existsSync(filepath)) return null;

    try {
      const content = fs.readFileSync(filepath, 'utf-8');
      return JSON.parse(content);
    } catch {
      return null;
    }
  }

  /**
   * Validate required files exist
   * @param {string} skillDir
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateRequiredFiles(skillDir) {
    const issues = [];

    // Check base required files
    for (const file of REQUIRED_FILES) {
      const filepath = path.join(skillDir, file);
      if (!fs.existsSync(filepath)) {
        issues.push(createError('structure',
          `${VALIDATION_MESSAGES.MISSING_FILE(file)}. ${VALIDATION_MESSAGES.GUIDE_REQUIRED_FILES}`
        ));
      }
    }

    // Check for _sections.md in references/ or rules/
    const { dir: refDir, name: refDirName } = this.getReferencesDir(skillDir);
    const sectionsPath = path.join(refDir, '_sections.md');
    if (!fs.existsSync(sectionsPath)) {
      issues.push(createError('structure',
        `${VALIDATION_MESSAGES.MISSING_FILE(`${refDirName}/_sections.md`)}. ${VALIDATION_MESSAGES.GUIDE_REQUIRED_FILES}`
      ));
    }

    return issues;
  }

  /**
   * Validate metadata.json
   * @param {string} skillDir
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateMetadataFile(skillDir) {
    const filepath = path.join(skillDir, 'metadata.json');
    if (!fs.existsSync(filepath)) return [];

    try {
      const content = fs.readFileSync(filepath, 'utf-8');
      const metadata = JSON.parse(content);
      return validateMetadata(metadata, 'metadata.json');
    } catch (e) {
      return [createError('metadata.json', VALIDATION_MESSAGES.INVALID_JSON('metadata.json', e.message))];
    }
  }

  /**
   * Validate SKILL.md
   * @param {string} skillDir
   * @param {Object|null} metadata - Loaded metadata for cross-validation
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateSkillMd(skillDir, metadata = null) {
    const filepath = path.join(skillDir, 'SKILL.md');
    if (!fs.existsSync(filepath)) return [];

    const issues = [];
    const content = fs.readFileSync(filepath, 'utf-8');
    const { frontmatter, body } = parseFrontmatter(content);

    // Validate frontmatter
    issues.push(...validateSkillFrontmatter(frontmatter, 'SKILL.md'));

    // Validate H1 format (must include org name and "Best Practices")
    const organization = metadata?.organization || null;
    issues.push(...validateSkillH1Format(content, organization, 'SKILL.md'));

    // Check line count
    const lineCount = content.split('\n').length;
    if (lineCount < MIN_SKILL_MD_LINES) {
      issues.push(createWarning('SKILL.md', VALIDATION_MESSAGES.SKILL_TOO_SHORT(lineCount)));
    }
    if (lineCount > MAX_SKILL_MD_LINES) {
      issues.push(createWarning('SKILL.md', VALIDATION_MESSAGES.SKILL_TOO_LONG(lineCount)));
    }

    // Check required sections
    for (const section of REQUIRED_SKILL_SECTIONS) {
      if (!body.includes(section)) {
        issues.push(createWarning('SKILL.md', VALIDATION_MESSAGES.SKILL_MISSING_SECTION(section)));
      }
    }

    return issues;
  }

  /**
   * Validate README.md
   * @param {string} skillDir
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateReadmeMd(skillDir) {
    const filepath = path.join(skillDir, 'README.md');
    if (!fs.existsSync(filepath)) {
      return [createWarning('README.md', 'README.md not found')];
    }

    const content = fs.readFileSync(filepath, 'utf-8');
    return validateReadmeSections(content, 'README.md');
  }

  /**
   * Get the references directory (references/ or legacy rules/)
   * @param {string} skillDir
   * @returns {{dir: string, name: string}}
   */
  getReferencesDir(skillDir) {
    const referencesDir = path.join(skillDir, 'references');
    const rulesDir = path.join(skillDir, 'rules');
    if (fs.existsSync(referencesDir)) {
      return { dir: referencesDir, name: 'references' };
    }
    return { dir: rulesDir, name: 'rules' };
  }

  /**
   * Parse _sections.md file
   * @param {string} skillDir
   * @returns {import('./types.js').Section[]}
   */
  parseSectionsFile(skillDir) {
    const { dir } = this.getReferencesDir(skillDir);
    const filepath = path.join(dir, '_sections.md');
    if (!fs.existsSync(filepath)) return [];

    const content = fs.readFileSync(filepath, 'utf-8');
    return parseSections(content);
  }

  /**
   * Validate _sections.md content
   * @param {string} skillDir
   * @param {import('./types.js').Section[]} sections
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateSectionsFile(skillDir, sections) {
    const { name: refDirName } = this.getReferencesDir(skillDir);
    const filepath = `${refDirName}/_sections.md`;
    const issues = [];

    if (sections.length === 0) {
      issues.push(createError(filepath, VALIDATION_MESSAGES.NO_SECTIONS_DEFINED));
      return issues;
    }

    // Validate each section
    let prevSection = null;
    for (let i = 0; i < sections.length; i++) {
      issues.push(...validateSection(sections[i], i + 1, prevSection, filepath));
      prevSection = sections[i];
    }

    // Validate impact ordering
    issues.push(...validateImpactOrdering(sections, filepath));

    return issues;
  }

  /**
   * Validate all rule files
   * @param {string} skillDir
   * @param {import('./types.js').Section[]} sections
   * @param {import('./types.js').ValidationIssue[]} issues - Mutated in place
   * @returns {{totalRules: number, quantifiedRules: number, rulesByPrefix: Object}}
   */
  validateRulesDir(skillDir, sections, issues) {
    const { dir: refDir, name: refDirName } = this.getReferencesDir(skillDir);
    const stats = {
      totalRules: 0,
      quantifiedRules: 0,
      rulesByPrefix: {}
    };

    if (!fs.existsSync(refDir)) return stats;

    const prefixMap = new Map();
    for (const section of sections) {
      prefixMap.set(section.prefix, section.name);
      stats.rulesByPrefix[section.prefix] = 0;
    }

    const ruleFiles = getFiles(refDir, RULE_FILE_REGEX)
      .filter(f => !f.startsWith('_'));

    if (ruleFiles.length === 0) {
      issues.push(createError(`${refDirName}/`, VALIDATION_MESSAGES.NO_RULES_FOUND));
      return stats;
    }

    for (const file of ruleFiles) {
      const filepath = path.join(refDir, file);
      const prefix = file.split('-')[0];
      const displayPath = `${refDirName}/${file}`;

      if (sections.length > 0 && !prefixMap.has(prefix)) {
        issues.push(createWarning(displayPath,
          VALIDATION_MESSAGES.RULE_ORPHAN_PREFIX(file, prefix)
        ));
      }

      const { issues: ruleIssues, frontmatter } = this.validateRuleFile(filepath, prefix);
      issues.push(...ruleIssues.map(issue => ({
        ...issue,
        path: displayPath
      })));

      stats.totalRules++;
      if (stats.rulesByPrefix[prefix] !== undefined) {
        stats.rulesByPrefix[prefix]++;
      }

      if (frontmatter.impactDescription) {
        const isQuantified = QUANTIFIED_PATTERNS.some(p => p.test(frontmatter.impactDescription));
        if (isQuantified) stats.quantifiedRules++;
      }
    }

    return stats;
  }

  /**
   * Validate a single rule file
   * @param {string} filepath - Full path to rule file
   * @param {string} expectedPrefix - Expected category prefix
   * @returns {{issues: import('./types.js').ValidationIssue[], frontmatter: Object}}
   */
  validateRuleFile(filepath, expectedPrefix) {
    const issues = [];
    let frontmatter = {};

    try {
      const content = fs.readFileSync(filepath, 'utf-8');
      const parsed = parseFrontmatter(content);
      frontmatter = parsed.frontmatter;
      const body = parsed.body;

      issues.push(...validateRuleFrontmatter(frontmatter, expectedPrefix, filepath));
      issues.push(...validateNoDuplicatedWords(frontmatter.title, filepath));
      issues.push(...validateRuleContent(body, filepath));
      issues.push(...validateRuleLanguage(body, frontmatter.title, filepath));
      issues.push(...validateCodeExampleQuality(body, filepath));
      issues.push(...validateTitleMatch(frontmatter.title, body, filepath));

    } catch (e) {
      issues.push(createError(filepath, `Error reading file: ${e.message}`));
    }

    return { issues, frontmatter };
  }

  /**
   * Validate AGENTS.md
   * @param {string} skillDir
   * @param {import('./types.js').Section[]} sections - Parsed sections for TOC validation
   * @param {Object|null} metadata - Metadata for technology-specific checks
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateAgentsMd(skillDir, sections = [], metadata = null) {
    const filepath = path.join(skillDir, 'AGENTS.md');
    const issues = [];

    if (!fs.existsSync(filepath)) {
      issues.push(createWarning('AGENTS.md', VALIDATION_MESSAGES.AGENTS_NOT_FOUND));
      return issues;
    }

    const content = fs.readFileSync(filepath, 'utf-8');

    if (!content.includes('## Abstract')) {
      issues.push(createError('AGENTS.md', VALIDATION_MESSAGES.AGENTS_MISSING_ABSTRACT));
    }
    if (!content.includes('## Table of Contents')) {
      issues.push(createError('AGENTS.md', VALIDATION_MESSAGES.AGENTS_MISSING_TOC));
    }
    if (!content.includes('## References')) {
      issues.push(createError('AGENTS.md', VALIDATION_MESSAGES.AGENTS_MISSING_REFERENCES));
    }

    if (!content.includes('> **Note:**')) {
      issues.push(createWarning('AGENTS.md', VALIDATION_MESSAGES.AGENTS_MISSING_NOTE));
    }

    if (sections.length > 0) {
      issues.push(...validateAgentsTocCompleteness(content, sections, 'AGENTS.md'));
    }

    const technology = metadata?.technology || null;
    issues.push(...validateAgentsNoteSpecific(content, technology, 'AGENTS.md'));

    return issues;
  }

  /**
   * Validate cross-references between files
   * @param {string} skillDir
   * @param {import('./types.js').Section[]} sections
   * @param {{totalRules: number, rulesByPrefix: Object}} ruleStats
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateCrossReferences(skillDir, sections, ruleStats) {
    const issues = [];

    for (const section of sections) {
      const count = ruleStats.rulesByPrefix[section.prefix] || 0;
      if (count === 0) {
        issues.push(createWarning('cross-reference',
          VALIDATION_MESSAGES.SECTION_NO_RULES(section.name, section.prefix)
        ));
      }
      if (count > MAX_RULES_PER_CATEGORY) {
        issues.push(createWarning('cross-reference',
          VALIDATION_MESSAGES.TOO_MANY_RULES_IN_CATEGORY(section.name, count)
        ));
      }
    }

    return issues;
  }

  /**
   * Validate overall statistics
   * @param {{totalRules: number, quantifiedRules: number}} stats
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateStatistics(stats) {
    const issues = [];

    if (stats.totalRules > 0 && stats.totalRules < MIN_RULE_COUNT) {
      issues.push(createWarning('statistics', VALIDATION_MESSAGES.TOO_FEW_RULES(stats.totalRules)));
    }

    if (stats.totalRules > 0) {
      const percent = Math.round((stats.quantifiedRules / stats.totalRules) * 100);
      if (percent < TARGET_QUANTIFIED_PERCENT) {
        issues.push(createWarning('statistics',
          `${VALIDATION_MESSAGES.LOW_QUANTIFIED_PERCENT(percent)}. ${VALIDATION_MESSAGES.GUIDE_QUANTIFIED_IMPACT}`
        ));
      }
    }

    return issues;
  }
}

export { SkillValidator, parseFrontmatter, parseSections, getFiles };
