---
title: Avoid Existentials in Hot Paths
impact: LOW-MEDIUM
impactDescription: Eliminates heap allocation and dynamic dispatch
tags: optim, existential, any, protocol
---

## Avoid Existentials in Hot Paths

Existential types (`any Protocol`) require heap allocation for large types and dynamic dispatch for all method calls. Use generics in performance-critical code.

**Incorrect (Existential in tight loop):**

```swift
protocol Processor {
    func process(_ value: Int) -> Int
}

func processAll(_ items: [Int], processor: any Processor) -> [Int] {
    return items.map { processor.process($0) }
    // Each call:
    // 1. Lookup method in witness table
    // 2. Call through function pointer
    // 3. Box/unbox values if needed
}
```

**Correct (Generic for static dispatch):**

```swift
protocol Processor {
    func process(_ value: Int) -> Int
}

func processAll<P: Processor>(_ items: [Int], processor: P) -> [Int] {
    return items.map { processor.process($0) }
    // With specialization:
    // 1. Direct method call
    // 2. Can be inlined
    // 3. No boxing
}

// Existential memory layout for reference:
// Small types (≤3 words): inline storage
// Large types: heap allocation + pointer

// When existentials are OK:
// - Heterogeneous collections that must store different types
// - Rare code paths (not hot loops)
// - API boundaries where flexibility matters more than speed

// Swift 5.7+ explicit syntax makes this clearer:
func slow(_ processor: any Processor) { }  // Existential
func fast<P: Processor>(_ processor: P) { }  // Generic
```

Reference: [WWDC24 - Explore Swift Performance](https://developer.apple.com/videos/play/wwdc2024/10217/)
