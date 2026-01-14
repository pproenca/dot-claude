---
title: Use Profile-Guided Optimization for Production Builds
impact: LOW-MEDIUM
impactDescription: 10-30% performance improvement with real usage patterns
tags: codegen, pgo, profile, optimization, release
---

## Use Profile-Guided Optimization for Production Builds

Profile-guided optimization (PGO) uses runtime profiling data to optimize code layout, branch prediction, and inlining decisions based on actual usage patterns.

**Basic PGO workflow:**

```bash
# Step 1: Build with instrumentation
g++ -fprofile-generate -O2 program.cpp -o program_instrumented

# Step 2: Run with representative workload
./program_instrumented < typical_input.txt

# Step 3: Rebuild with profile data
g++ -fprofile-use -O2 program.cpp -o program_optimized
```

**CMake integration:**

```cmake
# CMakeLists.txt
option(ENABLE_PGO_GENERATE "Build with PGO instrumentation" OFF)
option(ENABLE_PGO_USE "Build with PGO optimization" OFF)

if(ENABLE_PGO_GENERATE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fprofile-generate=${CMAKE_BINARY_DIR}/pgo")
endif()

if(ENABLE_PGO_USE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fprofile-use=${CMAKE_BINARY_DIR}/pgo")
endif()
```

**What PGO optimizes:**

```cpp
// Branch prediction - hot paths identified
void process(const Data& data) {
    if (data.isValid()) {  // PGO learns this is usually true
        normalPath();       // Optimized for likely case
    } else {
        errorPath();        // Moved to cold section
    }
}

// Function inlining - inline frequently called functions
int compute(int x) {
    return helper(x);  // PGO may inline if called often
}

// Code layout - hot functions placed together
void hotFunction();   // Placed in hot section
void coldFunction();  // Placed in cold section
```

**LLVM Bolt for post-link optimization:**

```bash
# Even more aggressive optimization using LLVM Bolt
llvm-bolt program -o program.bolt \
    -data=perf.fdata \
    -reorder-blocks=cache+ \
    -reorder-functions=hfsort
```

**Best practices:**
- Use representative workloads for profiling
- Profile multiple scenarios if usage varies
- Reprofile when code changes significantly
- Combine with LTO for maximum benefit

Reference: [GCC Profile Feedback](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html#index-fprofile-generate)
