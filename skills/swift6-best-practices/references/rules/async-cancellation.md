---
title: Handle Cancellation Properly
impact: MEDIUM
impactDescription: Respects structured concurrency contract
tags: async, cancellation, cooperative, check
---

## Handle Cancellation Properly

Check for cancellation in long-running tasks to respect structured concurrency. Swift uses cooperative cancellation - tasks must check and respond.

**Incorrect (Ignoring cancellation):**

```swift
func processLargeDataset(_ items: [Item]) async throws -> [Result] {
    var results: [Result] = []
    for item in items {  // 1 million items
        let result = await process(item)
        results.append(result)
    }
    return results
    // Runs to completion even if parent was cancelled
    // Wastes resources, delays app shutdown
}
```

**Correct (Cooperative cancellation):**

```swift
func processLargeDataset(_ items: [Item]) async throws -> [Result] {
    var results: [Result] = []
    for item in items {
        // Check cancellation regularly in long loops
        try Task.checkCancellation()  // Throws CancellationError if cancelled
        let result = await process(item)
        results.append(result)
    }
    return results
}

// Or with cleanup before throwing
func processWithCleanup(_ items: [Item]) async throws -> [Result] {
    var results: [Result] = []
    for item in items {
        if Task.isCancelled {
            // Perform cleanup before exiting
            await cleanup(results)
            throw CancellationError()
        }
        results.append(await process(item))
    }
    return results
}

// For async sequences, cancellation often handled automatically
func processStream(_ stream: AsyncStream<Item>) async {
    for await item in stream {
        // Loop exits automatically when task is cancelled
        process(item)
    }
}
```

Reference: [Swift Concurrency - Task Cancellation](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html#ID642)
