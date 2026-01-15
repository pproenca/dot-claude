---
title: Use Arena Allocators for Temporary Data
impact: HIGH
impactDescription: 5-20× improvement for complex operations with many small allocations
tags: mem, arena, allocator, temporary
---

## Use Arena Allocators for Temporary Data

When processing data requires many temporary allocations, use an arena allocator that bulk-frees all memory at once instead of individual allocations/deallocations.

**Incorrect (individual allocations):**

```cpp
Napi::Value ParseComplexData(const Napi::CallbackInfo& info) {
  std::vector<Node*> nodes;

  for (size_t i = 0; i < count; i++) {
    // Individual heap allocation per node
    Node* node = new Node();
    node->children = new std::vector<Node*>();  // More allocations
    node->data = new DataBlock();  // Even more allocations
    nodes.push_back(node);
  }

  // Process nodes...

  // Cleanup - must free each allocation
  for (auto* node : nodes) {
    delete node->data;
    delete node->children;
    delete node;
  }
}
```

**Correct (arena allocation):**

```cpp
#include <memory>
#include <vector>

class Arena {
 public:
  explicit Arena(size_t block_size = 64 * 1024)
      : block_size_(block_size), current_offset_(0) {
    blocks_.push_back(std::make_unique<uint8_t[]>(block_size_));
  }

  template<typename T, typename... Args>
  T* Allocate(Args&&... args) {
    size_t size = sizeof(T);
    size_t alignment = alignof(T);

    // Align offset
    current_offset_ = (current_offset_ + alignment - 1) & ~(alignment - 1);

    // Check if current block has space
    if (current_offset_ + size > block_size_) {
      blocks_.push_back(std::make_unique<uint8_t[]>(block_size_));
      current_offset_ = 0;
    }

    void* ptr = blocks_.back().get() + current_offset_;
    current_offset_ += size;

    return new (ptr) T(std::forward<Args>(args)...);
  }

  void Reset() {
    // Keep first block, release others
    blocks_.resize(1);
    current_offset_ = 0;
  }

  // All memory freed when Arena is destroyed
  ~Arena() = default;

 private:
  size_t block_size_;
  size_t current_offset_;
  std::vector<std::unique_ptr<uint8_t[]>> blocks_;
};

Napi::Value ParseComplexData(const Napi::CallbackInfo& info) {
  Arena arena(64 * 1024);  // 64KB blocks

  std::vector<Node*> nodes;
  for (size_t i = 0; i < count; i++) {
    // All allocations from arena - super fast
    Node* node = arena.Allocate<Node>();
    node->children = arena.Allocate<std::vector<Node*>>();
    node->data = arena.Allocate<DataBlock>();
    nodes.push_back(node);
  }

  // Process nodes...

  // No cleanup needed - arena destructor frees all
  return result;
}
```

**Thread-local arena for repeated operations:**

```cpp
// Reuse arena across calls on same thread
thread_local Arena* tl_arena = nullptr;

Napi::Value ProcessWithArena(const Napi::CallbackInfo& info) {
  if (!tl_arena) {
    tl_arena = new Arena(128 * 1024);
  }

  // Use arena...

  // Reset for next call instead of destroying
  tl_arena->Reset();

  return result;
}
```

**Benefits:**
- Single allocation serves many objects
- No per-object deallocation overhead
- Better cache locality
- Zero fragmentation

Reference: [Arena Allocation](https://en.wikipedia.org/wiki/Region-based_memory_management)
