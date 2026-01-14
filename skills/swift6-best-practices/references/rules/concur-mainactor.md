---
title: Use @MainActor for UI-Bound Code
impact: CRITICAL
impactDescription: Eliminates UI thread violations at compile time
tags: concur, mainactor, ui, threading
---

## Use @MainActor for UI-Bound Code

All UI updates must occur on the main thread. In Swift 6, annotating types or methods with `@MainActor` ensures the compiler enforces this at compile time, eliminating runtime crashes from thread violations.

**Incorrect (UI code without actor isolation):**

```swift
class ProfileViewController: UIViewController {
    var userName: String = ""

    func fetchAndDisplayUser() async {
        let user = await userService.fetchUser()
        // Potential data race: accessing userName from background thread
        userName = user.name
        nameLabel.text = userName
    }
}
```

**Correct (@MainActor ensures UI safety):**

```swift
@MainActor
class ProfileViewController: UIViewController {
    var userName: String = ""

    func fetchAndDisplayUser() async {
        let user = await userService.fetchUser()
        // Guaranteed to run on main actor
        userName = user.name
        nameLabel.text = userName
    }
}
```

Reference: [Apple Developer Documentation - Adopting Swift 6](https://developer.apple.com/documentation/swift/adoptingswift6)
