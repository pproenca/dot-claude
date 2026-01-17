#!/usr/bin/env node

/**
 * AGENTS.md Build Script
 *
 * Compiles individual reference files into a single comprehensive AGENTS.md document.
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

function getReferencesForSection(referencesDir, prefix, files) {
  const references = [];

  for (const file of files) {
    if (file.startsWith(prefix + '-') && file.endsWith('.md')) {
      const filepath = path.join(referencesDir, file);
      const content = fs.readFileSync(filepath, 'utf-8');
      const { frontmatter, body } = parseFrontmatter(content);

      references.push({
        filename: file,
        title: frontmatter.title || file,
        impact: frontmatter.impact || 'MEDIUM',
        impactDescription: frontmatter.impactDescription || '',
        tags: frontmatter.tags || '',
        body: body.trim()
      });
    }
  }

  references.sort((a, b) => a.title.localeCompare(b.title));

  return references;
}

function buildAgentsMD(skillDir) {
  const metadataPath = path.join(skillDir, 'metadata.json');
  if (!fs.existsSync(metadataPath)) {
    console.error('Error: metadata.json not found');
    process.exit(1);
  }
  const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'));

  // Try references/ first, fall back to rules/ for backwards compatibility
  let referencesDir = path.join(skillDir, 'references');
  let sectionsPath = path.join(referencesDir, '_sections.md');

  if (!fs.existsSync(sectionsPath)) {
    // Fall back to legacy rules/ directory
    referencesDir = path.join(skillDir, 'rules');
    sectionsPath = path.join(referencesDir, '_sections.md');
    if (!fs.existsSync(sectionsPath)) {
      console.error('Error: _sections.md not found in references/ or rules/');
      process.exit(1);
    }
  }

  const sections = parseSections(fs.readFileSync(sectionsPath, 'utf-8'));
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

  const referencesCache = new Map();
  const referenceFiles = fs.readdirSync(referencesDir);
  for (const section of sections) {
    referencesCache.set(section.prefix, getReferencesForSection(referencesDir, section.prefix, referenceFiles));
  }

  let totalRules = 0;
  for (const section of sections) {
    const sectionSlug = slugify(`${section.index} ${section.name}`);
    output.push(`${section.index}. [${section.name}](#${sectionSlug}) — **${section.impact}**`);

    const references = referencesCache.get(section.prefix);
    totalRules += references.length;
    for (let i = 0; i < references.length; i++) {
      const ruleNum = `${section.index}.${i + 1}`;
      const ruleSlug = slugify(`${ruleNum} ${references[i].title}`);
      output.push(`   - ${ruleNum} [${references[i].title}](#${ruleSlug})`);
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

    const references = referencesCache.get(section.prefix);
    for (let i = 0; i < references.length; i++) {
      const ref = references[i];
      const ruleNum = `${section.index}.${i + 1}`;
      const impact = ref.impactDescription
        ? `**Impact: ${ref.impact} (${ref.impactDescription})**`
        : `**Impact: ${ref.impact}**`;
      // Remove leading H2 title from body (already in subsection header)
      const body = ref.body.replace(/^## .+\n+/, '');

      output.push(`### ${ruleNum} ${ref.title}`, '', impact, '', body, '');
    }

    output.push('---', '');
  }

  output.push('## References', '');
  if (metadata.references?.length > 0) {
    metadata.references.forEach((ref, index) => {
      output.push(`${index + 1}. [${ref}](${ref})`);
    });
  }

  // Add Source Files footer section with markdown links
  const isNewStructure = fs.existsSync(path.join(skillDir, 'references'));
  const refDirName = isNewStructure ? 'references' : 'rules';

  output.push('', '---', '');
  output.push('## Source Files', '');
  output.push('This document was compiled from individual reference files. For detailed editing or extension:', '');
  output.push('| File | Description |');
  output.push('|------|-------------|');
  output.push(`| [${refDirName}/_sections.md](${refDirName}/_sections.md) | Category definitions and impact ordering |`);

  // Check for assets/templates directory
  const templatesDir = path.join(skillDir, 'assets', 'templates');
  if (fs.existsSync(templatesDir)) {
    output.push('| [assets/templates/_template.md](assets/templates/_template.md) | Template for creating new rules |');
  }

  output.push('| [SKILL.md](SKILL.md) | Quick reference entry point |');
  output.push('| [metadata.json](metadata.json) | Version and reference URLs |');

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
