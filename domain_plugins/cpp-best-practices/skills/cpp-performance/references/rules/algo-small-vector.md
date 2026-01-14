---
title: Use Small Buffer Optimization for Small Collections
impact: MEDIUM
impactDescription: eliminates heap allocation for small sizes, 10-100x faster construction
tags: algo, small-vector, sbo, allocation, stack-allocation
---

## Use Small Buffer Optimization for Small Collections

Small Buffer Optimization (SBO) stores small collections inline, avoiding heap allocation. Use specialized containers or implement SBO for frequently created small collections.

**Incorrect (heap allocation for small vectors):**

```cpp
void processItems() {
    std::vector<int> items;  // Always heap allocates
    items.push_back(1);
    items.push_back(2);
    items.push_back(3);
    // Heap allocation for just 3 integers!
}

// Called frequently in hot path
std::vector<Point> getNeighbors(Point p) {
    std::vector<Point> result;
    // Usually returns 4-8 neighbors, but heap allocates
    return result;
}
```

**Correct (using small vector with inline storage):**

```cpp
// Boost.Container small_vector
#include <boost/container/small_vector.hpp>

void processItems() {
    boost::container::small_vector<int, 8> items;  // 8 ints inline
    items.push_back(1);
    items.push_back(2);
    items.push_back(3);
    // No heap allocation!
}

// LLVM SmallVector
#include "llvm/ADT/SmallVector.h"
llvm::SmallVector<Point, 8> getNeighbors(Point p) {
    llvm::SmallVector<Point, 8> result;  // Inline up to 8
    // Add neighbors...
    return result;
}
```

**Simple small_vector implementation:**

```cpp
template<typename T, size_t N>
class SmallVector {
    alignas(T) char buffer_[sizeof(T) * N];
    T* data_ = reinterpret_cast<T*>(buffer_);
    size_t size_ = 0;
    size_t capacity_ = N;
    bool onHeap_ = false;

public:
    void push_back(const T& value) {
        if (size_ == capacity_) {
            grow();
        }
        new (data_ + size_) T(value);
        ++size_;
    }

private:
    void grow() {
        size_t newCap = capacity_ * 2;
        T* newData = static_cast<T*>(::operator new(sizeof(T) * newCap));
        for (size_t i = 0; i < size_; ++i) {
            new (newData + i) T(std::move(data_[i]));
            data_[i].~T();
        }
        if (onHeap_) ::operator delete(data_);
        data_ = newData;
        capacity_ = newCap;
        onHeap_ = true;
    }
};
```

**Choosing inline size:**
- Profile your actual usage patterns
- 8-16 elements is common for general use
- Consider `sizeof(T) * N` - keep under cache line (64 bytes)
- Too large wastes stack space when empty

Reference: [LLVM SmallVector](https://llvm.org/doxygen/classllvm_1_1SmallVector.html)
