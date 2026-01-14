---
title: Replace DispatchGroup with TaskGroup
impact: MEDIUM
impactDescription: Native async with better cancellation
tags: async, taskgroup, dispatchgroup, migration
---

## Replace DispatchGroup with TaskGroup

TaskGroup provides the same functionality as DispatchGroup with better cancellation support, type safety, and integration with Swift concurrency.

**Incorrect (DispatchGroup with async code):**

```swift
func fetchAllData() async -> [Data] {
    let group = DispatchGroup()
    var results: [Data] = []
    let lock = NSLock()

    for url in urls {
        group.enter()
        Task {
            let data = try? await fetch(url)
            lock.lock()
            if let data { results.append(data) }
            lock.unlock()
            group.leave()
        }
    }

    group.wait()  // Blocks thread!
    return results
}
```

**Correct (TaskGroup is native to async):**

```swift
func fetchAllData() async -> [Data] {
    await withTaskGroup(of: Data?.self) { group in
        for url in urls {
            group.addTask {
                try? await fetch(url)
            }
        }

        var results: [Data] = []
        for await data in group {
            if let data { results.append(data) }
        }
        return results
    }
}

// Benefits over DispatchGroup:
// - No manual enter/leave pairing
// - No locks needed (actor isolation)
// - Non-blocking await
// - Automatic cancellation propagation
// - Type-safe results

// For throwing tasks:
func fetchAllDataThrowing() async throws -> [Data] {
    try await withThrowingTaskGroup(of: Data.self) { group in
        for url in urls {
            group.addTask {
                try await fetch(url)
            }
        }
        return try await group.reduce(into: []) { $0.append($1) }
    }
}
```

Reference: [Swift Concurrency - Structured Concurrency](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0304-structured-concurrency.md)
