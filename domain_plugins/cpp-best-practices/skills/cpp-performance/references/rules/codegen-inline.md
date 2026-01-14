---
title: Use Inline Hints Appropriately
impact: LOW-MEDIUM
impactDescription: enables function inlining for hot paths
tags: codegen, inline, optimization, hot-path, performance
---

## Use Inline Hints Appropriately

Inlining eliminates function call overhead and enables further optimizations. Use `inline` for small functions in headers and compiler-specific hints for critical hot paths.

**Incorrect (forced inlining everywhere):**

```cpp
// Over-inlining bloats code and can hurt performance
class Widget {
public:
    __forceinline void complexOperation() {  // Too large to inline
        // 100 lines of code...
    }

    __forceinline void rarelyUsed() {  // Not worth inlining
        // Code that runs once per session
    }
};
```

**Correct (strategic inlining):**

```cpp
class Widget {
public:
    // Small accessors - good inline candidates
    inline int getId() const { return id_; }
    inline bool isActive() const { return active_; }

    // Hot path - hint for aggressive inlining
    [[gnu::always_inline]] inline void hotPathOp() {
        // Small, frequently called
    }

    // Cold path - prevent inlining
    [[gnu::noinline]] void errorHandler() {
        // Rarely called, keep out of hot code
    }

    // Let compiler decide for medium functions
    void normalOperation() {
        // Compiler will inline if beneficial
    }
};
```

**Compiler-specific attributes:**

```cpp
// GCC/Clang
[[gnu::always_inline]] inline void mustInline() {}
[[gnu::noinline]] void neverInline() {}
[[gnu::hot]] void hotFunction() {}
[[gnu::cold]] void coldFunction() {}

// MSVC
__forceinline void mustInline() {}
__declspec(noinline) void neverInline() {}

// Portable macro
#if defined(__GNUC__)
    #define FORCE_INLINE [[gnu::always_inline]] inline
    #define NO_INLINE [[gnu::noinline]]
#elif defined(_MSC_VER)
    #define FORCE_INLINE __forceinline
    #define NO_INLINE __declspec(noinline)
#else
    #define FORCE_INLINE inline
    #define NO_INLINE
#endif
```

**Link-Time Optimization (LTO) for cross-module inlining:**

```cmake
# CMakeLists.txt - enable LTO
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)

# Or per-target
set_property(TARGET myapp PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
```

**Guidelines:**
- Inline small accessors and trivial functions
- Don't inline functions with loops or branches (unless very hot)
- Don't inline error handling or cold paths
- Trust the compiler for medium-sized functions
- Use LTO to let compiler inline across translation units

Reference: [GCC Function Attributes](https://gcc.gnu.org/onlinedocs/gcc/Common-Function-Attributes.html)
