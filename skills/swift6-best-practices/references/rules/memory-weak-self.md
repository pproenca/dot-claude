---
title: Use weak self in Escaping Closures
impact: CRITICAL
impactDescription: Prevents retain cycles and memory leaks
tags: memory, weak, closure, retain-cycle
---

## Use weak self in Escaping Closures

Closures capture references strongly by default. Use `[weak self]` to prevent retain cycles that cause memory leaks.

**Incorrect (Strong capture creates retain cycle):**

```swift
class NetworkManager {
    var onDataReceived: ((Data) -> Void)?

    func startListening() {
        onDataReceived = { data in
            // Strong capture: self -> onDataReceived -> closure -> self
            self.processData(data)
        }
    }

    func processData(_ data: Data) { }
}
```

**Correct (Weak capture breaks the cycle):**

```swift
class NetworkManager {
    var onDataReceived: ((Data) -> Void)?

    func startListening() {
        onDataReceived = { [weak self] data in
            guard let self else { return }
            self.processData(data)
        }
    }

    func processData(_ data: Data) { }
}
```

Reference: [Apple Developer Documentation - ARC](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/automaticreferencecounting/)
