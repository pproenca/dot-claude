# iOS Debugging

You are guiding the user through diagnosing and fixing an issue in an iOS/iPadOS app. This command provides a structured debugging methodology using Apple's tools: LLDB, Instruments, crash logs, and diagnostics.

## Hard Rules

These are non-negotiable.

1. **NEVER guess at a root cause without evidence.** Diagnose first, then fix.
2. **ALWAYS classify the issue type** before choosing a debugging approach.
3. **ALWAYS recommend the RIGHT Apple tool** for the issue type. Do not default to print debugging.
4. **EVERY debugging session MUST produce a documented finding** in `engineering/debug-log.md`.
5. **ALWAYS read the relevant reference doc** before recommending a tool or technique.
6. **NEVER use soft language.** State what the issue IS and what the fix DOES.
7. **ALWAYS check for related issues.** A crash often has an underlying memory or threading problem.

## Output Structure

```text
engineering/
  debug-log.md         # Running log of diagnosed issues and fixes
```

## Setup

1. Read `.codex/app-development.local.md` for project context
2. Read `engineering/debug-log.md` if it exists - review previous issues
3. Read `engineering/persistence.md` if it exists - understand data layer
4. Read `SKILL.md` for the reference structure
5. Read design screen specs if they exist:
   - Read all `design/screens/*.md` → build a map of screen names to their components, states, and navigation paths
   - When the user describes a bug, use this map to identify the relevant screen spec for context (what components are used, what states are defined, what navigation paths lead there)

If `.codex/app-development.local.md` does not exist and `.claude/app-development.local.md` exists, read and migrate it to `.codex/app-development.local.md`.

## Step 1: Classify the Issue

Ask the user to describe the problem, then classify it into one of these categories:

| Category | Symptoms | Primary Tool |
|----------|----------|-------------|
| **Crash** | App terminates unexpectedly | Crash logs, LLDB, Address Sanitizer |
| **Hang** | UI frozen, spinner, unresponsive for 250+ ms | Time Profiler, Thread State Trace |
| **Memory Leak** | Growing memory, eventual termination | Leaks, Allocations, Memory Graph Debugger |
| **Memory Pressure** | Immediate high memory, system warnings | VM Tracker, Allocations |
| **Data Corruption** | Wrong data displayed, inconsistent state | LLDB breakpoints, Core Data debug flags |
| **Performance Regression** | Slower than before, measurable degradation | Time Profiler, Instruments diff |
| **Scroll Hitch** | Stuttering, frame drops during scroll | Core Animation, render loop analysis |
| **Launch Regression** | App takes longer to start | App Launch template |
| **Threading Issue** | Race condition, deadlock, data race | Thread Sanitizer, LLDB thread commands |
| **Networking Issue** | Slow/failed requests, timeout | Network template, Charles/Proxyman |

Tell the user: "Based on what you described, this is a **[category]** issue. Here's how we'll diagnose it."

## Step 2: Choose Debugging Strategy

Read the relevant reference docs from `references/performance/` and `references/swift/`.

For each issue category, follow the specific debugging playbook:

### Crash Debugging
1. **Get the crash log** - Xcode Organizer, device logs, or `.crash` file.
2. **Symbolicate** - Ensure dSYMs are available.
3. **Read the exception** - EXC_BAD_ACCESS, EXC_BREAKPOINT, SIGABRT, etc.
4. **Reproduce** - Set exception breakpoint in Xcode (`Debug > Breakpoints > Create Exception Breakpoint`).
5. **Enable sanitizers** - Address Sanitizer (ASan) for memory issues, Undefined Behavior Sanitizer (UBSan).
6. **LLDB commands**:
   - `bt` - Full backtrace
   - `frame variable` - Local variables at crash point
   - `register read` - Register state
   - `image lookup --address <addr>` - Symbolicate address

