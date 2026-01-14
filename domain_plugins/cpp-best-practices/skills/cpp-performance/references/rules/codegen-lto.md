---
title: Enable Link-Time Optimization for Release Builds
impact: LOW-MEDIUM
impactDescription: 5-20% performance improvement, better inlining across translation units
tags: codegen, lto, linker, optimization, release
---

## Enable Link-Time Optimization for Release Builds

Link-time optimization (LTO) allows the compiler to optimize across translation unit boundaries, enabling cross-module inlining, dead code elimination, and better devirtualization.

**Incorrect (separate compilation without LTO):**

```cpp
// math.cpp
double compute(double x) {
    return std::sin(x) * std::cos(x);
}

// main.cpp
extern double compute(double x);
int main() {
    double result = compute(3.14);  // Cannot inline across TUs
}
```

**Correct (enable LTO in build system):**

```cmake
# CMake
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)

# Or manually
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -flto")
set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} -flto")
```

**Compiler flags:**

```bash
# GCC/Clang
g++ -flto -O2 main.cpp math.cpp -o program

# MSVC
cl /GL main.cpp math.cpp /link /LTCG

# Thin LTO (faster build times, Clang)
clang++ -flto=thin -O2 main.cpp math.cpp -o program
```

**When to use:**
- Release builds only (increases link time significantly)
- Performance-critical applications
- When functions in different TUs call each other frequently

Reference: [GCC LTO Documentation](https://gcc.gnu.org/wiki/LinkTimeOptimization)
