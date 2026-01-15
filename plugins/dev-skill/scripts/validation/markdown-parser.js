/**
 * Markdown Parser
 *
 * Unified/remark-based markdown parser for reliable AST extraction.
 */

import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkFrontmatter from 'remark-frontmatter';
import { visit } from 'unist-util-visit';
import { parse as parseYaml } from 'yaml';

const processor = unified().use(remarkParse).use(remarkFrontmatter, ['yaml']);

/**
 * Parse markdown content into an AST
 * @param {string} content
 * @returns {Object}
 */
export function parseMarkdown(content) {
  return processor.parse(content);
}

/**
 * Extract YAML frontmatter from markdown
 * @param {string} content
 * @returns {Object|null}
 */
export function extractFrontmatter(content) {
  const tree = parseMarkdown(content);
  let frontmatter = null;

  visit(tree, 'yaml', (node) => {
    try {
      frontmatter = parseYaml(node.value);
    } catch {
      // Invalid YAML - return null
    }
  });

  return frontmatter;
}

/**
 * Extract the body content after frontmatter
 * @param {string} content
 * @returns {string}
 */
export function extractBody(content) {
  const match = content.match(/^---\n[\s\S]*?\n---\n/);
  return match ? content.slice(match[0].length) : content;
}

/**
 * Extract code blocks with context about preceding annotations
 * @param {string} content
 * @returns {Array<{lang: string|null, code: string, annotation: Object|null, isIncorrect: boolean, isCorrect: boolean}>}
 */
export function extractCodeBlocksWithContext(content) {
  const tree = parseMarkdown(content);
  const blocks = [];
  let lastAnnotation = null;

  visit(tree, (node) => {
    // Track strong/bold text that might be annotations
    if (node.type === 'strong') {
      const text = node.children
        .filter(child => child.type === 'text')
        .map(child => child.value)
        .join('');

      // Match Incorrect/Correct annotations with optional description
      const match = text.match(/^(Incorrect|Correct)(?:\s*\((.+)\))?:?$/i);
      if (match) {
        lastAnnotation = {
          type: match[1].toLowerCase(),
          description: match[2] || null
        };
      }
    }

    // Extract code blocks with annotation context
    if (node.type === 'code') {
      blocks.push({
        lang: node.lang || null,
        code: node.value,
        annotation: lastAnnotation,
        isIncorrect: lastAnnotation?.type === 'incorrect',
        isCorrect: lastAnnotation?.type === 'correct'
      });
      lastAnnotation = null;
    }
  });

  return blocks;
}
