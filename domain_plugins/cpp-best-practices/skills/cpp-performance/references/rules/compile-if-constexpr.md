---
title: Use if constexpr Instead of SFINAE
impact: HIGH
impactDescription: clearer code, faster compilation
tags: compile, if-constexpr, sfinae, templates, c++17
---

## Use if constexpr Instead of SFINAE

`if constexpr` (C++17) provides compile-time branching that's clearer and compiles faster than SFINAE-based alternatives. The compiler completely eliminates the untaken branch.

**Incorrect (SFINAE - complex and slow to compile):**

```cpp
// Complex SFINAE pattern
template<typename T>
typename std::enable_if<std::is_integral<T>::value, T>::type
process(T value) {
    return value * 2;
}

template<typename T>
typename std::enable_if<std::is_floating_point<T>::value, T>::type
process(T value) {
    return value * 2.5;
}

template<typename T>
typename std::enable_if<
    !std::is_integral<T>::value && !std::is_floating_point<T>::value,
    T
>::type
process(T value) {
    return value;
}
```

**Correct (if constexpr - clear and fast):**

```cpp
template<typename T>
T process(T value) {
    if constexpr (std::is_integral_v<T>) {
        return value * 2;
    } else if constexpr (std::is_floating_point_v<T>) {
        return value * 2.5;
    } else {
        return value;
    }
}
```

**The untaken branches can contain invalid code:**

```cpp
template<typename T>
auto getValue(T& container) {
    if constexpr (requires { container.size(); }) {
        return container.size();  // Only compiled if T has size()
    } else if constexpr (requires { container.length(); }) {
        return container.length();  // Only compiled if T has length()
    } else {
        return 0;
    }
}
```

**Recursive template example:**

```cpp
template<typename T, typename... Args>
void print(T first, Args... rest) {
    std::cout << first;
    if constexpr (sizeof...(rest) > 0) {
        std::cout << ", ";
        print(rest...);  // Only instantiated if more args
    }
}
```

**Type-based dispatch:**

```cpp
template<typename Container>
void processContainer(Container& c) {
    if constexpr (std::is_same_v<Container, std::vector<int>>) {
        // Vector-specific optimization
        c.reserve(1000);
    }
    for (auto& item : c) {
        process(item);
    }
}
```

Reference: [C++17 if constexpr](https://en.cppreference.com/w/cpp/language/if#Constexpr_if)
