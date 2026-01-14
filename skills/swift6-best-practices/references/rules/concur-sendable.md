---
title: Conform Types to Sendable
impact: CRITICAL
impactDescription: Enables compile-time data-race detection
tags: concur, sendable, threading, isolation
---

## Conform Types to Sendable

Types passed across isolation boundaries must conform to `Sendable`. This ensures the compiler can verify thread-safe access and prevents data races at compile time.

**Incorrect (Non-Sendable type crossing boundaries):**

```swift
class UserData {
    var name: String
    var age: Int

    init(name: String, age: Int) {
        self.name = name
        self.age = age
    }
}

func processUser(_ user: UserData) async {
    await Task.detached {
        // Error: UserData is not Sendable
        print(user.name)
    }.value
}
```

**Correct (Use Sendable struct or mark class correctly):**

```swift
// Option 1: Use a struct (implicitly Sendable if all properties are)
struct UserData: Sendable {
    let name: String
    let age: Int
}

// Option 2: Final class with immutable properties
final class UserData: Sendable {
    let name: String
    let age: Int

    init(name: String, age: Int) {
        self.name = name
        self.age = age
    }
}

// Option 3: Use @unchecked Sendable with manual synchronization
final class UserData: @unchecked Sendable {
    private let queue = DispatchQueue(label: "userData")
    private var _name: String

    var name: String {
        queue.sync { _name }
    }
}
```

Reference: [Swift.org - Enabling Complete Concurrency Checking](https://www.swift.org/documentation/concurrency/)
