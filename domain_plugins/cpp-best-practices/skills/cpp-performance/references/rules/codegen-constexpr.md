---
title: Use constexpr for Compile-Time Computation
impact: LOW-MEDIUM
impactDescription: moves computation from runtime to compile time
tags: codegen, constexpr, compile-time, optimization, c++20
---

## Use constexpr for Compile-Time Computation

`constexpr` functions and variables are evaluated at compile time when possible, eliminating runtime computation entirely.

**Incorrect (runtime computation):**

```cpp
// Computed every time at runtime
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// Array size determined at runtime
const int tableSize = 1 << 16;  // Runtime initialization
std::array<int, 65536> lookupTable;  // Can't use tableSize

void init() {
    for (int i = 0; i < factorial(10); ++i) {  // Computed at runtime
        // ...
    }
}
```

**Correct (compile-time computation):**

```cpp
// Computed at compile time
constexpr int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// Array size is compile-time constant
constexpr int tableSize = 1 << 16;
std::array<int, tableSize> lookupTable;

void init() {
    constexpr int limit = factorial(10);  // Computed at compile time
    for (int i = 0; i < limit; ++i) {
        // ...
    }
}

// Compile-time lookup table
constexpr auto makeTable() {
    std::array<int, 256> table{};
    for (int i = 0; i < 256; ++i) {
        table[i] = i * i;
    }
    return table;
}
constexpr auto squares = makeTable();  // Built at compile time
```

**consteval for guaranteed compile-time (C++20):**

```cpp
// MUST be evaluated at compile time
consteval int mustBeCompileTime(int n) {
    return n * n;
}

constexpr int a = mustBeCompileTime(5);  // OK
// int b = mustBeCompileTime(runtime_value);  // Error!
```

**constexpr algorithms (C++20):**

```cpp
constexpr std::array<int, 5> arr = {5, 3, 1, 4, 2};
constexpr auto sorted = [] {
    auto copy = arr;
    std::sort(copy.begin(), copy.end());  // constexpr in C++20
    return copy;
}();
// sorted is computed at compile time: {1, 2, 3, 4, 5}
```

**constexpr string operations (C++20):**

```cpp
constexpr std::string_view greet = "Hello";
constexpr size_t len = greet.length();  // Compile-time

constexpr bool startsWith(std::string_view str, std::string_view prefix) {
    return str.substr(0, prefix.size()) == prefix;
}

static_assert(startsWith("Hello, World", "Hello"));
```

**if constexpr for compile-time branching:**

```cpp
template<typename T>
auto process(T value) {
    if constexpr (std::is_integral_v<T>) {
        return value * 2;
    } else if constexpr (std::is_floating_point_v<T>) {
        return value * 2.5;
    } else {
        return value;
    }
}
```

Reference: [constexpr specifier](https://en.cppreference.com/w/cpp/language/constexpr)
