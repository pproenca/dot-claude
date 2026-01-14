---
title: Use extern template for Common Instantiations
impact: CRITICAL
impactDescription: eliminates redundant template instantiation
tags: compile, extern-template, templates, instantiation, link-time
---

## Use extern template for Common Instantiations

When templates are instantiated with the same types across many translation units, use `extern template` to instantiate once and share. This eliminates redundant code generation.

**Incorrect (redundant instantiation):**

```cpp
// vector_utils.h
template<typename T>
T sum(const std::vector<T>& v) {
    return std::accumulate(v.begin(), v.end(), T{});
}

// file1.cpp
#include "vector_utils.h"
void f1() { sum(std::vector<int>{}); }  // Instantiates sum<int>

// file2.cpp
#include "vector_utils.h"
void f2() { sum(std::vector<int>{}); }  // Instantiates sum<int> AGAIN

// file3.cpp - and so on for every file...
```

Each translation unit generates identical code, wasting compile time and bloating object files.

**Correct (explicit instantiation):**

```cpp
// vector_utils.h
template<typename T>
T sum(const std::vector<T>& v) {
    return std::accumulate(v.begin(), v.end(), T{});
}

// Suppress implicit instantiation for common types
extern template int sum(const std::vector<int>&);
extern template double sum(const std::vector<double>&);

// vector_utils.cpp - explicit instantiation
#include "vector_utils.h"

// Generate code once here
template int sum(const std::vector<int>&);
template double sum(const std::vector<double>&);
```

**Common candidates for extern template:**

```cpp
// Standard library containers with common types
extern template class std::vector<int>;
extern template class std::vector<std::string>;
extern template class std::basic_string<char>;

// Your frequently-used templates
extern template class Matrix<float>;
extern template class Matrix<double>;
extern template class Parser<JsonNode>;
```

**Measure impact:**

```bash
# Before extern template
time g++ -c file1.cpp  # 2.3s per file

# After extern template
time g++ -c file1.cpp  # 0.8s per file
```

Reference: [C++11 extern template](https://en.cppreference.com/w/cpp/language/class_template#Explicit_instantiation)
