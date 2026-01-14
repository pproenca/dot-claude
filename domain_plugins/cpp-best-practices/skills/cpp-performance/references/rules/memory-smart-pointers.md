---
title: Use Smart Pointers Over Raw Pointers
impact: CRITICAL
impactDescription: eliminates memory leaks and dangling pointers
tags: memory, smart-pointers, raii, ownership, unique_ptr, shared_ptr
---

## Use Smart Pointers Over Raw Pointers

Raw pointers require manual memory management and are prone to leaks, double-frees, and dangling pointer bugs. Use `std::unique_ptr` for exclusive ownership and `std::shared_ptr` for shared ownership.

**Incorrect (manual memory management):**

```cpp
class ResourceManager {
    Data* data_;
public:
    ResourceManager() : data_(new Data()) {}

    ~ResourceManager() {
        delete data_;  // Easy to forget, exception-unsafe
    }

    // Missing copy/move operations - rule of 5 violation
};

void processData() {
    Data* data = new Data();
    process(data);
    // If process() throws, memory leaks
    delete data;
}
```

**Correct (RAII with smart pointers):**

```cpp
class ResourceManager {
    std::unique_ptr<Data> data_;
public:
    ResourceManager() : data_(std::make_unique<Data>()) {}
    // Destructor, copy, move automatically handled correctly
};

void processData() {
    auto data = std::make_unique<Data>();
    process(data.get());
}  // Automatically deleted, even if exception thrown
```

**Choosing the right smart pointer:**

```cpp
// Exclusive ownership - use unique_ptr (zero overhead)
auto exclusive = std::make_unique<Widget>();

// Shared ownership - use shared_ptr (reference counting overhead)
auto shared = std::make_shared<Widget>();

// Non-owning reference to shared_ptr - use weak_ptr
std::weak_ptr<Widget> weak = shared;
```

Reference: [C++ Core Guidelines R.20](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#r20-use-unique_ptr-or-shared_ptr-to-represent-ownership)
