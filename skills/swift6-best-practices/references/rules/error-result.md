---
title: Leverage Result for Synchronous Errors
impact: LOW
impactDescription: Explicit success/failure without throwing
tags: error, result, synchronous, handling
---

## Leverage Result for Synchronous Errors

`Result` is useful for synchronous code that needs explicit error handling, especially in callbacks or when you want to store or pass around outcomes.

**Incorrect (Throwing in callback context):**

```swift
func validate(_ input: String, completion: (String?, Error?) -> Void) {
    if input.isEmpty {
        completion(nil, ValidationError.empty)
    } else {
        completion(input.uppercased(), nil)
    }
}

// Awkward to use:
validate(input) { result, error in
    if let error {
        handleError(error)
    } else if let result {
        use(result)
    }
    // What if both nil? What if both non-nil?
}
```

**Correct (Result for explicit success/failure):**

```swift
enum ValidationError: Error {
    case empty
    case tooLong
    case invalidCharacters
}

func validate(_ input: String) -> Result<String, ValidationError> {
    if input.isEmpty {
        return .failure(.empty)
    }
    if input.count > 100 {
        return .failure(.tooLong)
    }
    return .success(input.uppercased())
}

// Clean usage with switch
switch validate(input) {
case .success(let value):
    use(value)
case .failure(let error):
    handleError(error)
}

// Or with get() for throwing context
do {
    let validated = try validate(input).get()
    use(validated)
} catch {
    handleError(error)
}

// Storing outcomes
var outcomes: [Result<Data, NetworkError>] = []
outcomes.append(fetchResult)

// Transforming results
let mapped = validate(input).map { $0.lowercased() }
let flatMapped = validate(input).flatMap { furtherValidate($0) }
```

Reference: [Swift Standard Library - Result](https://developer.apple.com/documentation/swift/result)
