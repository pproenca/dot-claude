---
title: Reserve Task.detached for Special Cases
impact: MEDIUM
impactDescription: Preserves actor context by default
tags: async, detached, context, priority
---

## Reserve Task.detached for Special Cases

`Task.detached` creates tasks without inheriting actor context or priority. Use only when you specifically need to escape the current context.

**Incorrect (Task.detached by default):**

```swift
@MainActor
class ViewController {
    func processInBackground() {
        Task.detached {
            // Loses @MainActor context
            // Have to manually return to main actor
            let result = await self.compute()
            await MainActor.run {
                self.display(result)  // Extra boilerplate
            }
        }
    }
}
```

**Correct (Regular Task inherits context):**

```swift
@MainActor
class ViewController {
    func processInBackground() {
        Task {
            // Inherits @MainActor context
            let result = await compute()
            display(result)  // Already on main actor
        }
    }

    // Task.detached only when you NEED different behavior:

    // 1. Need different priority
    func lowPriorityWork() {
        Task.detached(priority: .background) {
            await self.heavyComputation()
        }
    }

    // 2. Need to escape actor isolation intentionally
    func cpuIntensiveWork() {
        Task.detached {
            // Runs on concurrent executor, not main actor
            let result = await self.crunchNumbers()
            await MainActor.run {
                self.updateUI(result)
            }
        }
    }
}
```

Reference: [SwiftLee - Async/await in Swift](https://www.avanderlee.com/swift/async-await/)
