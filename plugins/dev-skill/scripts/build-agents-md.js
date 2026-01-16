#!/usr/bin/env node

/**
 * AGENTS.md Build Script
 *
 * Compiles individual rule files into a single comprehensive AGENTS.md document.
 *
 * Usage: node build-agents-md.js <skill-directory>
 */

import fs from 'fs';
import path from 'path';

const FRONTMATTER_REGEX = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/;
const SECTION_HEADER_REGEX = /^## (\d+)\. (.+) \(([a-z]+)\)/;
const IMPACT_REGEX = /^\*\*Impact:\*\* (.+)/;
const DESCRIPTION_REGEX = /^\*\*Description:\*\* (.+)/;

function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim();
}

function parseFrontmatter(content) {
  const match = content.match(FRONTMATTER_REGEX);
  if (!match) return { frontmatter: {}, body: content };

  const frontmatter = {};
  for (const line of match[1].split('\n')) {
    const colonIndex = line.indexOf(':');
    if (colonIndex > 0) {
      const key = line.slice(0, colonIndex).trim();
      let value = line.slice(colonIndex + 1).trim();
      if ((value.startsWith('"') && value.endsWith('"')) ||
          (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }
      frontmatter[key] = value;
    }
  }
  return { frontmatter, body: match[2] };
}

function parseSections(content) {
  const sections = [];
  let currentSection = null;

  for (const line of content.split('\n')) {
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

    if (!currentSection) continue;

    const impactMatch = line.match(IMPACT_REGEX);
    if (impactMatch) {
      currentSection.impact = impactMatch[1].trim();
      continue;
    }

    const descMatch = line.match(DESCRIPTION_REGEX);
    if (descMatch) {
      currentSection.description = descMatch[1].trim();
    }
  }

  if (currentSection) sections.push(currentSection);
  return sections;
}

function getRulesForSection(rulesDir, prefix, files) {
  const rules = [];

  for (const file of files) {
    if (file.startsWith(prefix + '-') && file.endsWith('.md')) {
      const filepath = path.join(rulesDir, file);
      const content = fs.readFileSync(filepath, 'utf-8');
      const { frontmatter, body } = parseFrontmatter(content);

      rules.push({
        filename: file,
        title: frontmatter.title || file,
        impact: frontmatter.impact || 'MEDIUM',
        impactDescription: frontmatter.impactDescription || '',
        tags: frontmatter.tags || '',
        body: body.trim()
      });
    }
  }

  rules.sort((a, b) => a.title.localeCompare(b.title));

  return rules;
}

function buildAgentsMD(skillDir) {
  const metadataPath = path.join(skillDir, 'metadata.json');
  if (!fs.existsSync(metadataPath)) {
    console.error('Error: metadata.json not found');
    process.exit(1);
  }
  const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));

  const sectionsPath = path.join(skillDir, 'rules', '_sections.md');
  if (!fs.existsSync(sectionsPath)) {
    console.error('Error: rules/_sections.md not found');
    process.exit(1);
  }
  const sections = parseSections(fs.readFileSync(sectionsPath, 'utf-8'));
  const rulesDir = path.join(skillDir, 'rules');
  const techName = metadata.technology || 'Best Practices';

  const output = [
    `# ${techName}`,
    '',
    `**Version ${metadata.version}**  `,
    `${metadata.organization}  `,
    metadata.date,
    '',
    '> **Note:**  ',
    '> This document is mainly for agents and LLMs to follow when maintaining,  ',
    '> generating, or refactoring codebases. Humans may also find it useful,  ',
    '> but guidance here is optimized for automation and consistency by AI-assisted workflows.',
    '',
    '---',
    '',
    '## Abstract',
    '',
    metadata.abstract,
    '',
    '---',
    '',
    '## Table of Contents',
    ''
  ];

  const rulesCache = new Map();
  const ruleFiles = fs.readdirSync(rulesDir);
  for (const section of sections) {
    rulesCache.set(section.prefix, getRulesForSection(rulesDir, section.prefix, ruleFiles));
  }

  let totalRules = 0;
  for (const section of sections) {
    const sectionSlug = slugify(`${section.index} ${section.name}`);
    output.push(`${section.index}. [${section.name}](#${sectionSlug}) — **${section.impact}**`);

    const rules = rulesCache.get(section.prefix);
    totalRules += rules.length;
    for (let i = 0; i < rules.length; i++) {
      const ruleNum = `${section.index}.${i + 1}`;
      const ruleSlug = slugify(`${ruleNum} ${rules[i].title}`);
      output.push(`   - ${ruleNum} [${rules[i].title}](#${ruleSlug})`);
    }
  }

  output.push('', '---', '');

  for (const section of sections) {
    output.push(
      `## ${section.index}. ${section.name}`,
      '',
      `**Impact: ${section.impact}**`,
      '',
      section.description,
      ''
    );

    const rules = rulesCache.get(section.prefix);
    for (let i = 0; i < rules.length; i++) {
      const rule = rules[i];
      const ruleNum = `${section.index}.${i + 1}`;
      const impact = rule.impactDescription
        ? `**Impact: ${rule.impact} (${rule.impactDescription})**`
        : `**Impact: ${rule.impact}**`;
      // Remove leading H2 title from rule body (already in subsection header)
      const body = rule.body.replace(/^## .+\n+/, '');

      output.push(`### ${ruleNum} ${rule.title}`, '', impact, '', body, '');
    }

    output.push('---', '');
  }

  output.push('## References', '');
  if (metadata.references?.length > 0) {
    metadata.references.forEach((ref, index) => {
      output.push(`${index + 1}. [${ref}](${ref})`);
    });
  }

  return { output: output.join('\n'), totalRules, sectionCount: sections.length };
}

// Export for use as a module
export { buildAgentsMD };

// CLI entry point - only runs when executed directly
const isMainModule = import.meta.url === `file://${process.argv[1]}`;
if (isMainModule) {
  const skillDir = process.argv[2];
  if (!skillDir) {
    console.log('Usage: node build-agents-md.js <skill-directory>');
    process.exit(1);
  }

  if (!fs.existsSync(skillDir)) {
    console.error(`Error: Directory not found: ${skillDir}`);
    process.exit(1);
  }

  const { output, totalRules, sectionCount } = buildAgentsMD(skillDir);
  const outputPath = path.join(skillDir, 'AGENTS.md');
  fs.writeFileSync(outputPath, output);

  console.log(`Generated: ${outputPath}`);
  console.log(`Sections: ${sectionCount}, Rules: ${totalRules}, Lines: ${output.split('\n').length}`);
}
