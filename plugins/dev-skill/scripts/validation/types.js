/**
 * Validation Type Definitions
 *
 * @typedef {'ERROR' | 'WARNING' | 'INFO'} ValidationLevel
 * @typedef {{level: ValidationLevel, path: string, message: string, line?: number, suggestion?: string}} ValidationIssue
 * @typedef {{errors: number, warnings: number, info: number}} ValidationSummary
 * @typedef {{valid: boolean, issues: ValidationIssue[], summary: ValidationSummary}} ValidationReport
 * @typedef {{index: number, name: string, prefix: string, impact: string, description: string}} Section
 * @typedef {{frontmatter: Object, body: string}} ParsedFrontmatter
 */

/**
 * Create a validation issue
 * @param {'ERROR' | 'WARNING' | 'INFO'} level
 * @param {string} path
 * @param {string} message
 * @param {Object} [opts]
 * @returns {ValidationIssue}
 */
function createIssue(level, path, message, opts = {}) {
  return { level, path, message, ...opts };
}

function createError(path, message, opts) {
  return createIssue('ERROR', path, message, opts);
}

function createWarning(path, message, opts) {
  return createIssue('WARNING', path, message, opts);
}

function createInfo(path, message, opts) {
  return createIssue('INFO', path, message, opts);
}

/**
 * Create a validation report from issues
 * @param {ValidationIssue[]} issues
 * @param {boolean} [strictMode=false]
 * @returns {ValidationReport}
 */
function createReport(issues, strictMode = false) {
  const summary = { errors: 0, warnings: 0, info: 0 };

  for (const issue of issues) {
    if (issue.level === 'ERROR') summary.errors++;
    else if (issue.level === 'WARNING') summary.warnings++;
    else if (issue.level === 'INFO') summary.info++;
  }

  const valid = strictMode
    ? summary.errors === 0 && summary.warnings === 0
    : summary.errors === 0;

  return { valid, issues, summary };
}

export { createError, createWarning, createInfo, createReport };
