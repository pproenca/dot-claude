---
title: Use Lookup Tables for Repeated Computations
impact: MEDIUM
impactDescription: trades memory for speed, O(1) vs O(n) for known domains
tags: algo, lookup-table, memoization, precomputation, optimization
---

## Use Lookup Tables for Repeated Computations

Precomputing results into lookup tables converts repeated expensive computations into simple array lookups. Effective for functions with small, known input domains.

**Incorrect (repeated computation):**

```cpp
// Called millions of times in hot loop
int popcount_slow(uint8_t byte) {
    int count = 0;
    while (byte) {
        count += byte & 1;
        byte >>= 1;
    }
    return count;
}

// Trigonometry in tight loop
float fastSin(float angle) {
    return std::sin(angle);  // Expensive computation each call
}
```

**Correct (lookup table):**

```cpp
// Precomputed popcount table
constexpr std::array<uint8_t, 256> makePopcountTable() {
    std::array<uint8_t, 256> table{};
    for (int i = 0; i < 256; ++i) {
        table[i] = (i & 1) + table[i / 2];
    }
    return table;
}

constexpr auto POPCOUNT_TABLE = makePopcountTable();

int popcount_fast(uint8_t byte) {
    return POPCOUNT_TABLE[byte];  // Single array lookup
}

// Lookup table for 32-bit
int popcount32(uint32_t value) {
    return POPCOUNT_TABLE[value & 0xFF]
         + POPCOUNT_TABLE[(value >> 8) & 0xFF]
         + POPCOUNT_TABLE[(value >> 16) & 0xFF]
         + POPCOUNT_TABLE[(value >> 24) & 0xFF];
}
```

**Trigonometric lookup table:**

```cpp
class SinTable {
    static constexpr size_t SIZE = 1024;
    std::array<float, SIZE> table_;

public:
    SinTable() {
        for (size_t i = 0; i < SIZE; ++i) {
            table_[i] = std::sin(2.0f * M_PI * i / SIZE);
        }
    }

    float lookup(float angle) const {
        // Normalize to [0, 2π) and scale to table index
        float normalized = std::fmod(angle, 2.0f * M_PI);
        if (normalized < 0) normalized += 2.0f * M_PI;
        size_t index = static_cast<size_t>(normalized * SIZE / (2.0f * M_PI));
        return table_[index % SIZE];
    }

    // Interpolated lookup for better accuracy
    float lookupInterp(float angle) const {
        float normalized = std::fmod(angle, 2.0f * M_PI);
        if (normalized < 0) normalized += 2.0f * M_PI;
        float scaled = normalized * SIZE / (2.0f * M_PI);
        size_t i0 = static_cast<size_t>(scaled) % SIZE;
        size_t i1 = (i0 + 1) % SIZE;
        float frac = scaled - std::floor(scaled);
        return table_[i0] * (1 - frac) + table_[i1] * frac;
    }
};
```

**Perfect hash for string lookup:**

```cpp
// Compile-time string hash
constexpr uint32_t hash(const char* str) {
    uint32_t h = 0;
    while (*str) h = h * 31 + *str++;
    return h;
}

int handleCommand(std::string_view cmd) {
    switch (hash(cmd.data())) {
        case hash("start"): return 1;
        case hash("stop"):  return 2;
        case hash("pause"): return 3;
        default: return 0;
    }
}
```

Reference: [Lookup Table Optimization](https://en.algorithmica.org/hpc/data-structures/lookup/)
