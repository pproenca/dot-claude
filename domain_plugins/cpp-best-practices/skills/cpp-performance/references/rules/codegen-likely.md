---
title: Use Branch Prediction Hints for Hot Paths
impact: LOW-MEDIUM
impactDescription: improves branch prediction accuracy
tags: codegen, likely, unlikely, branch-prediction, c++20
---

## Use Branch Prediction Hints for Hot Paths

Use `[[likely]]` and `[[unlikely]]` (C++20) to hint expected branch outcomes, helping the compiler generate more efficient code for hot paths.

**Incorrect (no hints on critical branches):**

```cpp
void processData(Data* data) {
    if (data == nullptr) {  // Rarely true
        handleError();
        return;
    }
    // Hot path continues...
    process(data);
}

switch (type) {
    case COMMON_TYPE:
        handleCommon();  // 99% of cases
        break;
    case RARE_TYPE:
        handleRare();  // 1% of cases
        break;
}
```

**Correct (branch hints):**

```cpp
void processData(Data* data) {
    if (data == nullptr) [[unlikely]] {
        handleError();
        return;
    }
    // Compiler optimizes for this path
    process(data);
}

switch (type) {
    [[likely]] case COMMON_TYPE:
        handleCommon();
        break;
    case RARE_TYPE:
        handleRare();
        break;
}
```

**Pre-C++20 compiler intrinsics:**

```cpp
// GCC/Clang
#define LIKELY(x)   __builtin_expect(!!(x), 1)
#define UNLIKELY(x) __builtin_expect(!!(x), 0)

if (UNLIKELY(error)) {
    handleError();
}

// MSVC - use /O2 optimization and PGO
```

**Error handling patterns:**

```cpp
std::optional<Result> tryOperation() {
    if (auto result = attemptFast(); result) [[likely]] {
        return result;
    }
    // Fallback only when fast path fails
    return attemptSlow();
}

void validateInput(const Request& req) {
    if (!req.isValid()) [[unlikely]] {
        throw InvalidRequestError{};
    }
    // Normal processing...
}
```

**Loop patterns:**

```cpp
void processItems(const std::vector<Item>& items) {
    for (const auto& item : items) {
        if (item.needsSpecialHandling()) [[unlikely]] {
            handleSpecial(item);
            continue;
        }
        // Fast path for normal items
        processNormal(item);
    }
}
```

**When to use:**
- Error checking (errors are unlikely)
- Null pointer checks
- Bounds validation
- Feature flags (one branch dominates)
- Type dispatch (one type is common)

**When NOT to use:**
- 50/50 branches
- Branches that vary by input
- Cold code (doesn't matter)

Reference: [C++20 [[likely]] and [[unlikely]]](https://en.cppreference.com/w/cpp/language/attributes/likely)
