---
title: Use noexcept to Enable Compiler Optimizations
impact: LOW-MEDIUM
impactDescription: enables move optimizations in STL, reduces exception handling overhead
tags: codegen, noexcept, exceptions, move-semantics, optimization
---

## Use noexcept to Enable Compiler Optimizations

The `noexcept` specifier enables important compiler optimizations, especially for move operations. STL containers use `noexcept` to decide between moving and copying elements.

**Incorrect (missing noexcept on move operations):**

```cpp
class Buffer {
    char* data_;
    size_t size_;
public:
    // Move constructor without noexcept
    Buffer(Buffer&& other)
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }
    // std::vector will COPY instead of MOVE during reallocation!
};
```

**Correct (noexcept move operations):**

```cpp
class Buffer {
    char* data_;
    size_t size_;
public:
    Buffer(Buffer&& other) noexcept
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    Buffer& operator=(Buffer&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }
    // std::vector will now MOVE during reallocation
};
```

**Using conditional noexcept:**

```cpp
template<typename T>
class Container {
    T* data_;
public:
    // Conditionally noexcept based on T's move
    Container(Container&& other)
        noexcept(std::is_nothrow_move_constructible_v<T>)
        : data_(std::exchange(other.data_, nullptr)) {}
};
```

**Functions that should be noexcept:**
- Move constructors and move assignment operators
- Swap functions
- Destructors (implicitly noexcept)
- Simple accessors and getters

Reference: [C++ Core Guidelines C.66](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#c66-make-move-operations-noexcept)
