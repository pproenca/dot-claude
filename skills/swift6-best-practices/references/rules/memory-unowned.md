---
title: Prefer unowned When Lifetime is Guaranteed
impact: CRITICAL
impactDescription: Less overhead than weak (no side table)
tags: memory, unowned, performance, lifetime
---

## Prefer unowned When Lifetime is Guaranteed

`unowned` has less overhead than `weak` (no side table, no optional unwrapping) when you can guarantee the referenced object outlives the closure.

**Incorrect (Using weak when unowned is safe):**

```swift
class Parent {
    var child: Child?

    func setupChild() {
        child = Child()
        child?.onAction = { [weak self] in
            // Child cannot outlive parent, weak adds unnecessary overhead
            self?.handleAction()
        }
    }
}
```

**Correct (unowned for guaranteed lifetime):**

```swift
class Parent {
    var child: Child?

    func setupChild() {
        child = Child()
        child?.onAction = { [unowned self] in
            // Parent always exists when child exists
            // No optional, no side table overhead
            self.handleAction()
        }
    }
}
```

**Warning:** Using `unowned` when the object can be deallocated causes a crash. Only use when lifetime is absolutely guaranteed.

Reference: [Swift Memory Management - Strong, Weak, and Unowned](https://www.vadimbulavin.com/swift-memory-management-arc-strong-weak-and-unowned/)
