#!/usr/bin/env node

/**
 * Skill Validation CLI
 *
 * Validates generated performance best practices skills against quality guidelines.
 *
 * Usage:
 *   node validate-skill.js <skill-directory> [options]
 *   node validate-skill.js --all <skills-directory> [options]
 */

import fs from 'fs';
import path from 'path';
import { SkillValidator } from './validation/validator.js';

/**
 * Parse command line arguments
 * @param {string[]} args
 * @returns {{skillDir: string|null, options: Object}}
 */
function parseArgs(args) {
  const options = {
    strict: false,
    json: false,
    all: false,
    sectionsOnly: false,
    concurrency: parseInt(process.env.SKILL_VALIDATOR_CONCURRENCY || '6', 10),
  };

  let skillDir = null;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--strict') options.strict = true;
    else if (arg === '--json') options.json = true;
    else if (arg === '--all') options.all = true;
    else if (arg === '--sections-only') options.sectionsOnly = true;
    else if (arg === '--concurrency' && args[i + 1]) {
      const n = parseInt(args[++i], 10);
      if (n > 0) options.concurrency = n;
    } else if (!arg.startsWith('--')) {
      skillDir = arg;
    }
  }

  return { skillDir, options };
}

/**
 * Format and print issue by level
 * @param {string} label
 * @param {string} icon
 * @param {import('./validation/types.js').ValidationIssue[]} issues
 */
function printIssueGroup(label, icon, issues) {
  if (issues.length === 0) return;
  console.log(`\n${label}:`);
  for (const issue of issues) {
    const loc = issue.line ? `${issue.path}:${issue.line}` : issue.path;
    console.log(`  ${icon} [${loc}] ${issue.message}`);
  }
}

/**
 * Print human-readable report
 * @param {string} skillId
 * @param {import('./validation/types.js').ValidationReport} report
 * @param {number} durationMs
 */
function printHumanReport(skillId, report, durationMs) {
  console.log(`\nValidating skill: ${skillId}\n`);
  console.log('='.repeat(60));

  const byLevel = { ERROR: [], WARNING: [], INFO: [] };
  for (const issue of report.issues) {
    byLevel[issue.level]?.push(issue);
  }

  printIssueGroup('Errors', '✗', byLevel.ERROR);
  printIssueGroup('Warnings', '⚠', byLevel.WARNING);
  printIssueGroup('Info', 'ℹ', byLevel.INFO);

  console.log('\n' + '='.repeat(60));
  console.log(`\nSummary: ${report.summary.errors} errors, ${report.summary.warnings} warnings, ${report.summary.info} info`);
  console.log(`Duration: ${durationMs}ms`);
  console.log(`Status: ${report.valid ? '✅ PASSED' : '❌ FAILED'}\n`);

  if (!report.valid) {
    printNextSteps(report);
  }
}

/**
 * Print next steps guidance when validation fails
 * @param {import('./validation/types.js').ValidationReport} report
 */
function printNextSteps(report) {
  console.log('Next steps:');
  console.log('  - Fix all ERROR issues before release');
  console.log('  - Review WARNING issues for quality');
  console.log('  - Run with --strict to fail on warnings');

  const fixes = [
    { pattern: 'vague language', fix: 'Replace "consider" with "Use X when Y"' },
    { pattern: 'code example', fix: 'Add **Incorrect** and **Correct** code examples' },
    { pattern: 'First tag', fix: 'Ensure first tag matches file prefix (e.g., async-foo.md → "async")' },
    { pattern: 'quantified', fix: 'Quantify impact: "2-10× improvement", "200ms savings"' },
  ];

  const messages = report.issues.map(i => i.message).join(' ');
  const applicableFixes = fixes.filter(f => messages.includes(f.pattern));

  if (applicableFixes.length > 0) {
    console.log('\nCommon fixes:');
    for (const { fix } of applicableFixes) {
      console.log(`  - ${fix}`);
    }
  }
  console.log();
}

/**
 * Build JSON output for validation results
 * @param {Array<{id: string, valid: boolean, issues: Array, durationMs: number}>} items
 * @returns {Object}
 */
function buildJsonOutput(items) {
  const passed = items.filter(i => i.valid).length;
  const failed = items.length - passed;
  return {
    version: '1.0',
    items: items.map(i => ({ ...i, type: 'skill' })),
    summary: {
      totals: { items: items.length, passed, failed },
      byType: { skill: { items: items.length, passed, failed } }
    }
  };
}

/**
 * Print JSON report for a single skill
 * @param {string} skillId
 * @param {import('./validation/types.js').ValidationReport} report
 * @param {number} durationMs
 */
function printJsonReport(skillId, report, durationMs) {
  const output = buildJsonOutput([{ id: skillId, valid: report.valid, issues: report.issues, durationMs }]);
  console.log(JSON.stringify(output, null, 2));
}

/**
 * Run bulk validation on multiple skills
 * @param {string} skillsDir
 * @param {Object} options
 */
