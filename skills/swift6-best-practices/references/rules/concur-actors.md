---
title: Prefer Actors Over Classes with Locks
impact: CRITICAL
impactDescription: Eliminates deadlocks and simplifies synchronization
tags: concur, actor, synchronization, locks
---

## Prefer Actors Over Classes with Locks

Actors provide built-in isolation without manual synchronization. They eliminate data races by design and produce cleaner code than lock-based approaches, while also preventing deadlocks.

**Incorrect (Manual synchronization with locks):**

```swift
class BankAccount {
    private var balance: Double = 0
    private let lock = NSLock()

    func deposit(_ amount: Double) {
        lock.lock()
        defer { lock.unlock() }
        balance += amount
    }

    func withdraw(_ amount: Double) -> Bool {
        lock.lock()
        defer { lock.unlock() }
        guard balance >= amount else { return false }
        balance -= amount
        return true
    }
}
```

**Correct (Actor with automatic isolation):**

```swift
actor BankAccount {
    private var balance: Double = 0

    func deposit(_ amount: Double) {
        balance += amount
    }

    func withdraw(_ amount: Double) -> Bool {
        guard balance >= amount else { return false }
        balance -= amount
        return true
    }
}

// Usage requires await
let account = BankAccount()
await account.deposit(100)
```

Reference: [WWDC24 - Migrate your app to Swift 6](https://developer.apple.com/videos/play/wwdc2024/10169/)
