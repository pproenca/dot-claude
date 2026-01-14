---
title: Avoid Spawning Tasks Everywhere
impact: MEDIUM
impactDescription: Maintains structured concurrency benefits
tags: async, task, structured, unstructured
---

## Avoid Spawning Tasks Everywhere

Unstructured tasks (`Task { }`) break structured concurrency, losing automatic cancellation and resource management. Use sparingly and intentionally.

**Incorrect (Tasks scattered throughout code):**

```swift
class DataManager {
    func updateData() {
        Task {
            let data = await fetchData()
            Task {
                await processData(data)
                Task {
                    await saveData(data)
                    // Nested Tasks - unstructured mess
                    // Cancellation doesn't propagate
                    // No parent-child relationship
                }
            }
        }
    }
}
```

**Correct (Structured async flow):**

```swift
class DataManager {
    // Clean structured async function
    func updateData() async {
        let data = await fetchData()
        await processData(data)
        await saveData(data)
        // Linear, cancellable, debuggable
    }

    // Single entry point for unstructured context (e.g., from button tap)
    func triggerUpdate() {
        Task {
            await updateData()
        }
    }
}

// When Tasks are appropriate:
// 1. Bridging from sync to async (UI actions, callbacks)
// 2. Fire-and-forget operations
// 3. When you explicitly need unstructured concurrency

// But prefer:
// - async let for parallel operations
// - TaskGroup for dynamic parallelism
// - Direct await for sequential operations
```

Reference: [Swift Concurrency - Structured Concurrency](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0304-structured-concurrency.md)