async function runBulkValidation(skillsDir, options) {
  const validator = new SkillValidator(options.strict);

  const skillDirs = fs.readdirSync(skillsDir, { withFileTypes: true })
    .filter(e => e.isDirectory() && fs.existsSync(path.join(skillsDir, e.name, 'SKILL.md')))
    .map(e => e.name);

  if (skillDirs.length === 0) {
    if (options.json) {
      console.log(JSON.stringify(buildJsonOutput([]), null, 2));
    } else {
      console.log('No skills found to validate.');
    }
    process.exit(0);
  }

  const results = [];

  for (let i = 0; i < skillDirs.length; i += options.concurrency) {
    const chunk = skillDirs.slice(i, i + options.concurrency);

    if (!options.json) {
      process.stdout.write(`\rValidating (${Math.min(i + options.concurrency, skillDirs.length)}/${skillDirs.length})...`);
    }

    const chunkResults = await Promise.all(chunk.map(async (name) => {
      const start = Date.now();
      try {
        const report = await validator.validateSkill(path.join(skillsDir, name));
        return { id: name, valid: report.valid, issues: report.issues, durationMs: Date.now() - start };
      } catch (error) {
        return { id: name, valid: false, issues: [{ level: 'ERROR', path: 'file', message: error.message }], durationMs: 0 };
      }
    }));

    results.push(...chunkResults);
  }

  if (!options.json) {
    process.stdout.write('\r' + ' '.repeat(40) + '\r');
  }

  results.sort((a, b) => a.id.localeCompare(b.id));

  if (options.json) {
    console.log(JSON.stringify(buildJsonOutput(results), null, 2));
  } else {
    const passed = results.filter(r => r.valid).length;
    const failed = results.length - passed;

    console.log('\nBulk Validation Results:\n');
    for (const res of results) {
      if (res.valid) {
        console.log(`  ✓ ${res.id}`);
      } else {
        const errCount = res.issues.filter(i => i.level === 'ERROR').length;
        const warnCount = res.issues.filter(i => i.level === 'WARNING').length;
        console.log(`  ✗ ${res.id} (${errCount} errors, ${warnCount} warnings)`);
      }
    }
    console.log(`\nTotals: ${passed} passed, ${failed} failed (${results.length} skills)`);
  }

  process.exit(results.some(r => !r.valid) ? 1 : 0);
}

/**
 * Validate a single skill
 * @param {string} skillDir
 * @param {Object} options
 */
async function validateSingleSkill(skillDir, options) {
  const validator = new SkillValidator(options.strict);
  const skillId = path.basename(skillDir);
  const start = Date.now();

  const report = options.sectionsOnly
    ? await validator.validateSectionsOnly(skillDir)
    : await validator.validateSkill(skillDir);

  const durationMs = Date.now() - start;

  if (options.json) {
    printJsonReport(skillId, report, durationMs);
  } else {
    if (options.sectionsOnly) {
      console.log(`\nValidating sections only: ${skillId}\n`);
    }
    printHumanReport(skillId, report, durationMs);
  }

  process.exit(report.valid ? 0 : 1);
}

function printUsage() {
  console.log(`
Skill Validation CLI

Usage:
  node validate-skill.js <skill-directory> [options]
  node validate-skill.js --all <skills-directory> [options]

Options:
  --strict        Treat warnings as errors (fail if any warnings)
  --json          Output JSON report format
  --all           Validate all skills in the given directory
  --concurrency N Number of parallel validations (default: 6)
  --sections-only Validate only _sections.md (for incremental generation)

Examples:
  node validate-skill.js ./skills/react-best-practices
  node validate-skill.js ./skills/react-best-practices --strict
  node validate-skill.js ./skills/react-best-practices --json
  node validate-skill.js --all ./skills
  node validate-skill.js --all ./skills --json --concurrency 4
  node validate-skill.js ./skills/react-best-practices --sections-only

Incremental Validation:
  Use --sections-only during skill generation to validate categories early.
  This enables fail-fast behavior before generating individual rules.

Exit codes:
  0 - All validations passed
  1 - Validation errors found (or warnings in strict mode)

Environment variables:
  SKILL_VALIDATOR_CONCURRENCY - Default concurrency (default: 6)
`);
}

async function main() {
  const args = process.argv.slice(2);

  if (args.includes('--help') || args.includes('-h')) {
    printUsage();
    process.exit(0);
  }

  const { skillDir, options } = parseArgs(args);

  if (options.all) {
    if (!skillDir) {
      console.error('Error: --all requires a directory path');
      console.error('Usage: node validate-skill.js --all <skills-directory>');
      process.exit(1);
    }
    if (!fs.existsSync(skillDir)) {
      console.error(`Error: Directory not found: ${skillDir}`);
      process.exit(1);
    }
    await runBulkValidation(skillDir, options);
    return;
  }

  if (!skillDir) {
    console.error('Error: No skill directory specified');
    console.error('Usage: node validate-skill.js <skill-directory>');
    console.error('       node validate-skill.js --all <skills-directory>');
    console.error('\nRun with --help for more information.');
    process.exit(1);
  }

  if (!fs.existsSync(skillDir)) {
    console.error(`Error: Directory not found: ${skillDir}`);
    process.exit(1);
  }

  await validateSingleSkill(skillDir, options);
}

main().catch(error => {
  console.error(`Fatal error: ${error.message}`);
  process.exit(1);
});
