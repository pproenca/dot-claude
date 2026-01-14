---
title: Use Branchless Programming for Hot Paths
impact: LOW-MEDIUM
impactDescription: eliminates branch misprediction penalty (10-20 cycles per miss)
tags: codegen, branchless, optimization, branch-prediction, hot-path
---

## Use Branchless Programming for Hot Paths

Branch mispredictions are expensive (10-20 CPU cycles). For unpredictable branches in hot paths, branchless alternatives can significantly improve performance.

**Incorrect (unpredictable branches):**

```cpp
// Random data causes 50% misprediction rate
int clamp(int value, int min, int max) {
    if (value < min) return min;
    if (value > max) return max;
    return value;
}

// Branch on unpredictable condition
int selectValue(bool condition, int a, int b) {
    if (condition) return a;
    return b;
}
```

**Correct (branchless alternatives):**

```cpp
// Branchless clamp using min/max
int clamp(int value, int min, int max) {
    return std::min(std::max(value, min), max);
    // Compiles to: cmov instructions, no branches
}

// Branchless select using arithmetic
int selectValue(bool condition, int a, int b) {
    return condition * a + (!condition) * b;
    // Or use ternary which often compiles to cmov
    return condition ? a : b;
}

// Branchless absolute value
int abs_branchless(int x) {
    int mask = x >> 31;  // All 1s if negative, all 0s if positive
    return (x ^ mask) - mask;
}
```

**Branchless table lookup:**

```cpp
// Incorrect: switch with many cases
int categorize(int value) {
    switch (value) {
        case 0: return 10;
        case 1: return 20;
        case 2: return 15;
        // ... many cases
    }
}

// Correct: lookup table
constexpr int categoryTable[] = {10, 20, 15, /* ... */};
int categorize(int value) {
    return categoryTable[value];  // Single memory access
}
```

**Branchless sign function:**

```cpp
// Incorrect: branches
int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;
}

// Correct: branchless
int sign(int x) {
    return (x > 0) - (x < 0);
}
```

**When to use branchless:**
- Inner loops with unpredictable conditions
- Data-dependent branches with ~50% taken rate
- Performance-critical hot paths

**When NOT to use branchless:**
- Predictable branches (almost always/never taken)
- Cold code paths
- When it significantly hurts readability

Reference: [Branchless Programming](https://en.algorithmica.org/hpc/pipelining/branchless/)
