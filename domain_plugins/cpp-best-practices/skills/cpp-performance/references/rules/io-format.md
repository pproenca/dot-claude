---
title: Use std::format Over String Concatenation
impact: MEDIUM
impactDescription: faster, type-safe, no allocation overhead
tags: io, format, strings, c++20, performance
---

## Use std::format Over String Concatenation

C++20 `std::format` is faster than iostreams and string concatenation while being type-safe. It pre-computes format string parsing at compile time.

**Incorrect (string concatenation - multiple allocations):**

```cpp
std::string buildMessage(const std::string& name, int id, double value) {
    // Multiple temporary strings and allocations
    return "User " + name + " (ID: " + std::to_string(id) +
           ") has value: " + std::to_string(value);
}

// iostream - slow
std::ostringstream ss;
ss << "User " << name << " (ID: " << id << ") has value: " << value;
std::string result = ss.str();
```

**Correct (std::format - efficient):**

```cpp
#include <format>

std::string buildMessage(const std::string& name, int id, double value) {
    return std::format("User {} (ID: {}) has value: {:.2f}", name, id, value);
}
```

**Format to existing buffer (zero allocation):**

```cpp
std::array<char, 256> buffer;
auto result = std::format_to(buffer.begin(),
    "User {} (ID: {}) has value: {:.2f}", name, id, value);
// result points to end of formatted string
*result = '\0';  // Null terminate if needed
```

**Format specifications:**

```cpp
// Width and alignment
std::format("{:10}", 42);        // "        42"
std::format("{:<10}", 42);       // "42        "
std::format("{:>10}", 42);       // "        42"
std::format("{:^10}", 42);       // "    42    "

// Numeric formatting
std::format("{:d}", 42);         // "42" (decimal)
std::format("{:x}", 42);         // "2a" (hex)
std::format("{:b}", 42);         // "101010" (binary)
std::format("{:e}", 3.14);       // "3.140000e+00"
std::format("{:.2f}", 3.14159);  // "3.14"

// Fill character
std::format("{:0>5}", 42);       // "00042"
```

**Print directly (C++23):**

```cpp
#include <print>

// Direct output, no intermediate string
std::print("User {} has value {:.2f}\n", name, value);
std::println("Same but with newline: {}", data);
```

**Custom type formatting:**

```cpp
struct Point { int x, y; };

template<>
struct std::formatter<Point> {
    constexpr auto parse(format_parse_context& ctx) {
        return ctx.begin();
    }

    auto format(const Point& p, format_context& ctx) const {
        return std::format_to(ctx.out(), "({}, {})", p.x, p.y);
    }
};

// Usage
Point p{3, 4};
std::print("Point: {}\n", p);  // "Point: (3, 4)"
```

Reference: [std::format](https://en.cppreference.com/w/cpp/utility/format/format)
