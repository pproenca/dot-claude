---
title: Enable Strict Concurrency Incrementally
impact: CRITICAL
impactDescription: Manageable migration path to Swift 6
tags: concur, migration, incremental, strict
---

## Enable Strict Concurrency Incrementally

Migrate to Swift 6 concurrency module-by-module to avoid overwhelming changes. Large codebases can require thousands of annotations.

**Incorrect (Attempting full migration at once):**

```swift
// Enabling Swift 6 mode across entire large codebase
// Results in thousands of errors, migration becomes intractable
// Build settings: SWIFT_VERSION = 6.0 (globally)
```

**Correct (Incremental migration strategy):**

```swift
// Step 1: Enable warnings in Swift 5 mode per-module
// In build settings: Other Swift Flags = -strict-concurrency=complete

// Step 2: Fix warnings module by module, starting with leaf modules

// Step 3: Once a module is clean, switch it to Swift 6 language mode
// SWIFT_VERSION = 6.0 (per target)

// Step 4: Use @preconcurrency imports for dependencies not yet migrated
@preconcurrency import LegacyModule

// Real-world scale:
// - One team added 3,000+ @MainActor and Sendable annotations
// - Marked 400+ types as @unchecked Sendable after verification
// - Isolated entire modules with @preconcurrency for gradual progress
```

Reference: [Apple Developer Documentation - Adopting Swift 6](https://developer.apple.com/documentation/swift/adoptingswift6)
