---
title: Avoid False Sharing with Cache-Line Alignment
impact: HIGH
impactDescription: eliminates cache thrashing, 2-10x speedup
tags: async, false-sharing, cache-line, alignment, performance
---

## Avoid False Sharing with Cache-Line Alignment

False sharing occurs when threads access different variables that share a cache line, causing unnecessary cache invalidations. Align frequently-modified variables to cache line boundaries.

**Incorrect (false sharing between counters):**

```cpp
struct Counters {
    int counter1;  // Thread 1 modifies
    int counter2;  // Thread 2 modifies
    int counter3;  // Thread 3 modifies
    int counter4;  // Thread 4 modifies
};
// All counters fit in one 64-byte cache line
// When thread 1 writes counter1, threads 2-4 must reload

void increment(Counters& c, int threadId) {
    for (int i = 0; i < 1000000; ++i) {
        // Massive cache thrashing!
        if (threadId == 0) ++c.counter1;
        else if (threadId == 1) ++c.counter2;
        // ...
    }
}
```

**Correct (cache-line aligned):**

```cpp
struct alignas(64) AlignedCounter {
    std::atomic<int> value{0};
    // Padding fills rest of cache line
};

struct Counters {
    AlignedCounter counter1;  // Own cache line
    AlignedCounter counter2;  // Own cache line
    AlignedCounter counter3;  // Own cache line
    AlignedCounter counter4;  // Own cache line
};

// C++17 hardware_destructive_interference_size
struct alignas(std::hardware_destructive_interference_size) Counter {
    std::atomic<int> value{0};
};
```

**Detecting false sharing:**

```cpp
// Check alignment at compile time
static_assert(
    sizeof(AlignedCounter) >= std::hardware_destructive_interference_size,
    "Counter may cause false sharing"
);

// Runtime check
void checkAlignment(void* ptr) {
    auto addr = reinterpret_cast<std::uintptr_t>(ptr);
    if (addr % 64 != 0) {
        std::cerr << "Warning: potential false sharing\n";
    }
}
```

**Thread-local storage alternative:**

```cpp
// Each thread has its own counter - no sharing at all
thread_local int localCounter = 0;

void worker() {
    for (int i = 0; i < 1000000; ++i) {
        ++localCounter;  // No cache line contention
    }
}

int totalCount() {
    // Aggregate when needed
    return aggregateFromAllThreads();
}
```

**Array of thread data:**

```cpp
struct alignas(64) ThreadData {
    int counter;
    int localSum;
    // Other per-thread data
    char padding[64 - 2 * sizeof(int)];
};

std::array<ThreadData, 16> threadData;
// Each thread accesses only its own ThreadData
```

Reference: [C++17 hardware interference size](https://en.cppreference.com/w/cpp/thread/hardware_destructive_interference_size)
