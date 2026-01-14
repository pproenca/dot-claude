---
title: Choose Semantics Based on Identity
impact: MEDIUM-HIGH
impactDescription: Right type for right purpose
tags: value, identity, class, struct
---

## Choose Semantics Based on Identity

Use classes when identity matters (the specific instance), structs when value matters (the data content).

**Incorrect (Struct for identity-based entity):**

```swift
struct Window {
    var title: String
    var frame: CGRect

    func close() {
        // Which window? Copies don't share identity
        // Can't track "this specific window"
    }
}

var window1 = Window(title: "Settings", frame: .zero)
var window2 = window1  // Copy - now two independent "windows"
window1.title = "Preferences"  // Only window1 changes
// window2 is a completely separate entity
```

**Correct (Class for identity, struct for data):**

```swift
// Identity matters - use class
class Window {
    var title: String
    var frame: CGRect

    init(title: String, frame: CGRect) {
        self.title = title
        self.frame = frame
    }

    func close() {
        // This specific window instance
        WindowManager.shared.close(self)
    }
}

// Value matters - use struct
struct WindowConfiguration {
    var title: String
    var frame: CGRect
    var isResizable: Bool
}

// Use struct for configuration, class for the actual window
let config = WindowConfiguration(title: "Settings", frame: .zero, isResizable: true)
let window = Window(configuration: config)

// Identity comparison
let window1 = Window(title: "A", frame: .zero)
let window2 = window1
print(window1 === window2)  // true - same instance
```

Reference: [Choosing Between Structures and Classes - Apple Developer](https://developer.apple.com/documentation/swift/choosing-between-structures-and-classes)
