---
title: Use Concepts for Clear Template Constraints
impact: LOW
impactDescription: better errors, clearer code, faster compilation
tags: template, concepts, constraints, c++20, type-traits
---

## Use Concepts for Clear Template Constraints

C++20 concepts replace SFINAE with readable constraints, providing clearer error messages and faster compilation.

**Incorrect (SFINAE - cryptic errors):**

```cpp
// Hard to read, produces terrible error messages
template<typename T,
         typename = std::enable_if_t<
             std::is_arithmetic_v<T> &&
             !std::is_same_v<T, bool>>>
T add(T a, T b) {
    return a + b;
}

// Error message when called with string:
// "no matching function for call to 'add(std::string, std::string)'"
// ... followed by pages of template substitution failures
```

**Correct (concepts - clear constraints):**

```cpp
// Define reusable concept
template<typename T>
concept Numeric = std::is_arithmetic_v<T> && !std::is_same_v<T, bool>;

// Clean constraint syntax
template<Numeric T>
T add(T a, T b) {
    return a + b;
}

// Error message when called with string:
// "constraints not satisfied for template 'add'"
// "because 'std::string' does not satisfy 'Numeric'"
```

**Standard library concepts:**

```cpp
#include <concepts>

// Type concepts
template<std::integral T>      // int, long, etc.
void processInt(T value);

template<std::floating_point T>  // float, double
void processFloat(T value);

// Iterator concepts
template<std::random_access_iterator Iter>
void shuffle(Iter begin, Iter end);

// Range concepts
template<std::ranges::range R>
void process(R&& range);

// Callable concepts
template<std::invocable<int> F>
void forEach(F&& func);
```

**Custom concepts:**

```cpp
// Concept for types with a serialize method
template<typename T>
concept Serializable = requires(T t, std::ostream& os) {
    { t.serialize(os) } -> std::same_as<void>;
};

// Concept for container-like types
template<typename T>
concept Container = requires(T t) {
    { t.begin() } -> std::input_iterator;
    { t.end() } -> std::input_iterator;
    { t.size() } -> std::convertible_to<std::size_t>;
};

// Usage
template<Container C>
void printAll(const C& container) {
    for (const auto& item : container) {
        std::cout << item << '\n';
    }
}
```

**Abbreviated function templates:**

```cpp
// Even cleaner with auto and concepts
void process(std::integral auto value) {
    // value is constrained to integral types
}

auto add(Numeric auto a, Numeric auto b) {
    return a + b;
}
```

**Combining concepts:**

```cpp
template<typename T>
concept Printable = requires(T t) {
    { std::cout << t };
};

template<typename T>
concept PrintableNumeric = Numeric<T> && Printable<T>;
```

Reference: [C++20 Concepts](https://en.cppreference.com/w/cpp/language/constraints)
