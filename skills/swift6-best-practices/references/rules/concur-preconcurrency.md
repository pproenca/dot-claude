---
title: Apply @preconcurrency for Legacy Protocols
impact: CRITICAL
impactDescription: Bridges old APIs with Swift 6 concurrency
tags: concur, preconcurrency, delegate, migration
---

## Apply @preconcurrency for Legacy Protocols

When conforming to delegate protocols that assume main actor context, use `@preconcurrency` to bridge the gap between legacy APIs and Swift 6 strict concurrency.

**Incorrect (Delegate methods without isolation handling):**

```swift
@MainActor
class MyViewController: UIViewController, UITableViewDelegate {
    var selectedItems: [Item] = []

    // Warning: Protocol method may be called from any thread
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        selectedItems.append(items[indexPath.row])
    }
}
```

**Correct (@preconcurrency assumes main actor):**

```swift
@MainActor
class MyViewController: UIViewController, @preconcurrency UITableViewDelegate {
    var selectedItems: [Item] = []

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        // @preconcurrency assumes this is called on the main actor
        // Will trap at runtime if called from wrong context
        selectedItems.append(items[indexPath.row])
    }
}
```

Reference: [WWDC24 - Migrate your app to Swift 6](https://developer.apple.com/videos/play/wwdc2024/10169/)
