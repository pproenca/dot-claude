---
title: Use autoreleasepool in Tight Loops
impact: CRITICAL
impactDescription: Prevents memory pressure in loops
tags: memory, autoreleasepool, loop, objc
---

## Use autoreleasepool in Tight Loops

When working with Objective-C objects in tight loops, autoreleasepool prevents memory from accumulating until the loop ends.

**Incorrect (Memory builds up during loop):**

```swift
func processImages(_ urls: [URL]) {
    for url in urls {
        // Autoreleased objects accumulate until loop ends
        let image = UIImage(contentsOfFile: url.path)
        processImage(image)
    }
    // All memory released here, could cause memory pressure
}
```

**Correct (autoreleasepool drains each iteration):**

```swift
func processImages(_ urls: [URL]) {
    for url in urls {
        autoreleasepool {
            let image = UIImage(contentsOfFile: url.path)
            processImage(image)
        }
        // Memory released immediately after each iteration
    }
}
```

Reference: [Swift Memory Optimization](https://www.compilenrun.com/docs/language/swift/swift-best-practices/swift-memory-optimization/)
