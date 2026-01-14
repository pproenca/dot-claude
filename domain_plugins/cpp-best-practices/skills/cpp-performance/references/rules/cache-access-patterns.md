---
title: Optimize Memory Access Patterns
impact: MEDIUM-HIGH
impactDescription: 2-10x speedup for matrix/array operations
tags: cache, access-pattern, row-major, column-major, matrix
---

## Optimize Memory Access Patterns

Access memory sequentially when possible. For multi-dimensional arrays, iterate in row-major order (last index varies fastest in C++) to maximize cache line utilization.

**Incorrect (column-major access in C++):**

```cpp
const int N = 1000;
int matrix[N][N];

// Column-major iteration - cache unfriendly
int sum = 0;
for (int j = 0; j < N; ++j) {        // Outer: columns
    for (int i = 0; i < N; ++i) {    // Inner: rows
        sum += matrix[i][j];  // Jumps N*sizeof(int) bytes each iteration
    }
}
// Each access likely causes cache miss
```

**Correct (row-major access):**

```cpp
const int N = 1000;
int matrix[N][N];

// Row-major iteration - cache friendly
int sum = 0;
for (int i = 0; i < N; ++i) {        // Outer: rows
    for (int j = 0; j < N; ++j) {    // Inner: columns
        sum += matrix[i][j];  // Sequential memory access
    }
}
// Each cache line serves multiple iterations
```

**Matrix multiplication optimization:**

```cpp
// Incorrect - poor access pattern for B
void matmulNaive(const float* A, const float* B, float* C, int N) {
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            float sum = 0;
            for (int k = 0; k < N; ++k) {
                sum += A[i*N + k] * B[k*N + j];  // B accessed column-wise
            }
            C[i*N + j] = sum;
        }
    }
}

// Correct - blocked/tiled for cache
void matmulTiled(const float* A, const float* B, float* C, int N) {
    const int BLOCK = 32;  // Tile size for L1 cache
    for (int i0 = 0; i0 < N; i0 += BLOCK) {
        for (int j0 = 0; j0 < N; j0 += BLOCK) {
            for (int k0 = 0; k0 < N; k0 += BLOCK) {
                // Process tile
                for (int i = i0; i < std::min(i0+BLOCK, N); ++i) {
                    for (int j = j0; j < std::min(j0+BLOCK, N); ++j) {
                        float sum = C[i*N + j];
                        for (int k = k0; k < std::min(k0+BLOCK, N); ++k) {
                            sum += A[i*N + k] * B[k*N + j];
                        }
                        C[i*N + j] = sum;
                    }
                }
            }
        }
    }
}
```

**Loop interchange for better access:**

```cpp
// Before: poor access pattern
for (int k = 0; k < K; ++k) {
    for (int i = 0; i < N; ++i) {
        data[i] += weights[k] * input[k*N + i];
    }
}

// After: better access pattern
for (int i = 0; i < N; ++i) {
    for (int k = 0; k < K; ++k) {
        data[i] += weights[k] * input[k*N + i];
    }
}
```

**Measure with perf:**

```bash
perf stat -e cache-misses,cache-references ./program
```

Reference: [Cache-Oblivious Algorithms](https://en.wikipedia.org/wiki/Cache-oblivious_algorithm)