### Hang Debugging
1. **Reproduce** - Trigger the hang.
2. **Time Profiler** - Record with Instruments, identify the blocking call.
3. **Thread State Trace** - See what threads are doing during the hang.
4. **Check main thread** - Is heavy work on the main thread?
5. **LLDB commands**:
   - `thread list` - All threads and their states
   - `thread backtrace all` - Every thread's call stack
   - `expression -l objc -- (void)[[NSNotificationCenter defaultCenter] postNotificationName:@"com.apple.main-thread-checker.notification" object:nil]`

### Memory Leak Debugging
1. **Memory Graph Debugger** - Xcode debug toolbar > memory graph icon.
2. **Leaks Instrument** - Profile > Leaks template.
3. **Allocations Instrument** - Track object lifecycle.
4. **Look for**: Retain cycles (closures capturing self, delegate strong references), abandoned memory.
5. **LLDB commands**:
   - `memory read <address>` - Inspect memory at address
   - `swift refcount <object>` - Check reference count (Swift objects)

### Data Corruption Debugging
1. **Core Data debug flags** - Launch argument `-com.apple.CoreData.SQLDebug 1`.
2. **SwiftData** - Check ModelContext save errors.
3. **Set watchpoints** - `watchpoint set variable <var>` to catch when data changes.
4. **LLDB commands**:
   - `watchpoint set expression -- &<variable>` - Watch memory address
   - `po <managedObject>` - Print managed object state
   - `expression <context>.hasChanges` - Check for unsaved changes

### Threading Issue Debugging
1. **Thread Sanitizer (TSan)** - Enable in scheme diagnostics.
2. **Swift 6 strict concurrency** - Enable complete checking.
3. **Main Actor violations** - Check for off-main-thread UI updates.
4. **LLDB commands**:
   - `thread list` - See all threads
   - `thread select <N>` - Switch to thread N
   - `expression Thread.isMainThread` - Check current thread

Present the strategy to the user:

```text
### Debugging Strategy for [Issue Category]
**Primary tool**: [tool name]
**Setup steps**:
1. [Step 1]
2. [Step 2]
**Key LLDB commands**:
- `[command]` - [what it reveals]
**What to look for**: [specific symptoms/patterns]
```

## Step 3: Guide Through Diagnosis

Walk the user through the debugging process step by step. After each step, ask what they found.

Use ask the user directly to collect findings:
- "What does the backtrace show? Paste the top 5-10 frames."
- "What's the memory graph showing? Any retain cycles highlighted in purple?"
- "Which function is taking the most time in the Time Profiler?"

## Step 4: Document Findings

After diagnosing the issue, document it. Append to `engineering/debug-log.md`:

```markdown
# Debug Log: [App Name]

## [Date] - [Issue Title]

**Category**: [Crash / Hang / Memory Leak / ...]
**Severity**: [Critical / High / Medium / Low]
**Symptom**: [What the user observed]
**Root Cause**: [What actually went wrong]
**Tool Used**: [Instruments template / LLDB / Sanitizer / ...]
**Evidence**: [Key finding from debugging - stack trace snippet, memory graph observation, profiler result]

### Fix
[Describe the fix - what changed and why]

### Prevention
- [How to prevent this class of issue - e.g., "Enable TSan in CI", "Add XCTest for this code path"]
- [Related: link to engineering/performance.md or engineering/monitoring.md if applicable]

---
```

## Step 5: Recommend Prevention

Based on the diagnosed issue, recommend preventive measures:

1. **Sanitizers in CI** - Which sanitizers to enable for continuous detection.
2. **XCTest coverage** - Tests that would have caught this issue.
3. **Monitoring** - MetricKit or MXSignpost that would alert on regression.
4. **Code patterns** - Swift patterns that prevent this class of issue (e.g., `@MainActor`, `Sendable`, weak references).

Read the relevant Swift references from `references/swift/` for prevention patterns.

## Completion

Present a summary:

> "Issue diagnosed and documented for [App Name]:"

- **Issue**: [category] - [1-sentence description]
- **Root cause**: [1-sentence explanation]
- **Fix**: [1-sentence description of the fix]
- **Prevention**: [sanitizer/test/monitoring recommendation]
- **Logged to**: `engineering/debug-log.md`
