---
title: Avoid Strong Self Capture in Long-Lived Closures
impact: CRITICAL
impactDescription: Prevents indefinite memory retention
tags: memory, closure, timer, observer
---

## Avoid Strong Self Capture in Long-Lived Closures

Closures stored for long periods (timers, observers, notification handlers) are especially prone to retain cycles that prevent deallocation.

**Incorrect (Timer holds strong reference indefinitely):**

```swift
class PollingService {
    var timer: Timer?

    func startPolling() {
        timer = Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { _ in
            // Strong capture: PollingService can never be deallocated
            self.poll()
        }
    }

    func poll() { }
}
```

**Correct (Weak capture allows deallocation):**

```swift
class PollingService {
    var timer: Timer?

    func startPolling() {
        timer = Timer.scheduledTimer(withTimeInterval: 5, repeats: true) { [weak self] _ in
            self?.poll()
        }
    }

    func stopPolling() {
        timer?.invalidate()
        timer = nil
    }

    func poll() { }

    deinit {
        stopPolling()
    }
}
```

Reference: [ARC in Swift - Best Practices to Avoid Memory Leaks](https://medium.com/@dhananjayshchauhan/arc-in-swift-best-practices-to-avoid-memory-leaks-353d5d3f1404)
