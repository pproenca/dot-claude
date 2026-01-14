---
title: Use TaskGroup with Backpressure
impact: MEDIUM
impactDescription: Controlled parallelism prevents resource exhaustion
tags: async, taskgroup, backpressure, concurrency
---

## Use TaskGroup with Backpressure

Control concurrency with backpressure to avoid overwhelming resources like network connections, file handles, or memory.

**Incorrect (Unbounded parallelism):**

```swift
func processAllImages(_ urls: [URL]) async throws -> [ProcessedImage] {
    try await withThrowingTaskGroup(of: ProcessedImage.self) { group in
        for url in urls {
            group.addTask {
                try await self.downloadAndProcess(url)
            }
        }
        // All 10,000 downloads start simultaneously!
        // May exhaust connections, memory, or hit rate limits
        return try await group.reduce(into: []) { $0.append($1) }
    }
}
```

**Correct (Controlled parallelism with backpressure):**

```swift
func processAllImages(_ urls: [URL]) async throws -> [ProcessedImage] {
    try await withThrowingTaskGroup(of: ProcessedImage.self) { group in
        var results: [ProcessedImage] = []
        var iterator = urls.makeIterator()
        let maxConcurrent = 4

        // Start initial batch
        for _ in 0..<min(maxConcurrent, urls.count) {
            if let url = iterator.next() {
                group.addTask { try await self.downloadAndProcess(url) }
            }
        }

        // As each completes, start another (backpressure)
        for try await result in group {
            results.append(result)
            if let url = iterator.next() {
                group.addTask { try await self.downloadAndProcess(url) }
            }
        }

        return results
    }
}

// Benefits:
// - Maximum of 4 concurrent operations
// - Memory usage stays bounded
// - Network connections stay reasonable
// - Respects rate limits
```

Reference: [Swift Concurrency - TaskGroup](https://www.donnywals.com/swift-concurrencys-taskgroup-explained/)
