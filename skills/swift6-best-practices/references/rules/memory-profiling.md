---
title: Profile Retain Cycles with Instruments
impact: CRITICAL
impactDescription: Identifies leaks static analysis misses
tags: memory, instruments, profiling, leaks
---

## Profile Retain Cycles with Instruments

Use Instruments' Leaks and Allocations tools to identify retain cycles that static analysis misses. Apps with unmanaged reference cycles experience up to 20-30% degraded responsiveness.

**Correct (Regular profiling workflow):**

```swift
// 1. Run with Leaks instrument in Xcode
// Product > Profile > Leaks

// 2. Exercise app features that create/destroy objects
// Navigate between screens, open/close views

// 3. Check for objects with unexpected lifetime
// Look for increasing allocations that don't decrease

// 4. Use Memory Graph Debugger for cycle visualization
// Debug > View Memory Graph Hierarchy

// Debug-only retain cycle detection
#if DEBUG
class LeakDetector {
    static var instances: Set<ObjectIdentifier> = []

    static func track(_ object: AnyObject) {
        instances.insert(ObjectIdentifier(object))
    }

    static func untrack(_ object: AnyObject) {
        instances.remove(ObjectIdentifier(object))
    }

    static func assertAllDeallocated() {
        assert(instances.isEmpty, "Potential retain cycle: \(instances.count) objects leaked")
    }
}

// Usage in classes
class MyViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        LeakDetector.track(self)
    }

    deinit {
        LeakDetector.untrack(self)
    }
}
#endif
```

Reference: [Xcode Instruments - Leaks](https://developer.apple.com/documentation/xcode/gathering-information-about-memory-use)
