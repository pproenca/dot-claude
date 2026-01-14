---
title: Structure Code for Auto-Vectorization
impact: LOW-MEDIUM
impactDescription: 2-8x speedup for numeric loops when vectorized
tags: codegen, simd, vectorization, avx, sse, optimization
---

## Structure Code for Auto-Vectorization

Modern compilers can automatically vectorize loops using SIMD instructions (SSE, AVX). Structuring code correctly enables this optimization for significant performance gains.

**Incorrect (prevents auto-vectorization):**

```cpp
void addArrays(float* a, const float* b, const float* c, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        a[i] = b[i] + c[i];  // May not vectorize due to aliasing
    }
}

// Function call in loop prevents vectorization
float transform(float x);
void process(float* data, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        data[i] = transform(data[i]);  // Cannot vectorize
    }
}
```

**Correct (enables auto-vectorization):**

```cpp
// Use __restrict to promise no aliasing
void addArrays(float* __restrict a,
               const float* __restrict b,
               const float* __restrict c, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        a[i] = b[i] + c[i];  // Will vectorize
    }
}

// Inline the transform function
inline float transform(float x) { return x * x + 1.0f; }
void process(float* data, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        data[i] = transform(data[i]);  // Can vectorize
    }
}

// Or use OpenMP SIMD directive
void process(float* data, size_t n) {
    #pragma omp simd
    for (size_t i = 0; i < n; ++i) {
        data[i] = data[i] * data[i] + 1.0f;
    }
}
```

**Data layout for vectorization:**

```cpp
// Incorrect: Array of Structs (AoS) - poor vectorization
struct Particle { float x, y, z, w; };
std::vector<Particle> particles;

// Correct: Structure of Arrays (SoA) - excellent vectorization
struct Particles {
    std::vector<float> x, y, z, w;

    void update(float dt) {
        size_t n = x.size();
        for (size_t i = 0; i < n; ++i) {
            x[i] += vx[i] * dt;  // All x values contiguous
            y[i] += vy[i] * dt;  // Vectorizes efficiently
        }
    }
};
```

**Checking vectorization:**

```bash
# GCC/Clang: vectorization report
g++ -O3 -fopt-info-vec-missed code.cpp
clang++ -O3 -Rpass=loop-vectorize -Rpass-missed=loop-vectorize code.cpp
```

Reference: [Intel Vectorization Guide](https://www.intel.com/content/www/us/en/docs/intrinsics-guide/)
