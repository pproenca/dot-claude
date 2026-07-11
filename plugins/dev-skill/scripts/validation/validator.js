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
  REQUIRED_SKILL_SECTIONS_BY_DISCIPLINE,
  VALID_DISCIPLINES,
  VALID_TYPES,
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
// Adversarial protocol files live in references/ but are not rules
const ADVERSARIAL_PROTOCOL_FILES = ['reviewer-prompt.md', 'rules-source.md'];

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
    const discipline = this.detectDiscipline(skillDir, metadata);

    // Universal checks (all disciplines)
    issues.push(...this.validateRequiredFiles(skillDir, discipline));
    issues.push(...this.validateMetadataFile(skillDir));
    issues.push(...this.validateSkillMd(skillDir, metadata, discipline));

    // Discipline-specific checks
    if (discipline === 'distillation') {
      // README.md is optional. A skill is a context bundle, not a standalone
      // repo — it does not need an Overview/Getting-Started/Contributing README
      // with build commands. If one exists it is left untouched.
      const sections = this.parseSectionsFile(skillDir);
      issues.push(...this.validateSectionsFile(skillDir, sections));
      const ruleStats = this.validateRulesDir(skillDir, sections, issues);
      issues.push(...this.validateAgentsMd(skillDir, sections, metadata));

      issues.push(...this.validateCrossReferences(skillDir, sections, ruleStats));
      issues.push(...this.validateStatistics(ruleStats));
    } else if (discipline === 'composition') {
      issues.push(...this.validateCompositionSkill(skillDir));
    } else if (discipline === 'investigation') {
      issues.push(...this.validateInvestigationSkill(skillDir));
    } else if (discipline === 'extraction') {
      issues.push(...this.validateExtractionSkill(skillDir));
    } else if (discipline === 'adversarial') {
      issues.push(...this.validateAdversarialSkill(skillDir));
    } else if (discipline === 'navigation') {
      issues.push(...this.validateNavigationSkill(skillDir));
    }

    return createReport(issues, this.strictMode);
  }

  /**
   * Validate composition skill structure
   * @param {string} skillDir
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateCompositionSkill(skillDir) {
    const issues = [];
    const scriptsDir = path.join(skillDir, 'scripts');

    if (!fs.existsSync(scriptsDir)) {
      issues.push(createError('structure', 'Composition skill missing scripts/ directory'));
    } else {
      const scripts = fs.readdirSync(scriptsDir).filter(f => f.endsWith('.sh'));
      if (scripts.length === 0) {
        issues.push(createWarning('scripts/', 'No shell scripts found in scripts/ directory'));
      }
      for (const script of scripts) {
        const content = fs.readFileSync(path.join(scriptsDir, script), 'utf-8');
        if (!content.includes('set -e')) {
          issues.push(createWarning(`scripts/${script}`, 'Script missing strict mode (set -euo pipefail)'));
        }
        if (!content.startsWith('#!')) {
          issues.push(createWarning(`scripts/${script}`, 'Script missing shebang line'));
        }
      }
    }

    // Check hooks if present
    const hooksPath = path.join(skillDir, 'hooks', 'hooks.json');
    if (fs.existsSync(hooksPath)) {
      try {
        const content = fs.readFileSync(hooksPath, 'utf-8');
        JSON.parse(content);
      } catch {
        issues.push(createError('hooks/hooks.json', 'Invalid JSON in hooks file'));
      }
    }

    // Check config.json if present
    const configPath = path.join(skillDir, 'config.json');
    if (fs.existsSync(configPath)) {
      try {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
        if (!config._setup_instructions) {
          issues.push(createWarning('config.json', 'Missing _setup_instructions field'));
        }
      } catch {
        issues.push(createError('config.json', 'Invalid JSON in config file'));
      }
    }

    return issues;
  }

  /**
   * Validate investigation skill structure
   * @param {string} skillDir
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateInvestigationSkill(skillDir) {
    const issues = [];
    const refsDir = path.join(skillDir, 'references');

    if (!fs.existsSync(refsDir)) {
      issues.push(createError('structure', 'Investigation skill missing references/ directory'));
      return issues;
    }

    // Check for symptom catalog
    const symptomsPath = path.join(refsDir, 'symptoms.md');
    if (!fs.existsSync(symptomsPath)) {
      issues.push(createWarning('references/', 'Missing symptoms.md catalog'));
    }

    // Check for decision trees
    const refFiles = fs.readdirSync(refsDir);
    const treeFiles = refFiles.filter(f => f.endsWith('-tree.md'));
    if (treeFiles.length === 0) {
      issues.push(createWarning('references/', 'No decision tree files found (*-tree.md)'));
    }

    // Check for query patterns
    const queriesDir = path.join(refsDir, 'queries');
    if (!fs.existsSync(queriesDir)) {
      issues.push(createWarning('references/', 'Missing queries/ directory'));
    }

    // Check report template
    const reportPath = path.join(skillDir, 'assets', 'templates', 'report.md');
    if (!fs.existsSync(reportPath)) {
      issues.push(createWarning('assets/templates/', 'Missing report.md template'));
    }

    return issues;
  }

  /**
   * Validate extraction skill structure
   * @param {string} skillDir
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateExtractionSkill(skillDir) {
    const issues = [];
    const templatesDir = path.join(skillDir, 'assets', 'templates');

    if (!fs.existsSync(templatesDir)) {
      issues.push(createError('structure', 'Extraction skill missing assets/templates/ directory'));
      return issues;
    }

    const templateFiles = fs.readdirSync(templatesDir).filter(f => f.endsWith('.template'));
    if (templateFiles.length === 0) {
      issues.push(createWarning('assets/templates/', 'No .template files found'));
    }

    // Check for conventions doc
    const conventionsPath = path.join(skillDir, 'references', 'conventions.md');
    if (!fs.existsSync(conventionsPath)) {
      issues.push(createWarning('references/', 'Missing conventions.md'));
    }

    return issues;
  }

  /**
   * Validate adversarial skill structure
   * @param {string} skillDir
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateAdversarialSkill(skillDir) {
    const issues = [];
    const refsDir = path.join(skillDir, 'references');

    if (!fs.existsSync(refsDir)) {
      issues.push(createError('structure', 'Adversarial skill missing references/ directory'));
      return issues;
    }

    // Reviewer prompt is the heart of the gate
    const promptPath = path.join(refsDir, 'reviewer-prompt.md');
    if (!fs.existsSync(promptPath)) {
      issues.push(createError('references/', 'Missing reviewer-prompt.md — the gate cannot dispatch blind reviewers without it'));
    } else {
      const prompt = fs.readFileSync(promptPath, 'utf-8');
      if (!/\bPASS\b/.test(prompt) || !/\bFAIL\b/.test(prompt)) {
        issues.push(createError('references/reviewer-prompt.md', 'Reviewer prompt must demand structured PASS/FAIL verdicts'));
      }
      if (!/evidence/i.test(prompt)) {
        issues.push(createWarning('references/reviewer-prompt.md', 'Reviewer prompt should require evidence for both PASS and FAIL verdicts'));
      }
    }

    // Verdict report template
    const verdictPath = path.join(skillDir, 'assets', 'templates', 'verdict.md');
    if (!fs.existsSync(verdictPath)) {
      issues.push(createWarning('assets/templates/', 'Missing verdict.md report template'));
    }

    // Exactly one rule mode: owned rules (_sections.md + rule files) or companion (rules-source.md)
    const hasSections = fs.existsSync(path.join(refsDir, '_sections.md'));
    const hasRulesSource = fs.existsSync(path.join(refsDir, 'rules-source.md'));

    if (hasSections && hasRulesSource) {
      issues.push(createError('references/', 'Both _sections.md and rules-source.md present — an adversarial skill owns rules OR references a source skill, not both'));
    } else if (hasSections) {
      // Owned-rules mode: rules follow the distillation format
      const sections = this.parseSectionsFile(skillDir);
      issues.push(...this.validateSectionsFile(skillDir, sections));
      this.validateRulesDir(skillDir, sections, issues, ADVERSARIAL_PROTOCOL_FILES);
    } else if (hasRulesSource) {
      const source = fs.readFileSync(path.join(refsDir, 'rules-source.md'), 'utf-8');
      if (!/\*\*Path:\*\*/.test(source)) {
        issues.push(createError('references/rules-source.md', 'Missing "**Path:**" line — companion mode must record where the source rules live'));
      }
      if (!/Source version/i.test(source)) {
        issues.push(createWarning('references/rules-source.md', 'Missing "Source version" line — drift from the source skill is undetectable without it'));
      }
      if (!/Excluded Rules/i.test(source)) {
        issues.push(createWarning('references/rules-source.md', 'Missing "Excluded Rules" section — non-decidable source rules must be listed with reasons, not silently dropped'));
      }
    } else {
      issues.push(createError('references/', 'Adversarial skill needs rules: either _sections.md + rule files (owned) or rules-source.md (companion)'));
    }

    return issues;
  }

  /**
   * Validate navigation skill structure
   * @param {string} skillDir
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateNavigationSkill(skillDir) {
    const issues = [];
    const refsDir = path.join(skillDir, 'references');

    if (!fs.existsSync(refsDir)) {
      issues.push(createError('structure', 'Navigation skill missing references/ directory'));
      return issues;
    }

    // The source map is the heart of a navigation skill
    const sourcesPath = path.join(refsDir, 'sources.md');
    if (!fs.existsSync(sourcesPath)) {
      issues.push(createError('references/', 'Missing sources.md — a navigation skill cannot route without its source map'));
    } else {
      const sources = fs.readFileSync(sourcesPath, 'utf-8');
      if (!/https?:\/\//.test(sources)) {
        issues.push(createError('references/sources.md', 'Source map contains no URLs — each source needs a resolvable location'));
      }
      if (!/not authoritative/i.test(sources)) {
        issues.push(createWarning('references/sources.md', 'No "NOT authoritative for" scoping found — sources should state both what they cover and what they do not'));
      }
    }

    // Search playbooks
    const refFiles = fs.readdirSync(refsDir);
    const playbookFiles = refFiles.filter(f => f.endsWith('-playbook.md'));
    if (playbookFiles.length === 0) {
      issues.push(createWarning('references/', 'No playbook files found (*-playbook.md)'));
    }
    for (const playbook of playbookFiles) {
      const content = fs.readFileSync(path.join(refsDir, playbook), 'utf-8');
      if (!/escalat|ask the user/i.test(content)) {
        issues.push(createWarning(`references/${playbook}`, 'Playbook has no explicit escalation step — every search path must terminate'));
      }
    }

    // Verification rules
    const verificationPath = path.join(refsDir, 'verification.md');
    if (!fs.existsSync(verificationPath)) {
      issues.push(createWarning('references/', 'Missing verification.md — found answers need currency and authority checks'));
    }

    return issues;
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
   * Detect discipline from metadata or directory structure.
   * Defaults to 'distillation' for backwards compatibility.
   * @param {string} skillDir
   * @param {Object|null} metadata
   * @returns {string}
   */
  detectDiscipline(skillDir, metadata) {
    // Prefer explicit discipline from metadata
    if (metadata?.discipline && VALID_DISCIPLINES.includes(metadata.discipline)) {
      return metadata.discipline;
    }

    // Infer from directory structure
    // reviewer-prompt.md is unique to adversarial gates — check before broader signals
    if (fs.existsSync(path.join(skillDir, 'references', 'reviewer-prompt.md'))) {
      return 'adversarial';
    }

    // sources.md + playbooks are unique to navigation — check before the broader
    // scripts/ signal, since a navigation skill may bundle a local doc-search script
    const navRefsDir = path.join(skillDir, 'references');
    if (fs.existsSync(navRefsDir)) {
      const navFiles = fs.readdirSync(navRefsDir);
      if (fs.existsSync(path.join(navRefsDir, 'sources.md')) && navFiles.some(f => f.endsWith('-playbook.md'))) {
        return 'navigation';
      }
    }

    if (fs.existsSync(path.join(skillDir, 'scripts'))) {
      return 'composition';
    }

    const refsDir = path.join(skillDir, 'references');
    if (fs.existsSync(refsDir)) {
      const refFiles = fs.readdirSync(refsDir);
      if (refFiles.some(f => f.endsWith('-tree.md')) || fs.existsSync(path.join(refsDir, 'queries'))) {
        return 'investigation';
      }
    }

    const templatesDir = path.join(skillDir, 'assets', 'templates');
    if (fs.existsSync(templatesDir)) {
      const templateFiles = fs.readdirSync(templatesDir);
      if (templateFiles.some(f => f.endsWith('.template'))) {
        return 'extraction';
      }
    }

    // Default: distillation (backwards compatible)
    return 'distillation';
  }

  /**
   * Validate required files exist
   * @param {string} skillDir
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateRequiredFiles(skillDir, discipline = 'distillation') {
    const issues = [];

    // Check base required files (universal)
    for (const file of REQUIRED_FILES) {
      const filepath = path.join(skillDir, file);
      if (!fs.existsSync(filepath)) {
        issues.push(createError('structure',
          `${VALIDATION_MESSAGES.MISSING_FILE(file)}. ${VALIDATION_MESSAGES.GUIDE_REQUIRED_FILES}`
        ));
      }
    }

    // _sections.md is only required for distillation (category-based skills)
    if (discipline === 'distillation') {
      const { dir: refDir, name: refDirName } = this.getReferencesDir(skillDir);
      const sectionsPath = path.join(refDir, '_sections.md');
      if (!fs.existsSync(sectionsPath)) {
        issues.push(createError('structure',
          `${VALIDATION_MESSAGES.MISSING_FILE(`${refDirName}/_sections.md`)}. ${VALIDATION_MESSAGES.GUIDE_REQUIRED_FILES}`
        ));
      }
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
  validateSkillMd(skillDir, metadata = null, discipline = 'distillation') {
    const filepath = path.join(skillDir, 'SKILL.md');
    if (!fs.existsSync(filepath)) return [];

    const issues = [];
    const content = fs.readFileSync(filepath, 'utf-8');
    const { frontmatter, body } = parseFrontmatter(content);

    // Validate frontmatter (universal)
    issues.push(...validateSkillFrontmatter(frontmatter, 'SKILL.md'));

    // H1 presence check is distillation-only (the title text itself is free-form)
    if (discipline === 'distillation') {
      const organization = metadata?.organization || null;
      issues.push(...validateSkillH1Format(content, organization, 'SKILL.md'));
    }

    // Check line count (universal)
    const lineCount = content.split('\n').length;
    if (lineCount < MIN_SKILL_MD_LINES) {
      issues.push(createWarning('SKILL.md', VALIDATION_MESSAGES.SKILL_TOO_SHORT(lineCount)));
    }
    if (lineCount > MAX_SKILL_MD_LINES) {
      issues.push(createWarning('SKILL.md', VALIDATION_MESSAGES.SKILL_TOO_LONG(lineCount)));
    }

    // Check discipline-specific required sections
    const requiredSections = REQUIRED_SKILL_SECTIONS_BY_DISCIPLINE[discipline] || REQUIRED_SKILL_SECTIONS;
    for (const section of requiredSections) {
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
   * @param {string[]} excludeFiles - Non-rule files to skip (e.g. adversarial protocol files)
   * @returns {{totalRules: number, quantifiedRules: number, rulesByPrefix: Object}}
   */
  validateRulesDir(skillDir, sections, issues, excludeFiles = []) {
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
      .filter(f => !f.startsWith('_') && !excludeFiles.includes(f));

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

    // No "> **Note:** this document is for agents/LLMs" block is required.
    // Telling the reader the reader is an AI is dead weight — the build script
    // no longer emits it.

    if (sections.length > 0) {
      issues.push(...validateAgentsTocCompleteness(content, sections, 'AGENTS.md'));
    }

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
   * Overall statistics no longer produce warnings.
   *
   * Two checks used to live here and both fought against conciseness:
   *   - a rule-count floor ("only N rules found") that rewarded padding, and
   *   - a quantified-impact percentage that rewarded fake metrics.
   * Completeness is proven by behavior on the target tasks, not by counts.
   * Kept as a no-op so the call site and any consumers stay stable.
   * @returns {import('./types.js').ValidationIssue[]}
   */
  validateStatistics() {
    return [];
  }
}

export { SkillValidator, parseFrontmatter, parseSections, getFiles };
