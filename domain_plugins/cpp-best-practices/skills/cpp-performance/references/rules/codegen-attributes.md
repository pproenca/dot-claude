---
title: Use Standard Attributes to Guide Compiler Optimization
impact: LOW-MEDIUM
impactDescription: prevents bugs, enables better warnings, guides optimizer
tags: codegen, attributes, nodiscard, maybe_unused, deprecated, optimization
---

## Use Standard Attributes to Guide Compiler Optimization

C++ standard attributes provide hints to the compiler for optimization and static analysis. They help catch bugs at compile time and improve code generation.

**Incorrect (missing important attributes):**

```cpp
// Return value silently ignored
ErrorCode initialize();
void setup() {
    initialize();  // Error code discarded - bug!
}

// Unused parameter warning
void callback(int event, [[maybe_unused]] void* userData) {
    // userData unused but that's intentional
}

// Pure function not marked
int square(int x) {
    return x * x;  // No side effects
}
```

**Correct (using standard attributes):**

```cpp
// [[nodiscard]] prevents ignored return values
[[nodiscard]] ErrorCode initialize();
void setup() {
    auto result = initialize();  // Must handle!
    if (result != ErrorCode::OK) { /* handle */ }
}

// [[maybe_unused]] suppresses warnings intentionally
void callback(int event, [[maybe_unused]] void* userData) {
    // Clearly intentionally unused
}

// [[nodiscard]] with message (C++20)
[[nodiscard("Memory must be freed")]]
void* allocate(size_t size);
```

**Other useful attributes:**

```cpp
// [[deprecated]] for API migration
[[deprecated("Use newFunction() instead")]]
void oldFunction();

// [[fallthrough]] in switch statements
switch (value) {
    case 1:
        prepare();
        [[fallthrough]];  // Intentional fallthrough
    case 2:
        execute();
        break;
}

// [[likely]]/[[unlikely]] for branch prediction (C++20)
if (error) [[unlikely]] {
    handleError();
}
```

**Compiler-specific attributes for optimization:**

```cpp
// GCC/Clang: Pure functions (no side effects, only reads memory)
[[gnu::pure]] int lookup(const Table* t, int key);

// GCC/Clang: Const functions (only reads arguments)
[[gnu::const]] int square(int x);

// Force inline
[[gnu::always_inline]] inline int fastPath(int x);
```

Reference: [cppreference Attributes](https://en.cppreference.com/w/cpp/language/attributes)
