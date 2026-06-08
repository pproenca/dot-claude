---
name: ios-debugger-agent
description: Build, run, launch, and debug the current iOS project on a booted simulator with XcodeBuildMCP, and read build errors / run tests against the open Xcode workspace with XcodeBridge (xcrun mcpbridge). Trigger when asked to run an iOS app, interact with the simulator UI, inspect on-screen state, capture logs/console output, check whether the project builds, surface compiler errors, run tests, or diagnose runtime behavior.
---

# iOS Debugger Agent

## Overview
Use **XcodeBuildMCP** to build and run the current project scheme on a booted iOS simulator, interact with the UI, and capture logs. Prefer its MCP tools for simulator control, logs, and view inspection. Use **XcodeBridge** (Apple's `xcrun mcpbridge`) when you only need IDE-level build status, compiler errors, or test results from the open Xcode workspace — it is faster than a full simulator cycle but cannot control simulators or automate UI.

## Core Workflow
Follow this sequence unless the user asks for a narrower action.

### 1) Discover the booted simulator
- Call `mcp__XcodeBuildMCP__list_sims` and select the simulator with state `Booted`.
- If none are booted, ask the user to boot one (do not boot automatically unless asked).

### 2) Set session defaults
- Call `mcp__XcodeBuildMCP__session-set-defaults` with:
  - `projectPath` or `workspacePath` (whichever the repo uses)
  - `scheme` for the current app
  - `simulatorId` from the booted device
  - Optional: `configuration: "Debug"`, `useLatestOS: true`

### 3) Build + run (when requested)
- Call `mcp__XcodeBuildMCP__build_run_sim`.
- **If the build fails**, check the error output and retry (optionally with `preferXcodebuild: true`) or escalate to the user before attempting any UI interaction.
- **After a successful build**, verify the app launched by calling `mcp__XcodeBuildMCP__describe_ui` or `mcp__XcodeBuildMCP__screenshot` before proceeding to UI interaction.
- If the app is already built and only launch is requested, use `mcp__XcodeBuildMCP__launch_app_sim`.
- If bundle id is unknown:
  1) `mcp__XcodeBuildMCP__get_sim_app_path`
  2) `mcp__XcodeBuildMCP__get_app_bundle_id`

## UI Interaction & Debugging
Use these when asked to inspect or interact with the running app.

- **Describe UI**: `mcp__XcodeBuildMCP__describe_ui` before tapping or swiping.
- **Tap**: `mcp__XcodeBuildMCP__tap` (prefer `id` or `label`; use coordinates only if needed).
- **Type**: `mcp__XcodeBuildMCP__type_text` after focusing a field.
- **Gestures**: `mcp__XcodeBuildMCP__gesture` for common scrolls and edge swipes.
- **Screenshot**: `mcp__XcodeBuildMCP__screenshot` for visual confirmation.

## Logs & Console Output
- Start logs: `mcp__XcodeBuildMCP__start_sim_log_cap` with the app bundle id.
- Stop logs: `mcp__XcodeBuildMCP__stop_sim_log_cap` and summarize important lines.
- For console output, set `captureConsole: true` and relaunch if required.

## Xcode IDE Diagnostics (XcodeBridge)
The `XcodeBridge` server (Apple's `xcrun mcpbridge`) drives the **running Xcode
instance** on its active workspace. Use it for compiler/build feedback that is
faster or richer than the simulator flow — it requires Xcode to be open on the
target project, and cannot control simulators or automate UI.

- **Build the active scheme**: `mcp__XcodeBridge__BuildProject`, then read
  `mcp__XcodeBridge__GetBuildLog` for the full log.
- **List current issues**: `mcp__XcodeBridge__XcodeListNavigatorIssues` for the
  errors/warnings shown in Xcode's Issue Navigator.
- **Per-file diagnostics**: `mcp__XcodeBridge__XcodeRefreshCodeIssuesInFile`.
- **Run tests**: `mcp__XcodeBridge__RunAllTests` or
  `mcp__XcodeBridge__RunSomeTests` (use `mcp__XcodeBridge__GetTestList` first).
- **Prefer this over the simulator** when the user only needs to know whether
  the code builds, what the errors are, or whether tests pass — it avoids a full
  simulator boot/build/run cycle.

## Troubleshooting
- If build fails, ask whether to retry with `preferXcodebuild: true`.
- If the wrong app launches, confirm the scheme and bundle id.
- If UI elements are not hittable, re-run `describe_ui` after layout changes.
