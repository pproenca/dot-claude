---
title: Use Move Semantics to Avoid Copies
impact: CRITICAL
impactDescription: eliminates expensive deep copies
tags: memory, move-semantics, rvalue, std-move, performance
---

## Use Move Semantics to Avoid Copies

Move semantics transfer ownership of resources instead of copying them. Use `std::move` to convert lvalues to rvalues when you no longer need the original value.

**Incorrect (unnecessary copies):**

```cpp
std::vector<std::string> buildStrings() {
    std::vector<std::string> result;
    std::string temp = computeString();
    result.push_back(temp);  // Copies temp
    return result;
}

void processData(std::vector<int> data) {  // Copies entire vector
    // ...
}

class Widget {
    std::string name_;
public:
    void setName(std::string name) {
        name_ = name;  // Copies name
    }
};
```

**Correct (move semantics):**

```cpp
std::vector<std::string> buildStrings() {
    std::vector<std::string> result;
    std::string temp = computeString();
    result.push_back(std::move(temp));  // Moves temp, no copy
    return result;  // NRVO or implicit move
}

void processData(std::vector<int>&& data) {  // Takes ownership
    // ...
}

class Widget {
    std::string name_;
public:
    void setName(std::string name) {
        name_ = std::move(name);  // Move from parameter
    }
};
```

**Sink pattern for optimal performance:**

```cpp
class Container {
    std::vector<Item> items_;
public:
    // Sink: caller decides copy vs move
    void addItem(Item item) {
        items_.push_back(std::move(item));
    }
};

// Usage:
container.addItem(existingItem);           // Copies
container.addItem(std::move(existingItem)); // Moves
container.addItem(Item{});                  // Moves temporary
```

**Warning:** Don't use moved-from objects except to reassign or destroy them.

Reference: [C++ Core Guidelines F.18](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#f18-for-will-move-from-parameters-pass-by-x-and-stdmove-the-parameter)
