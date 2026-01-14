---
title: Use string_view for Non-Owning String Parameters
impact: HIGH
impactDescription: eliminates temporary string allocations
tags: memory, string_view, strings, allocation, parameters
---

## Use string_view for Non-Owning String Parameters

Use `std::string_view` for function parameters that only read strings. It avoids allocations when called with string literals or substrings, and works with both `std::string` and `const char*`.

**Incorrect (forces allocation):**

```cpp
// Forces allocation when called with string literal
void log(const std::string& message) {
    std::cout << message << std::endl;
}

bool startsWith(const std::string& str, const std::string& prefix) {
    return str.compare(0, prefix.size(), prefix) == 0;
}

// Usage - allocates temporary std::string
log("Hello, world!");  // Allocates!
startsWith(myString, "prefix");  // Allocates for "prefix"!
```

**Correct (no allocation):**

```cpp
// No allocation for any string type
void log(std::string_view message) {
    std::cout << message << std::endl;
}

bool startsWith(std::string_view str, std::string_view prefix) {
    return str.size() >= prefix.size() &&
           str.compare(0, prefix.size(), prefix) == 0;
}

// Usage - no allocations
log("Hello, world!");  // No allocation
log(myStdString);      // No allocation
startsWith(myString, "prefix");  // No allocation
```

**Substring operations without allocation:**

```cpp
std::string_view fullPath = "/home/user/documents/file.txt";
auto filename = fullPath.substr(fullPath.rfind('/') + 1);
// filename is "file.txt" - no allocation, just pointer + length
```

**When NOT to use string_view:**

```cpp
class Config {
    // Need to store the string - use std::string
    std::string filename_;  // NOT string_view

public:
    void setFilename(std::string_view name) {
        filename_ = name;  // Convert to owning string for storage
    }
};
```

**Warning:** `string_view` does not own the data - ensure the underlying string outlives the view.

Reference: [C++ Core Guidelines SL.str.2](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#slstr2-use-stdstring_view-or-gslstring_span-to-refer-to-character-sequences)
