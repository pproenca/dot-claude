# MCP Builder

Build and integrate MCP (Model Context Protocol) servers that enable LLMs to interact with external services.

## Skills

| Skill | Purpose |
|-------|---------|
| mcp-builder | Comprehensive MCP server development guide |

## What's Included

The skill covers:

- **Phase 1**: Research and planning
- **Phase 2**: Implementation patterns
- **Phase 3**: Review and testing
- **Phase 4**: Creating evaluations

## Supported Stacks

**TypeScript (recommended)**
- MCP SDK for TypeScript
- Zod for schema validation
- Streamable HTTP transport

**Python**
- FastMCP framework
- Pydantic for schemas
- stdio or HTTP transport

## Reference Files

```
skills/mcp-builder/
├── SKILL.md                    # Main guide
├── reference/
│   ├── mcp_best_practices.md   # Universal MCP guidelines
│   ├── node_mcp_server.md      # TypeScript patterns
│   ├── python_mcp_server.md    # Python patterns
│   └── evaluation.md           # Testing evaluations
└── scripts/                    # Helper utilities
```

## Usage

Ask Claude to help build an MCP server:

```
Help me build an MCP server for the GitHub API
```

The skill provides structured guidance through all phases of MCP development.
