---
title: Use C++20 Modules for Large Projects
impact: HIGH
impactDescription: 2-5x faster builds, better encapsulation
tags: compile, modules, c++20, imports, build-time
---

## Use C++20 Modules for Large Projects

C++20 modules replace the preprocessor-based include model with a modern import system. Modules are parsed once and cached, eliminating redundant parsing and macro pollution.

**Incorrect (header-based):**

```cpp
// math_utils.h
#pragma once
#include <cmath>
#include <vector>

inline double average(const std::vector<double>& v) {
    double sum = 0;
    for (auto x : v) sum += x;
    return sum / v.size();
}

// Every includer re-parses this and all its includes
```

**Correct (module-based):**

```cpp
// math_utils.ixx (module interface)
export module math_utils;

import <cmath>;
import <vector>;

export double average(const std::vector<double>& v) {
    double sum = 0;
    for (auto x : v) sum += x;
    return sum / v.size();
}

// main.cpp
import math_utils;  // Binary interface, no re-parsing

int main() {
    std::vector<double> data = {1.0, 2.0, 3.0};
    auto avg = average(data);
}
```

**Module partitions for large modules:**

```cpp
// graphics.ixx - main module interface
export module graphics;

export import :shapes;    // Re-export shapes partition
export import :rendering; // Re-export rendering partition

// graphics-shapes.ixx - partition
export module graphics:shapes;

export class Circle { /* ... */ };
export class Rectangle { /* ... */ };

// graphics-rendering.ixx - partition
export module graphics:rendering;

export void render(const Circle& c);
```

**Internal implementation partition:**

```cpp
// graphics-impl.ixx - internal partition (not exported)
module graphics:impl;

// Internal helpers, not visible to importers
void internalHelper() { /* ... */ }
```

**CMake configuration:**

```cmake
# CMakeLists.txt (CMake 3.28+)
add_library(math_utils)
target_sources(math_utils
    PUBLIC FILE_SET CXX_MODULES FILES
        math_utils.ixx
)
```

**Benefits:**
- Headers parsed once, cached as binary
- No macro leakage between modules
- Explicit export controls visibility
- Better dependency tracking

Reference: [C++20 Modules](https://en.cppreference.com/w/cpp/language/modules)
