---
title: Use Typed Throws for Exhaustive Handling
impact: LOW
impactDescription: Compiler-verified exhaustive error handling
tags: error, typed-throws, exhaustive, swift6
---

## Use Typed Throws for Exhaustive Handling

Typed throws in Swift 6 allow switch-based error handling with compiler-verified exhaustiveness. No catch-all required when all cases are handled.

**Incorrect (Untyped throws requires catch-all):**

```swift
enum ParseError: Error {
    case invalidSyntax
    case unexpectedEOF
}

func parse(_ input: String) throws -> AST {
    // throws any Error
}

do {
    let ast = try parse(input)
} catch let error as ParseError {
    // Handle known errors
    switch error {
    case .invalidSyntax: handleSyntaxError()
    case .unexpectedEOF: handleEOF()
    }
} catch {
    // Must have catch-all for unknown errors
    handleUnknownError(error)
}
```

**Correct (Typed throws for exhaustive handling):**

```swift
enum ParseError: Error {
    case invalidSyntax
    case unexpectedEOF
}

func parse(_ input: String) throws(ParseError) -> AST {
    // Only throws ParseError - compiler knows this
    guard !input.isEmpty else {
        throw .unexpectedEOF
    }
    // ...
}

do {
    let ast = try parse(input)
} catch .invalidSyntax {
    handleSyntaxError()
} catch .unexpectedEOF {
    handleEOF()
}
// No catch-all needed - compiler knows all cases handled

// Also enables pattern matching
do {
    try parse(input)
} catch .invalidSyntax {
    // Handle specific case
}
// Other cases propagate automatically
```

Reference: [Swift Evolution SE-0413 - Typed throws](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0413-typed-throws.md)
