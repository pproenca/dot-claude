---
title: Use restrict for Non-Aliasing Pointers
impact: LOW-MEDIUM
impactDescription: enables vectorization and optimizations
tags: codegen, restrict, aliasing, vectorization, optimization
---

## Use restrict for Non-Aliasing Pointers

When pointers don't alias (point to overlapping memory), use `__restrict` to inform the compiler, enabling aggressive optimizations like vectorization.

**Incorrect (aliasing assumed):**

```cpp
// Compiler must assume a and b might overlap
void addArrays(float* a, float* b, float* result, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        result[i] = a[i] + b[i];
    }
}
// Compiler can't vectorize - result might alias a or b
```

**Correct (no aliasing guaranteed):**

```cpp
// Compiler knows pointers don't overlap
void addArrays(float* __restrict a,
               float* __restrict b,
               float* __restrict result,
               size_t n) {
    for (size_t i = 0; i < n; ++i) {
        result[i] = a[i] + b[i];
    }
}
// Compiler can vectorize with SIMD instructions
```

**Portable restrict macro:**

```cpp
#if defined(__GNUC__) || defined(__clang__)
    #define RESTRICT __restrict__
#elif defined(_MSC_VER)
    #define RESTRICT __restrict
#else
    #define RESTRICT
#endif

void process(float* RESTRICT input, float* RESTRICT output, size_t n);
```

**Matrix operations benefit greatly:**

```cpp
void matmul(const float* RESTRICT A,
            const float* RESTRICT B,
            float* RESTRICT C,
            int N) {
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            float sum = 0;
            for (int k = 0; k < N; ++k) {
                sum += A[i*N + k] * B[k*N + j];
            }
            C[i*N + j] = sum;
        }
    }
}
// Without restrict: ~3x slower due to aliasing checks
```

**OpenMP SIMD for explicit vectorization:**

```cpp
void addArraysSIMD(float* __restrict a,
                   float* __restrict b,
                   float* __restrict result,
                   size_t n) {
    #pragma omp simd
    for (size_t i = 0; i < n; ++i) {
        result[i] = a[i] + b[i];
    }
}
```

**When restrict is safe:**
- Separate arrays passed as arguments
- Non-overlapping views into same array
- Output array distinct from all inputs

**When restrict is UNSAFE:**
- In-place operations (input == output)
- Overlapping array slices
- Unknown caller behavior

**Verify vectorization:**

```bash
# GCC - check vectorization report
g++ -O3 -fopt-info-vec -c code.cpp

# Clang - check LLVM remarks
clang++ -O3 -Rpass=loop-vectorize -c code.cpp
```

Reference: [GCC Restricted Pointers](https://gcc.gnu.org/onlinedocs/gcc/Restricted-Pointers.html)
