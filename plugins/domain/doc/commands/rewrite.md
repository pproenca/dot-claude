---
description: Rewrite a markdown document following Amazon's narrative writing standards
argument-hint: "[document-type]"
allowed-tools:
  - Read
  - Write
  - Glob
  - Skill
  - AskUserQuestion
---

# Amazon-Style Document Rewriter

Rewrite content following Amazon's internal writing standards, transforming documents into narrative memos with data-driven communication.

## Supported Document Types

- **press-release** or **pr**: Product/feature announcement (1-1.5 pages)
- **6-pager** or **six-pager**: Detailed strategic memo (6 pages + appendix)
- **1-pager** or **one-pager**: Quick decision document (1 page)
- **prfaq**: Press Release + FAQ for product innovation

## Workflow

### Step 1: Gather Input

If the user provided a file path in their message or as an argument:
- Read the file using the Read tool

If no file was provided, use AskUserQuestion:

### Input Source
- Header: "Source"
- Question: "How would you like to provide the content to rewrite?"
- Options:
  - File path: I'll specify a file path to read
  - Paste content: I'll paste the content directly in chat
  - Browse: Show me markdown files in the project to choose from

### Step 2: Determine Document Type

If document type was provided as argument (e.g., `/memo-writer:rewrite press-release`):
- Use that document type

If no document type specified, use AskUserQuestion:

### Document Type
- Header: "Format"
- Question: "What document type should this be rewritten as?"
- Options:
  - Press Release: Product/feature announcements (1-1.5 pages)
  - 6-Pager: Complex strategic topics requiring detailed analysis
  - 1-Pager: Quick decisions, straightforward topics (1 page max)
  - PRFAQ: Product innovation using working-backwards method

### Step 3: Load Guidelines

Use the Skill tool to load the `amazon-writing` skill for core writing rules.

Then read the appropriate reference file for detailed document-specific guidelines:
- Press Release: `${CLAUDE_PLUGIN_ROOT}/skills/amazon-writing/references/press-release.md`
- 6-Pager: `${CLAUDE_PLUGIN_ROOT}/skills/amazon-writing/references/six-pager.md`
- 1-Pager: `${CLAUDE_PLUGIN_ROOT}/skills/amazon-writing/references/one-pager.md`
- PRFAQ: `${CLAUDE_PLUGIN_ROOT}/skills/amazon-writing/references/prfaq.md`

### Step 4: Analyze Content

Before rewriting, analyze the content in a scratchpad:

```
<scratchpad>
1. Main message/purpose: [identify]
2. Vague qualifiers to replace with data: [list them]
3. Passive voice to convert: [list constructions]
4. Jargon/acronyms to clarify: [list them]
5. Logical narrative flow: [outline beginning, middle, end]
6. Document-specific sections: [which are present/missing]
</scratchpad>
```

### Step 5: Rewrite Content

Transform the content following:
- Core Amazon writing rules (narrative structure, data over adjectives, active voice, conciseness, "so what" test, respect reader's time)
- Document-specific structure and required sections
- Length constraints for the document type

Output the rewritten content in a clear format:

```
<rewritten_content>
[Complete rewritten document in Amazon style]
</rewritten_content>
```

### Step 6: Output Options

After presenting the rewritten content, use AskUserQuestion:

### Save Options
- Header: "Save"
- Question: "How would you like to save the rewritten document?"
- Options:
  - Display only: Keep it in the conversation (no file changes)
  - New file: Write to a new file (e.g., `original-name-amazon.md`)
  - Overwrite: Replace the original file with the rewritten version

If user chooses new file or overwrite, use the Write tool to save.

## Important Notes

- Never use bullet points in the rewritten content (Amazon narrative style)
- Replace ALL vague qualifiers with specific data (ask user for data if critical metrics are missing)
- Convert ALL passive voice to active voice
- Ensure every sentence passes the "so what" test
- Check length constraints for the document type
- For PRFAQs, ensure both External and Internal FAQ sections are included

## Example Usage

User: `/memo-writer:rewrite press-release`
User: "Here's my product announcement: [content]"

User: `/memo-writer:rewrite`
User: "Rewrite /path/to/document.md as a 6-pager"

User: `/memo-writer:rewrite 1-pager /path/to/notes.md`
