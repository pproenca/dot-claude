---
title: Prefer make_unique and make_shared Over new
impact: CRITICAL
impactDescription: exception-safe, more efficient allocation
tags: memory, make_unique, make_shared, allocation, exception-safety
---

## Prefer make_unique and make_shared Over new

Using `std::make_unique` and `std::make_shared` is exception-safe, more efficient, and clearer than using `new` directly. `make_shared` performs a single allocation for both the object and control block.

**Incorrect (direct new - exception unsafe):**

```cpp
void createWidgets() {
    // Exception-unsafe: if second new throws, first leaks
    processWidgets(
        std::shared_ptr<Widget>(new Widget()),
        std::shared_ptr<Widget>(new Widget())
    );
}

// Two allocations: object + control block
auto ptr = std::shared_ptr<Data>(new Data());
```

**Correct (make functions):**

```cpp
void createWidgets() {
    // Exception-safe: no intermediate raw pointers
    processWidgets(
        std::make_shared<Widget>(),
        std::make_shared<Widget>()
    );
}

// Single allocation: object and control block together
auto ptr = std::make_shared<Data>();

// For unique_ptr
auto unique = std::make_unique<Data>();

// With constructor arguments
auto widget = std::make_unique<Widget>(42, "name");
```

**When NOT to use make_shared:**

```cpp
// Custom deleter required
auto file = std::shared_ptr<FILE>(
    fopen("data.txt", "r"),
    [](FILE* f) { if (f) fclose(f); }
);

// Weak pointers outlive shared pointers (memory not released)
// In this case, separate allocations may be preferred
```

Reference: [C++ Core Guidelines R.22](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#r22-use-make_shared-to-make-shared_ptrs)
