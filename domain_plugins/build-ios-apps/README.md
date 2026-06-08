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
  - bundles two complementary MCP servers (see below)

## MCP Servers

The plugin ships two MCP servers that cover different layers of the Apple
toolchain:

| Server | Backed by | Covers |
| --- | --- | --- |
| `XcodeBuildMCP` | [XcodeBuildMCP](https://github.com/nicklama/xcodebuildmcp) via `npx` | Simulator build/run/launch, UI automation (tap/type/swipe), screenshots, simulator log capture, device workflows |
| `XcodeBridge` | Apple's `xcrun mcpbridge` (ships with Xcode) | Drives the **running Xcode IDE** on the active workspace: build (`BuildProject`), tests (`RunAllTests`/`RunSomeTests`), diagnostics (`XcodeListNavigatorIssues`, `GetBuildLog`), SwiftUI previews (`RenderPreview`), and Apple docs search (`DocumentationSearch`) |

The two are complementary: `XcodeBridge` reads build errors and runs tests
against whatever workspace Xcode currently has open, while `XcodeBuildMCP`
boots simulators and automates the on-screen UI. `XcodeBridge` cannot control
simulators, capture device logs, or automate UI — use `XcodeBuildMCP` for those.

## Prerequisites

**`XcodeBuildMCP`** (simulator run/debug + UI automation): the plugin's
`.mcp.json` runs it via `npx` with no setup. Alternatively, install via
Homebrew:

```bash
brew tap nicklama/xcodebuildmcp
brew install xcodebuildmcp
```

**`XcodeBridge`** (Apple `xcrun mcpbridge`): requires Xcode 26 or later and a
**running Xcode instance** with the target workspace open — the bridge connects
to that process to fetch tools. Verify the binary resolves:

```bash
xcrun --find mcpbridge   # /Applications/Xcode.app/Contents/Developer/usr/bin/mcpbridge
```

If multiple Xcode instances are running, the bridge follows `xcode-select` (or
set `MCP_XCODE_PID` to pin a specific instance).

Verify both servers are connected with `/mcp` in Claude Code.
