# Build iOS Apps Plugin

> Ported from the [OpenAI Codex plugin](https://github.com/openai/codex) to Claude Code.

This plugin packages iOS and Swift workflows in `domain_plugins/build-ios-apps`.

It currently includes these skills:

- `ios-debugger-agent`
- `swiftui-liquid-glass`
- `swiftui-performance-audit`
- `swiftui-ui-patterns`
- `swiftui-view-refactor`

## What It Covers

- building and refactoring SwiftUI UI using current platform patterns
- reviewing or adopting iOS 26+ Liquid Glass APIs
- auditing SwiftUI performance and guiding profiling workflows
- debugging iOS apps on simulators with XcodeBuildMCP-backed flows
- restructuring large SwiftUI views toward smaller, more stable compositions

## Plugin Structure

The plugin lives at:

- `domain_plugins/build-ios-apps/`

with this shape:

- `.claude-plugin/plugin.json`
  - required plugin manifest
  - defines plugin metadata for Claude Code

- `agents/`
  - autonomous subagent definitions
  - one `.md` file per agent, matching each skill

- `skills/`
  - the actual skill payload
  - each skill keeps the normal skill structure (`SKILL.md`, optional
    `references/`)

- `.mcp.json`
  - MCP server configuration
  - bundles XcodeBuildMCP for simulator debugging workflows

## Prerequisites

The `ios-debugger-agent` skill and agent require
[XcodeBuildMCP](https://github.com/nicklama/xcodebuildmcp) for simulator
build/run/debug workflows. The plugin ships an `.mcp.json` that configures it
via npx. Alternatively, install via Homebrew:

```bash
brew tap nicklama/xcodebuildmcp
brew install xcodebuildmcp
```

Verify the MCP server is connected with `/mcp` in Claude Code.
