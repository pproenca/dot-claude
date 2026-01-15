# Node.js Native Addons (C++)

**Version 0.1.0**  
Node.js Community  
January 2026

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring codebases. Humans may also find it useful,  
> but guidance here is optimized for automation and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive performance optimization guide for Node.js native addons written in C++, designed for AI agents and LLMs. Contains 38 rules across 8 categories, prioritized by impact from critical (JS/C++ boundary optimization, memory management, async threading) to medium (N-API patterns, build configuration). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.

---

## Table of Contents

1. [JS/C++ Boundary Optimization](#1-jsc-boundary-optimization) — **CRITICAL**
   - 1.1 [Avoid Callbacks in Hot Loops](#11-avoid-callbacks-in-hot-loops)
   - 1.2 [Batch Multiple Operations in Single Call](#12-batch-multiple-operations-in-single-call)
   - 1.3 [Cache Property Accessors Across Calls](#13-cache-property-accessors-across-calls)
   - 1.4 [Return Primitives Over Objects When Possible](#14-return-primitives-over-objects-when-possible)
   - 1.5 [Use TypedArrays for Numeric Data](#15-use-typedarrays-for-numeric-data)
2. [Memory Management](#2-memory-management) — **CRITICAL**
   - 2.1 [Avoid Unnecessary String Copies](#21-avoid-unnecessary-string-copies)
   - 2.2 [Track External Memory with AdjustExternalMemory](#22-track-external-memory-with-adjustexternalmemory)
   - 2.3 [Use Arena Allocators for Temporary Data](#23-use-arena-allocators-for-temporary-data)
   - 2.4 [Use Buffer Pools for Repeated Allocations](#24-use-buffer-pools-for-repeated-allocations)
   - 2.5 [Use Weak References to Prevent Memory Leaks](#25-use-weak-references-to-prevent-memory-leaks)
3. [Thread Safety & Async](#3-thread-safety-async) — **CRITICAL**
   - 3.1 [Avoid Mutex Contention in Hot Paths](#31-avoid-mutex-contention-in-hot-paths)
   - 3.2 [Configure UV_THREADPOOL_SIZE for Workload](#32-configure-uvthreadpoolsize-for-workload)
   - 3.3 [Parallelize Independent Operations Across Workers](#33-parallelize-independent-operations-across-workers)
   - 3.4 [Use AsyncWorker for CPU-Intensive Tasks](#34-use-asyncworker-for-cpu-intensive-tasks)
   - 3.5 [Use ThreadSafeFunction for Callbacks from Threads](#35-use-threadsafefunction-for-callbacks-from-threads)
4. [Data Conversion](#4-data-conversion) — **HIGH**
   - 4.1 [Avoid JSON Serialization for Structured Data](#41-avoid-json-serialization-for-structured-data)
   - 4.2 [Choose Efficient String Encoding](#42-choose-efficient-string-encoding)
   - 4.3 [Optimize Object Serialization for Large Data](#43-optimize-object-serialization-for-large-data)
   - 4.4 [Use Correct Number Type Conversions](#44-use-correct-number-type-conversions)
   - 4.5 [Use Zero-Copy Buffer Access](#45-use-zero-copy-buffer-access)
5. [Handle Management](#5-handle-management) — **HIGH**
   - 5.1 [Always Check Value Types Before Conversion](#51-always-check-value-types-before-conversion)
   - 5.2 [Minimize Handle Creation in Hot Paths](#52-minimize-handle-creation-in-hot-paths)
   - 5.3 [Use EscapableHandleScope for Return Values](#53-use-escapablehandlescope-for-return-values)
   - 5.4 [Use HandleScope in All Native Functions](#54-use-handlescope-in-all-native-functions)
   - 5.5 [Use Persistent References for Long-Lived Values](#55-use-persistent-references-for-long-lived-values)
6. [Object Wrapping](#6-object-wrapping) — **MEDIUM-HIGH**
   - 6.1 [Implement Proper Destructor Cleanup](#61-implement-proper-destructor-cleanup)
   - 6.2 [Prevent GC During Native Operations](#62-prevent-gc-during-native-operations)
   - 6.3 [Use Weak Pointers for Observer Patterns](#63-use-weak-pointers-for-observer-patterns)
7. [N-API Best Practices](#7-n-api-best-practices) — **MEDIUM**
   - 7.1 [Handle Errors with Exceptions](#71-handle-errors-with-exceptions)
   - 7.2 [Register Cleanup Hooks for Module Unload](#72-register-cleanup-hooks-for-module-unload)
   - 7.3 [Target Appropriate N-API Version](#73-target-appropriate-n-api-version)
   - 7.4 [Use DefineClass for Object-Oriented APIs](#74-use-defineclass-for-object-oriented-apis)
   - 7.5 [Use node-addon-api Over Raw N-API](#75-use-node-addon-api-over-raw-n-api)
8. [Build & Module Loading](#8-build-module-loading) — **MEDIUM**
   - 8.1 [Distribute Prebuilt Binaries](#81-distribute-prebuilt-binaries)
   - 8.2 [Minimize Binary Size](#82-minimize-binary-size)
   - 8.3 [Use Context-Aware Addons](#83-use-context-aware-addons)
   - 8.4 [Use Lazy Initialization for Heavy Resources](#84-use-lazy-initialization-for-heavy-resources)
   - 8.5 [Use Optimal Compiler Flags](#85-use-optimal-compiler-flags)

---

## 1. JS/C++ Boundary Optimization

**Impact: CRITICAL**

Every JS↔C++ crossing has significant overhead (~100-1000ns). Minimizing boundary crossings and batching operations yields the largest performance gains.

### 1.1 Avoid Callbacks in Hot Loops

**Impact: CRITICAL (50-200× improvement in tight loops)**

Calling JS callbacks from C++ in a tight loop incurs massive overhead. Each callback requires context switching, handle scope creation, and argument marshaling.

**Incorrect (callback per iteration):**

```cpp
Napi::Value ProcessWithCallback(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array data = info[0].As<Napi::Array>();
  Napi::Function callback = info[1].As<Napi::Function>();

  for (uint32_t i = 0; i < data.Length(); i++) {
    Napi::Value item = data[i];
    // Call JS callback for EACH item - extremely slow
    callback.Call({item});  // ~1000ns per call
  }
  return env.Undefined();
}
```

**Correct (batch results, single callback):**

```cpp
Napi::Value ProcessWithCallback(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array data = info[0].As<Napi::Array>();
  Napi::Function callback = info[1].As<Napi::Function>();

  // Process all items natively
  Napi::Array results = Napi::Array::New(env, data.Length());
  for (uint32_t i = 0; i < data.Length(); i++) {
    Napi::Value item = data[i];
    // Process natively
    results[i] = ProcessNatively(env, item);
  }

  // Single callback with all results
  callback.Call({results});
  return env.Undefined();
}
```

**Alternative (streaming with chunks):**

```cpp
// For very large datasets, callback with chunks
const size_t CHUNK_SIZE = 1000;
for (size_t start = 0; start < length; start += CHUNK_SIZE) {
  size_t end = std::min(start + CHUNK_SIZE, length);
  Napi::Array chunk = Napi::Array::New(env, end - start);
  // Fill chunk
  callback.Call({chunk, Napi::Number::New(env, start)});
}
```

**When NOT to use this pattern:**
- When callback performs async I/O that can overlap with native processing
- When immediate streaming feedback is required for UX

Reference: [V8 Embedder's Guide](https://v8.dev/docs/embed)

### 1.2 Batch Multiple Operations in Single Call

**Impact: CRITICAL (10-100× improvement for repeated operations)**

Each JS→C++ boundary crossing costs ~100-1000ns. When performing many similar operations, batch them into a single native call that processes an array.

**Incorrect (N boundary crossings):**

```javascript
// JavaScript - calling native function in loop
const addon = require('./build/Release/addon');

const results = [];
for (let i = 0; i < 10000; i++) {
  results.push(addon.processItem(items[i]));  // 10,000 boundary crossings
}
```

```cpp
// C++ - processes one item per call
Napi::Value ProcessItem(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  auto item = info[0].As<Napi::Object>();
  // Process single item
  return Napi::Number::New(env, result);
}
```

**Correct (1 boundary crossing):**

```javascript
// JavaScript - single call with array
const addon = require('./build/Release/addon');

const results = addon.processItems(items);  // 1 boundary crossing
```

```cpp
// C++ - processes entire array
Napi::Value ProcessItems(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();
  uint32_t length = items.Length();

  Napi::Array results = Napi::Array::New(env, length);
  for (uint32_t i = 0; i < length; i++) {
    Napi::Value item = items[i];
    // Process item
    results[i] = Napi::Number::New(env, result);
  }
  return results;
}
```

**Benefits:**
- Eliminates N-1 boundary crossings
- Better CPU cache utilization
- Allows native-side vectorization

Reference: [Node-API Documentation](https://nodejs.org/api/n-api.html)

### 1.3 Cache Property Accessors Across Calls

**Impact: CRITICAL (5-20× improvement for repeated property access)**

Looking up object properties by string name requires hash table lookups. Cache `Napi::PropertyDescriptor` or use indexed properties for repeated access patterns.

**Incorrect (string lookup every access):**

```cpp
Napi::Value ProcessObjects(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array objects = info[0].As<Napi::Array>();

  double sum = 0;
  for (uint32_t i = 0; i < objects.Length(); i++) {
    Napi::Object obj = objects[i].As<Napi::Object>();
    // String lookup on EVERY iteration
    sum += obj.Get("value").As<Napi::Number>().DoubleValue();
    sum += obj.Get("weight").As<Napi::Number>().DoubleValue();
  }
  return Napi::Number::New(env, sum);
}
```

**Correct (cached property names):**

```cpp
// Module-level cached property names
static Napi::Reference<Napi::String> cachedValueKey;
static Napi::Reference<Napi::String> cachedWeightKey;

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  // Cache property names once at module init
  cachedValueKey = Napi::Persistent(Napi::String::New(env, "value"));
  cachedWeightKey = Napi::Persistent(Napi::String::New(env, "weight"));
  // ... rest of init
}

Napi::Value ProcessObjects(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array objects = info[0].As<Napi::Array>();

  // Get cached keys once
  Napi::String valueKey = cachedValueKey.Value();
  Napi::String weightKey = cachedWeightKey.Value();

  double sum = 0;
  for (uint32_t i = 0; i < objects.Length(); i++) {
    Napi::Object obj = objects[i].As<Napi::Object>();
    // Use cached keys - faster lookup
    sum += obj.Get(valueKey).As<Napi::Number>().DoubleValue();
    sum += obj.Get(weightKey).As<Napi::Number>().DoubleValue();
  }
  return Napi::Number::New(env, sum);
}
```

**Alternative (use TypedArrays for numeric data):**

```cpp
// Even faster: use Float64Array instead of objects
Napi::Value ProcessTypedArray(const Napi::CallbackInfo& info) {
  Napi::Float64Array data = info[0].As<Napi::Float64Array>();
  double* ptr = data.Data();
  size_t length = data.ElementLength();

  double sum = 0;
  for (size_t i = 0; i < length; i++) {
    sum += ptr[i];  // Direct memory access, no JS overhead
  }
  return Napi::Number::New(info.Env(), sum);
}
```

Reference: [N-API Reference](https://nodejs.org/api/n-api.html#napi_get_named_property)

### 1.4 Return Primitives Over Objects When Possible

**Impact: HIGH (2-5× faster returns)**

Returning JS objects requires heap allocation and handle creation. Primitives (numbers, booleans) are returned inline without allocation.

**Incorrect (object return for simple result):**

```cpp
Napi::Value GetStats(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Heap allocation for every call
  Napi::Object result = Napi::Object::New(env);
  result.Set("count", Napi::Number::New(env, count_));
  result.Set("total", Napi::Number::New(env, total_));
  result.Set("average", Napi::Number::New(env, total_ / count_));
  return result;
}
```

**Correct (primitive returns, batch object creation):**

```cpp
// Separate getters for individual values
Napi::Value GetCount(const Napi::CallbackInfo& info) {
  return Napi::Number::New(info.Env(), count_);
}

Napi::Value GetTotal(const Napi::CallbackInfo& info) {
  return Napi::Number::New(info.Env(), total_);
}

Napi::Value GetAverage(const Napi::CallbackInfo& info) {
  return Napi::Number::New(info.Env(), total_ / count_);
}

// Object version only when caller needs multiple values
Napi::Value GetStats(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Object result = Napi::Object::New(env);
  result.Set("count", Napi::Number::New(env, count_));
  result.Set("total", Napi::Number::New(env, total_));
  result.Set("average", Napi::Number::New(env, total_ / count_));
  return result;
}
```

**Alternative (return TypedArray for multiple numbers):**

```cpp
// For fixed-layout numeric results
Napi::Value GetStatsArray(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Create ArrayBuffer once, reuse across calls
  Napi::Float64Array result = Napi::Float64Array::New(env, 3);
  double* data = result.Data();
  data[0] = count_;
  data[1] = total_;
  data[2] = total_ / count_;
  return result;
}
```

```javascript
// JS side - destructure array
const [count, total, average] = addon.getStatsArray();
```

**When NOT to use this pattern:**
- When the return structure is complex or variable
- When the caller always needs all values together

Reference: [V8 Value Representation](https://v8.dev/blog/pointer-compression)

### 1.5 Use TypedArrays for Numeric Data

**Impact: CRITICAL (20-100× improvement over JS arrays)**

TypedArrays provide direct memory access without per-element JS↔C++ conversion. This eliminates boxing/unboxing overhead and enables SIMD optimization.

**Incorrect (JS Array with boxing):**

```cpp
Napi::Value SumArray(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array arr = info[0].As<Napi::Array>();

  double sum = 0;
  for (uint32_t i = 0; i < arr.Length(); i++) {
    // Each access: boundary crossing + unboxing
    sum += arr.Get(i).As<Napi::Number>().DoubleValue();
  }
  return Napi::Number::New(env, sum);
}
```

```javascript
// JS side - using regular array
const data = [1.0, 2.0, 3.0, /* ... thousands more */];
const result = addon.sumArray(data);
```

**Correct (TypedArray with direct access):**

```cpp
Napi::Value SumTypedArray(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Float64Array arr = info[0].As<Napi::Float64Array>();

  double* data = arr.Data();  // Direct pointer to memory
  size_t length = arr.ElementLength();

  double sum = 0;
  for (size_t i = 0; i < length; i++) {
    sum += data[i];  // Pure C++ memory access
  }
  return Napi::Number::New(env, sum);
}
```

```javascript
// JS side - using Float64Array
const data = new Float64Array([1.0, 2.0, 3.0, /* ... thousands more */]);
const result = addon.sumTypedArray(data);
```

**SIMD-optimized version:**

```cpp
#include <immintrin.h>

Napi::Value SumTypedArraySIMD(const Napi::CallbackInfo& info) {
  Napi::Float64Array arr = info[0].As<Napi::Float64Array>();
  double* data = arr.Data();
  size_t length = arr.ElementLength();

  __m256d sum_vec = _mm256_setzero_pd();
  size_t i = 0;

  // Process 4 doubles at a time
  for (; i + 4 <= length; i += 4) {
    __m256d vec = _mm256_loadu_pd(&data[i]);
    sum_vec = _mm256_add_pd(sum_vec, vec);
  }

  // Horizontal sum
  double temp[4];
  _mm256_storeu_pd(temp, sum_vec);
  double sum = temp[0] + temp[1] + temp[2] + temp[3];

  // Handle remaining elements
  for (; i < length; i++) {
    sum += data[i];
  }

  return Napi::Number::New(info.Env(), sum);
}
```

**Benefits:**
- Zero-copy data sharing between JS and C++
- Cache-friendly contiguous memory layout
- Enables SIMD vectorization
- No garbage collection overhead for numeric data

Reference: [MDN TypedArray](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypedArray)

---

## 2. Memory Management

**Impact: CRITICAL**

Incorrect memory handling causes V8 heap pressure, native memory leaks, and GC pauses that stall the event loop.

### 2.1 Avoid Unnecessary String Copies

**Impact: HIGH (2-10× improvement for string-heavy operations)**

Creating `std::string` from V8 strings copies the entire buffer. For read-only access, use string views or direct buffer access.

**Incorrect (multiple copies):**

```cpp
Napi::Value ProcessString(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Copy 1: V8 string → std::string
  std::string input = info[0].As<Napi::String>().Utf8Value();

  // Copy 2: std::string → another std::string (in function)
  std::string result = DoProcessing(input);

  // Copy 3: std::string → V8 string
  return Napi::String::New(env, result);
}

std::string DoProcessing(std::string input) {  // Copy by value!
  return ProcessImpl(input);
}
```

**Correct (minimized copies):**

```cpp
Napi::Value ProcessString(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Single copy from V8
  std::string input = info[0].As<Napi::String>().Utf8Value();

  // Pass by const reference - no copy
  DoProcessing(input);

  // Return directly
  return Napi::String::New(env, input);
}

void DoProcessing(const std::string& input) {  // No copy!
  ProcessImpl(input);
}
```

**Alternative (direct buffer access for analysis):**

```cpp
Napi::Value AnalyzeString(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::String str = info[0].As<Napi::String>();

  // Get length without copying
  size_t length = str.Utf8Value().size();

  // For simple analysis, use direct N-API calls
  napi_value napi_str = str;
  size_t str_length;
  napi_get_value_string_utf8(env, napi_str, nullptr, 0, &str_length);

  // Only copy if you need the content
  if (NeedToModify(str_length)) {
    std::string content = str.Utf8Value();
    // Modify content
  }

  return Napi::Number::New(env, length);
}
```

**For large strings (external string resource):**

```cpp
// For very large strings, use external string resources
// to share memory with V8 without copying
class ExternalStringResource : public v8::String::ExternalOneByteStringResource {
 public:
  ExternalStringResource(const char* data, size_t length)
      : data_(data), length_(length) {}

  const char* data() const override { return data_; }
  size_t length() const override { return length_; }

 private:
  const char* data_;
  size_t length_;
};
```

**Benefits:**
- Reduced memory bandwidth
- Lower GC pressure
- Better cache utilization

Reference: [V8 String Internals](https://v8.dev/blog/string-processing-in-v8)

### 2.2 Track External Memory with AdjustExternalMemory

**Impact: CRITICAL (prevents OOM crashes and improves GC timing)**

V8's garbage collector doesn't see native memory allocations. Use `AdjustExternalMemory` to inform V8 about native allocations so it can trigger GC appropriately.

**Incorrect (V8 unaware of native allocations):**

```cpp
class LargeBuffer : public Napi::ObjectWrap<LargeBuffer> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports);
  LargeBuffer(const Napi::CallbackInfo& info);

 private:
  std::vector<uint8_t> buffer_;  // V8 doesn't know about this
};

LargeBuffer::LargeBuffer(const Napi::CallbackInfo& info)
    : Napi::ObjectWrap<LargeBuffer>(info) {
  size_t size = info[0].As<Napi::Number>().Uint32Value();
  buffer_.resize(size);  // Allocates native memory - V8 unaware!
  // V8 thinks heap is small, won't GC even as native memory grows
}
```

**Correct (V8 informed of native allocations):**

```cpp
class LargeBuffer : public Napi::ObjectWrap<LargeBuffer> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports);
  LargeBuffer(const Napi::CallbackInfo& info);
  ~LargeBuffer();

 private:
  std::vector<uint8_t> buffer_;
  int64_t allocated_size_ = 0;
};

LargeBuffer::LargeBuffer(const Napi::CallbackInfo& info)
    : Napi::ObjectWrap<LargeBuffer>(info) {
  Napi::Env env = info.Env();
  size_t size = info[0].As<Napi::Number>().Uint32Value();

  buffer_.resize(size);
  allocated_size_ = static_cast<int64_t>(size);

  // Tell V8 about the native allocation
  Napi::MemoryManagement::AdjustExternalMemory(env, allocated_size_);
}

LargeBuffer::~LargeBuffer() {
  // Tell V8 the memory is freed (negative value)
  // Note: Must be called from correct thread context
}

// Use weak callback for proper cleanup
void LargeBuffer::Destructor(Napi::Env env, LargeBuffer* instance) {
  Napi::MemoryManagement::AdjustExternalMemory(env, -instance->allocated_size_);
  delete instance;
}
```

**Benefits:**
- V8 GC triggers at appropriate times
- Prevents memory bloat from unreferenced native objects
- Application memory usage stays predictable

**When NOT to use this pattern:**
- For small allocations (<1KB) - overhead exceeds benefit
- For memory managed by external libraries with own pooling

Reference: [N-API Memory Management](https://nodejs.org/api/n-api.html#napi_adjust_external_memory)

### 2.3 Use Arena Allocators for Temporary Data

**Impact: HIGH (5-20× improvement for complex operations with many small allocations)**

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

### 2.4 Use Buffer Pools for Repeated Allocations

**Impact: CRITICAL (10-50× improvement for high-frequency allocations)**

Creating new Buffers or TypedArrays per operation causes allocation pressure. Pool and reuse buffers for repeated operations.

**Incorrect (allocation per call):**

```cpp
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  size_t size = info[0].As<Napi::Number>().Uint32Value();

  // New allocation EVERY call
  Napi::Buffer<uint8_t> buffer = Napi::Buffer<uint8_t>::New(env, size);
  uint8_t* data = buffer.Data();

  // Fill buffer with processed data
  ProcessInto(data, size);

  return buffer;
}
```

**Correct (pooled buffers):**

```cpp
#include <queue>
#include <mutex>

class BufferPool {
 public:
  static BufferPool& Instance() {
    static BufferPool instance;
    return instance;
  }

  Napi::Buffer<uint8_t> Acquire(Napi::Env env, size_t size) {
    std::lock_guard<std::mutex> lock(mutex_);

    // Find existing buffer of appropriate size
    for (auto it = pool_.begin(); it != pool_.end(); ++it) {
      if (it->ByteLength() >= size) {
        Napi::Buffer<uint8_t> buffer = std::move(*it);
        pool_.erase(it);
        return buffer;
      }
    }

    // No suitable buffer, create new one
    return Napi::Buffer<uint8_t>::New(env, size);
  }

  void Release(Napi::Buffer<uint8_t>&& buffer) {
    std::lock_guard<std::mutex> lock(mutex_);
    if (pool_.size() < MAX_POOL_SIZE) {
      pool_.push_back(std::move(buffer));
    }
    // If pool is full, buffer is destroyed
  }

 private:
  static constexpr size_t MAX_POOL_SIZE = 32;
  std::vector<Napi::Buffer<uint8_t>> pool_;
  std::mutex mutex_;
};

// Usage with Reference counting
class PooledBuffer {
 public:
  Napi::Buffer<uint8_t> buffer;

  PooledBuffer(Napi::Env env, size_t size)
      : buffer(BufferPool::Instance().Acquire(env, size)) {}

  ~PooledBuffer() {
    BufferPool::Instance().Release(std::move(buffer));
  }
};
```

**Alternative (pre-allocated ring buffer):**

```cpp
class RingBuffer {
 public:
  RingBuffer(Napi::Env env, size_t slot_size, size_t num_slots)
      : slot_size_(slot_size), num_slots_(num_slots), current_(0) {
    for (size_t i = 0; i < num_slots; i++) {
      slots_.push_back(Napi::Buffer<uint8_t>::New(env, slot_size));
    }
  }

  Napi::Buffer<uint8_t> GetNext() {
    Napi::Buffer<uint8_t>& slot = slots_[current_];
    current_ = (current_ + 1) % num_slots_;
    return slot;  // Returns reference, not copy
  }

 private:
  size_t slot_size_;
  size_t num_slots_;
  size_t current_;
  std::vector<Napi::Buffer<uint8_t>> slots_;
};
```

**Benefits:**
- Eliminates allocation overhead in hot paths
- Reduces GC pressure
- More predictable latency

Reference: [Memory Pooling Patterns](https://en.wikipedia.org/wiki/Memory_pool)

### 2.5 Use Weak References to Prevent Memory Leaks

**Impact: CRITICAL (eliminates memory leaks in wrapped objects)**

Memory leaks happen when C++ prevents JavaScript objects from being garbage collected. Use weak references and weak callbacks for proper cleanup.

**Incorrect (memory leak from strong reference):**

```cpp
class DataProcessor : public Napi::ObjectWrap<DataProcessor> {
 public:
  DataProcessor(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<DataProcessor>(info) {
    // Store strong reference to callback - LEAK!
    callback_ = Napi::Persistent(info[0].As<Napi::Function>());
    // This prevents the callback from ever being GC'd
  }

 private:
  Napi::Reference<Napi::Function> callback_;
};
```

**Correct (weak reference with cleanup):**

```cpp
class DataProcessor : public Napi::ObjectWrap<DataProcessor> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports) {
    Napi::Function func = DefineClass(env, "DataProcessor", {
      InstanceMethod("dispose", &DataProcessor::Dispose),
    });
    exports.Set("DataProcessor", func);
    return exports;
  }

  DataProcessor(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<DataProcessor>(info) {
    Napi::Env env = info.Env();

    // Use weak reference - allows callback to be GC'd
    callback_ = Napi::Reference<Napi::Function>::New(
      info[0].As<Napi::Function>(),
      0  // ref count = 0 means weak reference
    );
  }

  void Dispose(const Napi::CallbackInfo& info) {
    // Explicit cleanup
    callback_.Reset();
  }

  ~DataProcessor() {
    // Note: destructor may not run until GC
  }

  bool HasCallback() {
    return !callback_.IsEmpty();
  }

  void InvokeCallback(Napi::Env env, Napi::Value arg) {
    if (!callback_.IsEmpty()) {
      Napi::Function cb = callback_.Value();
      if (!cb.IsUndefined()) {
        cb.Call({arg});
      }
    }
  }

 private:
  Napi::Reference<Napi::Function> callback_;
};
```

**Alternative (weak callback pattern):**

```cpp
class Observer {
 public:
  static void SetCallback(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Function callback = info[0].As<Napi::Function>();

    // Store weak reference with destructor callback
    weak_callback_ = Napi::Weak(callback);
    weak_callback_.SetPointer(new CallbackData{env, callback});

    // Set weak callback to clean up when JS object is GC'd
    weak_callback_.SetPointerGCCallBack([](Napi::Env env, void* data, void*) {
      auto* cb_data = static_cast<CallbackData*>(data);
      delete cb_data;  // Clean up native resources
    });
  }

 private:
  struct CallbackData {
    Napi::Env env;
    Napi::Function callback;
  };
  static Napi::Reference<Napi::Function> weak_callback_;
};
```

**Common memory leak scenarios:**
- Storing event listeners without cleanup
- Circular references between C++ and JS objects
- Global caches holding JS references
- Timer callbacks not cleared on shutdown

Reference: [N-API Reference Handling](https://nodejs.org/api/n-api.html#references)

---

## 3. Thread Safety & Async

**Impact: CRITICAL**

Blocking the main thread freezes the event loop. Async workers and thread-safe callbacks enable true parallelism without blocking.

### 3.1 Avoid Mutex Contention in Hot Paths

**Impact: HIGH (2-10× improvement under concurrent load)**

Heavy mutex usage in async workers creates contention that serializes parallel work. Use lock-free structures or fine-grained locking.

**Incorrect (global mutex bottleneck):**

```cpp
std::mutex global_cache_mutex;
std::unordered_map<std::string, Result> cache;

class CachingWorker : public Napi::AsyncWorker {
  void Execute() override {
    for (const auto& key : keys_) {
      {
        // All workers contend on this single mutex
        std::lock_guard<std::mutex> lock(global_cache_mutex);
        auto it = cache.find(key);
        if (it != cache.end()) {
          results_.push_back(it->second);
          continue;
        }
      }

      Result result = ComputeExpensive(key);

      {
        std::lock_guard<std::mutex> lock(global_cache_mutex);  // Again!
        cache[key] = result;
      }
      results_.push_back(result);
    }
  }
};
```

**Correct (lock-free read path):**

```cpp
#include <shared_mutex>
#include <atomic>

std::shared_mutex cache_mutex;
std::unordered_map<std::string, Result> cache;

class OptimizedCachingWorker : public Napi::AsyncWorker {
  void Execute() override {
    for (const auto& key : keys_) {
      // Try read with shared lock (multiple readers allowed)
      {
        std::shared_lock<std::shared_mutex> read_lock(cache_mutex);
        auto it = cache.find(key);
        if (it != cache.end()) {
          results_.push_back(it->second);
          continue;
        }
      }

      // Cache miss - compute without holding lock
      Result result = ComputeExpensive(key);

      // Write with exclusive lock
      {
        std::unique_lock<std::shared_mutex> write_lock(cache_mutex);
        // Double-check (another thread may have computed)
        auto it = cache.find(key);
        if (it == cache.end()) {
          cache[key] = result;
        }
      }
      results_.push_back(result);
    }
  }
};
```

**Alternative (thread-local caching):**

```cpp
class ThreadLocalWorker : public Napi::AsyncWorker {
  void Execute() override {
    // Each thread has its own local cache
    thread_local std::unordered_map<std::string, Result> local_cache;

    for (const auto& key : keys_) {
      // Check thread-local cache first (no locking)
      auto it = local_cache.find(key);
      if (it != local_cache.end()) {
        results_.push_back(it->second);
        continue;
      }

      // Then check shared cache
      {
        std::shared_lock<std::shared_mutex> lock(cache_mutex);
        auto shared_it = shared_cache.find(key);
        if (shared_it != shared_cache.end()) {
          local_cache[key] = shared_it->second;  // Promote to local
          results_.push_back(shared_it->second);
          continue;
        }
      }

      Result result = ComputeExpensive(key);
      local_cache[key] = result;

      // Optionally promote to shared cache
      {
        std::unique_lock<std::shared_mutex> lock(cache_mutex);
        shared_cache[key] = result;
      }

      results_.push_back(result);
    }
  }
};
```

**Lock-free approach with atomics:**

```cpp
#include <atomic>

template<typename T>
class LockFreeStack {
  struct Node {
    T data;
    std::atomic<Node*> next;
  };

  std::atomic<Node*> head_{nullptr};

 public:
  void Push(T value) {
    Node* new_node = new Node{std::move(value)};
    new_node->next = head_.load(std::memory_order_relaxed);
    while (!head_.compare_exchange_weak(
      new_node->next, new_node,
      std::memory_order_release,
      std::memory_order_relaxed
    ));
  }
};
```

Reference: [C++ Concurrency in Action](https://www.manning.com/books/c-plus-plus-concurrency-in-action-second-edition)

### 3.2 Configure UV_THREADPOOL_SIZE for Workload

**Impact: HIGH (2-4× throughput for I/O-bound addons)**

The libuv thread pool defaults to 4 threads. For addons with heavy async operations, increase this to match your workload.

**Incorrect (default pool size):**

```javascript
// No configuration - uses default 4 threads
const addon = require('./build/Release/addon');

// With 100 concurrent async operations, only 4 run in parallel
// 96 operations wait in queue
for (let i = 0; i < 100; i++) {
  addon.asyncOperation(data[i], callback);
}
```

**Correct (sized pool):**

```javascript
// Set BEFORE requiring any native modules
process.env.UV_THREADPOOL_SIZE = '16';  // Must be string

// Or set in environment before starting Node
// UV_THREADPOOL_SIZE=16 node app.js

const addon = require('./build/Release/addon');

// Now 16 operations can run in parallel
for (let i = 0; i < 100; i++) {
  addon.asyncOperation(data[i], callback);
}
```

**Programmatic check and documentation:**

```cpp
// In addon init, document thread pool usage
Napi::Object Init(Napi::Env env, Napi::Object exports) {
  // Check current pool size
  const char* pool_size = std::getenv("UV_THREADPOOL_SIZE");
  int size = pool_size ? std::atoi(pool_size) : 4;

  // Warn if pool might be undersized
  if (size < 8) {
    Napi::Error::New(env,
      "Warning: UV_THREADPOOL_SIZE is " + std::to_string(size) +
      ". Increase to 8+ for better async performance."
    ).ThrowAsJavaScriptException();
  }

  // Export pool info
  exports.Set("threadPoolSize", Napi::Number::New(env, size));

  return exports;
}
```

**Guidelines for sizing:**
- CPU-bound tasks: `UV_THREADPOOL_SIZE` = number of CPU cores
- I/O-bound tasks: `UV_THREADPOOL_SIZE` = 2-4× number of CPU cores
- Mixed workloads: Profile to find optimal value
- Maximum: 1024 (hard limit in libuv)

**Self-sizing addon:**

```cpp
#include <thread>

int RecommendPoolSize(bool io_bound) {
  int cores = std::thread::hardware_concurrency();
  if (io_bound) {
    return std::min(cores * 4, 128);
  }
  return cores;
}

Napi::Value GetRecommendedPoolSize(const Napi::CallbackInfo& info) {
  bool io_bound = info[0].As<Napi::Boolean>().Value();
  return Napi::Number::New(info.Env(), RecommendPoolSize(io_bound));
}
```

```javascript
// Application startup
const addon = require('./build/Release/addon');
const recommended = addon.getRecommendedPoolSize(true);

if (!process.env.UV_THREADPOOL_SIZE) {
  console.warn(`Set UV_THREADPOOL_SIZE=${recommended} for optimal performance`);
}
```

**When NOT to increase pool size:**
- Memory-constrained environments (each thread uses stack space)
- Mostly synchronous operations
- When using custom thread pools instead of libuv's

Reference: [libuv Threadpool Documentation](https://docs.libuv.org/en/v1.x/threadpool.html)

### 3.3 Parallelize Independent Operations Across Workers

**Impact: CRITICAL (N× throughput on multi-core systems)**

For operations on independent data chunks, spawn multiple async workers to utilize all CPU cores.

**Incorrect (sequential processing):**

```cpp
class SingleWorker : public Napi::AsyncWorker {
 public:
  SingleWorker(Napi::Function& cb, std::vector<Item>&& items)
      : Napi::AsyncWorker(cb), items_(std::move(items)) {}

  void Execute() override {
    // Process all items on ONE thread
    for (auto& item : items_) {
      results_.push_back(ProcessItem(item));  // Sequential!
    }
  }

  void OnOK() override { /* return results */ }

 private:
  std::vector<Item> items_;
  std::vector<Result> results_;
};
```

**Correct (parallel workers):**

```cpp
#include <atomic>

class ParallelCoordinator {
 public:
  ParallelCoordinator(
    Napi::Env env,
    Napi::Promise::Deferred deferred,
    std::vector<Item>&& items,
    size_t num_workers
  ) : env_(env),
      deferred_(deferred),
      items_(std::move(items)),
      num_workers_(num_workers),
      completed_(0) {
    results_.resize(items_.size());
  }

  void Start() {
    size_t chunk_size = (items_.size() + num_workers_ - 1) / num_workers_;

    for (size_t i = 0; i < num_workers_; i++) {
      size_t start = i * chunk_size;
      size_t end = std::min(start + chunk_size, items_.size());

      if (start < items_.size()) {
        auto* worker = new ChunkWorker(this, start, end);
        worker->Queue();
      }
    }
  }

  void OnChunkComplete(size_t start, size_t end, std::vector<Result>&& chunk_results) {
    // Copy results to correct positions
    for (size_t i = start; i < end; i++) {
      results_[i] = std::move(chunk_results[i - start]);
    }

    // Check if all workers done
    if (++completed_ == num_workers_) {
      // All done - resolve promise on main thread
      deferred_.Resolve(CreateResultArray());
    }
  }

 private:
  class ChunkWorker : public Napi::AsyncWorker {
   public:
    ChunkWorker(ParallelCoordinator* coord, size_t start, size_t end)
        : Napi::AsyncWorker(coord->env_),
          coordinator_(coord),
          start_(start),
          end_(end) {}

    void Execute() override {
      // Process chunk on this thread
      for (size_t i = start_; i < end_; i++) {
        results_.push_back(ProcessItem(coordinator_->items_[i]));
      }
    }

    void OnOK() override {
      coordinator_->OnChunkComplete(start_, end_, std::move(results_));
    }

   private:
    ParallelCoordinator* coordinator_;
    size_t start_, end_;
    std::vector<Result> results_;
  };

  Napi::Env env_;
  Napi::Promise::Deferred deferred_;
  std::vector<Item> items_;
  std::vector<Result> results_;
  size_t num_workers_;
  std::atomic<size_t> completed_;
};

Napi::Value ProcessParallel(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  auto items = ExtractItems(info[0]);

  // Use number of CPU cores
  size_t num_workers = std::thread::hardware_concurrency();

  Napi::Promise::Deferred deferred = Napi::Promise::Deferred::New(env);
  auto* coordinator = new ParallelCoordinator(
    env, deferred, std::move(items), num_workers
  );
  coordinator->Start();

  return deferred.Promise();
}
```

**Simpler approach with thread pool:**

```cpp
#include <thread>
#include <future>

void Execute() override {
  size_t num_threads = std::thread::hardware_concurrency();
  std::vector<std::future<std::vector<Result>>> futures;

  size_t chunk_size = (items_.size() + num_threads - 1) / num_threads;

  for (size_t t = 0; t < num_threads; t++) {
    size_t start = t * chunk_size;
    size_t end = std::min(start + chunk_size, items_.size());

    futures.push_back(std::async(std::launch::async, [this, start, end]() {
      std::vector<Result> chunk_results;
      for (size_t i = start; i < end; i++) {
        chunk_results.push_back(ProcessItem(items_[i]));
      }
      return chunk_results;
    }));
  }

  // Collect results
  for (auto& future : futures) {
    auto chunk = future.get();
    results_.insert(results_.end(), chunk.begin(), chunk.end());
  }
}
```

Reference: [libuv Thread Pool](https://docs.libuv.org/en/v1.x/threadpool.html)

### 3.4 Use AsyncWorker for CPU-Intensive Tasks

**Impact: CRITICAL (prevents event loop blocking, enables true parallelism)**

Synchronous C++ code blocks the Node.js event loop. Use `Napi::AsyncWorker` to offload CPU-intensive work to background threads.

**Incorrect (blocks event loop):**

```cpp
Napi::Value ProcessLargeDataset(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Buffer<uint8_t> data = info[0].As<Napi::Buffer<uint8_t>>();

  // This blocks the event loop for seconds!
  std::vector<uint8_t> result = HeavyComputation(
    data.Data(),
    data.ByteLength()
  );

  return Napi::Buffer<uint8_t>::Copy(env, result.data(), result.size());
}
```

**Correct (async worker):**

```cpp
class ComputationWorker : public Napi::AsyncWorker {
 public:
  ComputationWorker(
    Napi::Function& callback,
    std::vector<uint8_t>&& input_data
  ) : Napi::AsyncWorker(callback),
      input_data_(std::move(input_data)) {}

  // Runs on background thread - doesn't block event loop
  void Execute() override {
    result_ = HeavyComputation(input_data_.data(), input_data_.size());
  }

  // Runs on main thread after Execute completes
  void OnOK() override {
    Napi::Env env = Env();
    Callback().Call({
      env.Null(),
      Napi::Buffer<uint8_t>::Copy(env, result_.data(), result_.size())
    });
  }

  void OnError(const Napi::Error& error) override {
    Callback().Call({error.Value()});
  }

 private:
  std::vector<uint8_t> input_data_;
  std::vector<uint8_t> result_;
};

Napi::Value ProcessLargeDatasetAsync(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Buffer<uint8_t> data = info[0].As<Napi::Buffer<uint8_t>>();
  Napi::Function callback = info[1].As<Napi::Function>();

  // Copy input data since buffer may be GC'd during async operation
  std::vector<uint8_t> input_copy(data.Data(), data.Data() + data.ByteLength());

  // Queue work on libuv thread pool
  ComputationWorker* worker = new ComputationWorker(callback, std::move(input_copy));
  worker->Queue();

  return env.Undefined();
}
```

**Promise-based version:**

```cpp
class ComputationWorker : public Napi::AsyncWorker {
 public:
  ComputationWorker(
    Napi::Env env,
    Napi::Promise::Deferred deferred,
    std::vector<uint8_t>&& input_data
  ) : Napi::AsyncWorker(env),
      deferred_(deferred),
      input_data_(std::move(input_data)) {}

  void Execute() override {
    result_ = HeavyComputation(input_data_.data(), input_data_.size());
  }

  void OnOK() override {
    Napi::Env env = Env();
    deferred_.Resolve(
      Napi::Buffer<uint8_t>::Copy(env, result_.data(), result_.size())
    );
  }

  void OnError(const Napi::Error& error) override {
    deferred_.Reject(error.Value());
  }

 private:
  Napi::Promise::Deferred deferred_;
  std::vector<uint8_t> input_data_;
  std::vector<uint8_t> result_;
};

Napi::Value ProcessLargeDatasetPromise(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Buffer<uint8_t> data = info[0].As<Napi::Buffer<uint8_t>>();

  Napi::Promise::Deferred deferred = Napi::Promise::Deferred::New(env);
  std::vector<uint8_t> input_copy(data.Data(), data.Data() + data.ByteLength());

  ComputationWorker* worker = new ComputationWorker(env, deferred, std::move(input_copy));
  worker->Queue();

  return deferred.Promise();
}
```

**When NOT to use this pattern:**
- Operations completing in <1ms (async overhead exceeds benefit)
- When you need synchronous result for initialization

Reference: [N-API AsyncWorker](https://nodejs.org/api/n-api.html#asynchronous-operations)

### 3.5 Use ThreadSafeFunction for Callbacks from Threads

**Impact: CRITICAL (enables safe JS callbacks from any thread)**

Calling JavaScript from non-main threads crashes Node.js. Use `Napi::ThreadSafeFunction` to safely invoke JS callbacks from any thread.

**Incorrect (crashes):**

```cpp
void BackgroundThread(Napi::Function callback, Napi::Env env) {
  std::thread([callback, env]() {
    // CRASH! Calling JS from non-main thread
    callback.Call({Napi::String::New(env, "result")});
  }).detach();
}
```

**Correct (thread-safe function):**

```cpp
class EventEmitter {
 public:
  static Napi::Value Start(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Function callback = info[0].As<Napi::Function>();

    // Create thread-safe function
    tsfn_ = Napi::ThreadSafeFunction::New(
      env,
      callback,
      "EventEmitter",  // Resource name for debugging
      0,               // Max queue size (0 = unlimited)
      1                // Initial thread count
    );

    // Start background thread
    worker_ = std::thread([]() {
      while (running_) {
        // Generate event data
        std::string data = GenerateEvent();

        // Queue call to JS - safe from any thread!
        tsfn_.BlockingCall([data](Napi::Env env, Napi::Function callback) {
          callback.Call({Napi::String::New(env, data)});
        });

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
      }
    });

    return env.Undefined();
  }

  static Napi::Value Stop(const Napi::CallbackInfo& info) {
    running_ = false;
    if (worker_.joinable()) {
      worker_.join();
    }
    tsfn_.Release();
    return info.Env().Undefined();
  }

 private:
  static Napi::ThreadSafeFunction tsfn_;
  static std::thread worker_;
  static std::atomic<bool> running_;
};
```

**With custom data transfer:**

```cpp
struct EventData {
  std::string message;
  int code;
};

void CallJS(Napi::Env env, Napi::Function callback, EventData* data) {
  if (env != nullptr && callback != nullptr) {
    Napi::Object result = Napi::Object::New(env);
    result.Set("message", Napi::String::New(env, data->message));
    result.Set("code", Napi::Number::New(env, data->code));
    callback.Call({result});
  }
  delete data;  // Clean up after use
}

using TSFN = Napi::TypedThreadSafeFunction<void, EventData, CallJS>;

class TypedEmitter {
 public:
  static Napi::Value Start(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    tsfn_ = TSFN::New(
      env,
      info[0].As<Napi::Function>(),
      "TypedEmitter",
      0,
      1
    );

    worker_ = std::thread([]() {
      while (running_) {
        // Create data on heap - will be freed after callback
        EventData* data = new EventData{"event occurred", 42};
        tsfn_.BlockingCall(data);
      }
    });

    return env.Undefined();
  }

 private:
  static TSFN tsfn_;
  static std::thread worker_;
  static std::atomic<bool> running_;
};
```

**Non-blocking variant:**

```cpp
// Use NonBlockingCall when you can't afford to wait
napi_status status = tsfn_.NonBlockingCall(data);
if (status == napi_queue_full) {
  // Queue is full - handle backpressure
  delete data;  // Don't leak
  HandleBackpressure();
}
```

Reference: [ThreadSafeFunction Documentation](https://nodejs.org/api/n-api.html#thread-safe-functions)

---

## 4. Data Conversion

**Impact: HIGH**

Converting between JS and C++ types is expensive. Zero-copy techniques and efficient encoding reduce CPU and memory overhead.

### 4.1 Avoid JSON Serialization for Structured Data

**Impact: MEDIUM-HIGH (5-20× faster than JSON.parse/stringify roundtrip)**

Don't serialize to JSON in C++ and parse in JS (or vice versa). Use direct object construction or binary protocols.

**Incorrect (JSON roundtrip):**

```cpp
Napi::Value GetData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Build JSON string in C++
  std::string json = "{\"items\":[";
  for (size_t i = 0; i < items.size(); i++) {
    if (i > 0) json += ",";
    json += "{\"id\":" + std::to_string(items[i].id) +
            ",\"name\":\"" + EscapeJson(items[i].name) +
            "\",\"value\":" + std::to_string(items[i].value) + "}";
  }
  json += "]}";

  // Return string - JS will need to JSON.parse()
  return Napi::String::New(env, json);
}
```

```javascript
// JavaScript
const result = JSON.parse(addon.getData());  // Expensive parse!
```

**Correct (direct object construction):**

```cpp
Napi::Value GetData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  Napi::Object result = Napi::Object::New(env);
  Napi::Array itemsArray = Napi::Array::New(env, items.size());

  for (size_t i = 0; i < items.size(); i++) {
    Napi::Object item = Napi::Object::New(env);
    item.Set("id", Napi::Number::New(env, items[i].id));
    item.Set("name", Napi::String::New(env, items[i].name));
    item.Set("value", Napi::Number::New(env, items[i].value));
    itemsArray[i] = item;
  }

  result.Set("items", itemsArray);
  return result;
}
```

```javascript
// JavaScript - no parsing needed
const result = addon.getData();
console.log(result.items[0].name);
```

**For very large datasets - binary protocol:**

```cpp
// Pack data into binary format
Napi::Value GetDataBinary(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Calculate total size
  size_t size = 4;  // item count
  for (const auto& item : items) {
    size += 4 + 4 + 2 + item.name.size();  // id + value + name_len + name
  }

  Napi::Buffer<uint8_t> buffer = Napi::Buffer<uint8_t>::New(env, size);
  uint8_t* ptr = buffer.Data();

  // Write count
  *reinterpret_cast<uint32_t*>(ptr) = items.size();
  ptr += 4;

  // Write items
  for (const auto& item : items) {
    *reinterpret_cast<int32_t*>(ptr) = item.id;
    ptr += 4;
    *reinterpret_cast<float*>(ptr) = item.value;
    ptr += 4;
    *reinterpret_cast<uint16_t*>(ptr) = item.name.size();
    ptr += 2;
    memcpy(ptr, item.name.data(), item.name.size());
    ptr += item.name.size();
  }

  return buffer;
}
```

```javascript
// JavaScript - fast binary parsing
function parseData(buffer) {
  const view = new DataView(buffer.buffer);
  let offset = 0;

  const count = view.getUint32(offset, true);
  offset += 4;

  const items = [];
  for (let i = 0; i < count; i++) {
    const id = view.getInt32(offset, true);
    offset += 4;
    const value = view.getFloat32(offset, true);
    offset += 4;
    const nameLen = view.getUint16(offset, true);
    offset += 2;
    const name = buffer.toString('utf8', offset, offset + nameLen);
    offset += nameLen;

    items.push({ id, name, value });
  }

  return { items };
}
```

**When JSON might be acceptable:**
- Debugging or logging
- Interop with JSON-based APIs
- Small, infrequent data transfers

Reference: [V8 JSON Performance](https://v8.dev/blog/cost-of-javascript-2019)

### 4.2 Choose Efficient String Encoding

**Impact: HIGH (2-5× faster string conversion)**

V8 stores strings in either Latin-1 (one-byte) or UTF-16. Choose the conversion that matches your needs to avoid unnecessary transcoding.

**Incorrect (always UTF-8):**

```cpp
Napi::Value ProcessString(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::String str = info[0].As<Napi::String>();

  // Always converts to UTF-8, even for ASCII strings
  std::string utf8 = str.Utf8Value();

  // Process...

  return Napi::String::New(env, result);  // Converts back from UTF-8
}
```

**Correct (choose based on content):**

```cpp
Napi::Value ProcessString(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::String str = info[0].As<Napi::String>();

  // Check if string is one-byte (ASCII/Latin-1)
  napi_value napi_str = str;
  napi_valuetype type;
  napi_typeof(env, napi_str, &type);

  // For ASCII-only processing, use Latin-1 (no transcoding for ASCII)
  if (IsAsciiOnly()) {
    std::u16string utf16 = str.Utf16Value();
    // Process as wide chars...
  } else {
    std::string utf8 = str.Utf8Value();
    // Process as UTF-8...
  }

  return result;
}
```

**For known ASCII content:**

```cpp
// When you know content is ASCII, use direct buffer access
Napi::Value ProcessAscii(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::String str = info[0].As<Napi::String>();

  // Get length first
  size_t length;
  napi_get_value_string_latin1(env, str, nullptr, 0, &length);

  // Allocate and copy
  std::string ascii(length, '\0');
  napi_get_value_string_latin1(env, str, &ascii[0], length + 1, nullptr);

  // Process ASCII string
  ProcessAsciiImpl(ascii);

  return Napi::String::New(env, ascii);
}
```

**Return strings efficiently:**

```cpp
// For small strings, New() is fine
return Napi::String::New(env, small_result);

// For large strings created from raw data
extern "C" char* large_data;
size_t large_length;

// Use external string when data is already in memory
// (advanced - requires custom string resource)
```

**Avoid repeated conversions:**

```cpp
// BAD - converts string twice
void ProcessTwice(const Napi::CallbackInfo& info) {
  Napi::String str = info[0].As<Napi::String>();

  std::string a = str.Utf8Value();  // Convert
  DoSomething(a);

  std::string b = str.Utf8Value();  // Convert AGAIN
  DoSomethingElse(b);
}

// GOOD - convert once
void ProcessOnce(const Napi::CallbackInfo& info) {
  Napi::String str = info[0].As<Napi::String>();

  std::string converted = str.Utf8Value();  // Convert once
  DoSomething(converted);
  DoSomethingElse(converted);
}
```

Reference: [V8 String Types](https://v8.dev/blog/string)

### 4.3 Optimize Object Serialization for Large Data

**Impact: HIGH (3-10× faster for complex object graphs)**

For complex objects crossing the JS/C++ boundary, use structured serialization or custom binary formats instead of property-by-property conversion.

**Incorrect (property-by-property conversion):**

```cpp
Napi::Value SerializeObjects(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array objects = info[0].As<Napi::Array>();

  std::vector<MyStruct> result;
  for (uint32_t i = 0; i < objects.Length(); i++) {
    Napi::Object obj = objects[i].As<Napi::Object>();

    MyStruct item;
    // Each Get() is a hash lookup + type conversion
    item.id = obj.Get("id").As<Napi::Number>().Int32Value();
    item.name = obj.Get("name").As<Napi::String>().Utf8Value();
    item.x = obj.Get("x").As<Napi::Number>().DoubleValue();
    item.y = obj.Get("y").As<Napi::Number>().DoubleValue();
    item.z = obj.Get("z").As<Napi::Number>().DoubleValue();
    // ... more properties

    result.push_back(item);
  }

  return ProcessStructs(result);
}
```

**Correct (TypedArray for numeric fields):**

```cpp
// JavaScript side - prepare data in TypedArrays
// const ids = new Int32Array(objects.map(o => o.id));
// const positions = new Float64Array(objects.flatMap(o => [o.x, o.y, o.z]));
// addon.processOptimized(ids, positions, names);

Napi::Value ProcessOptimized(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Direct memory access for numeric data
  Napi::Int32Array ids = info[0].As<Napi::Int32Array>();
  Napi::Float64Array positions = info[1].As<Napi::Float64Array>();
  Napi::Array names = info[2].As<Napi::Array>();

  int32_t* id_ptr = ids.Data();
  double* pos_ptr = positions.Data();
  size_t count = ids.ElementLength();

  std::vector<MyStruct> result(count);
  for (size_t i = 0; i < count; i++) {
    result[i].id = id_ptr[i];
    result[i].x = pos_ptr[i * 3];
    result[i].y = pos_ptr[i * 3 + 1];
    result[i].z = pos_ptr[i * 3 + 2];
    // Only string needs JS access
    result[i].name = names[i].As<Napi::String>().Utf8Value();
  }

  return ProcessStructs(result);
}
```

**Alternative (binary protocol):**

```cpp
// Define binary format
struct PackedData {
  int32_t id;
  float x, y, z;
  uint16_t name_length;
  // followed by name_length bytes of name
};

Napi::Value ProcessBinary(const Napi::CallbackInfo& info) {
  Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();
  uint8_t* data = buffer.Data();
  size_t length = buffer.Length();

  std::vector<MyStruct> result;
  size_t offset = 0;

  while (offset < length) {
    PackedData* packed = reinterpret_cast<PackedData*>(data + offset);
    offset += sizeof(PackedData);

    MyStruct item;
    item.id = packed->id;
    item.x = packed->x;
    item.y = packed->y;
    item.z = packed->z;
    item.name = std::string(
      reinterpret_cast<char*>(data + offset),
      packed->name_length
    );
    offset += packed->name_length;

    result.push_back(std::move(item));
  }

  return ProcessStructs(result);
}
```

```javascript
// JavaScript helper to pack objects
function packObjects(objects) {
  const parts = [];
  for (const obj of objects) {
    const nameBytes = Buffer.from(obj.name);
    const header = Buffer.alloc(18);  // 4 + 4*3 + 2
    header.writeInt32LE(obj.id, 0);
    header.writeFloatLE(obj.x, 4);
    header.writeFloatLE(obj.y, 8);
    header.writeFloatLE(obj.z, 12);
    header.writeUInt16LE(nameBytes.length, 16);
    parts.push(header, nameBytes);
  }
  return Buffer.concat(parts);
}
```

Reference: [MessagePack](https://msgpack.org/) for a standard binary serialization format.

### 4.4 Use Correct Number Type Conversions

**Impact: MEDIUM-HIGH (avoids precision loss and range errors)**

JavaScript numbers are IEEE 754 doubles. Using incorrect C++ types causes silent precision loss or crashes.

**Incorrect (wrong types):**

```cpp
Napi::Value ProcessNumber(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // BUG: Int32Value() truncates values > 2^31
  int32_t large = info[0].As<Napi::Number>().Int32Value();
  // Input: 3000000000 → Output: -1294967296

  // BUG: Uint32Value() wraps negative values
  uint32_t positive = info[1].As<Napi::Number>().Uint32Value();
  // Input: -1 → Output: 4294967295

  // BUG: Float loses precision for large integers
  float value = info[2].As<Napi::Number>().FloatValue();
  // Input: 16777217 → Output: 16777216 (precision lost)
}
```

**Correct (appropriate types):**

```cpp
Napi::Value ProcessNumber(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // For large integers, use int64_t or double
  int64_t large = info[0].As<Napi::Number>().Int64Value();

  // For general numbers, use double (matches JS precision)
  double value = info[1].As<Napi::Number>().DoubleValue();

  // For validated small integers, int32_t is fine
  if (IsValidInt32(info[2])) {
    int32_t small = info[2].As<Napi::Number>().Int32Value();
  }
}

bool IsValidInt32(Napi::Value val) {
  double d = val.As<Napi::Number>().DoubleValue();
  return d >= INT32_MIN && d <= INT32_MAX && d == std::floor(d);
}
```

**Safe conversion helpers:**

```cpp
#include <limits>
#include <cmath>

std::optional<int32_t> SafeToInt32(const Napi::Value& val) {
  if (!val.IsNumber()) return std::nullopt;

  double d = val.As<Napi::Number>().DoubleValue();

  if (std::isnan(d) || std::isinf(d)) return std::nullopt;
  if (d < INT32_MIN || d > INT32_MAX) return std::nullopt;
  if (d != std::trunc(d)) return std::nullopt;  // Not an integer

  return static_cast<int32_t>(d);
}

std::optional<uint32_t> SafeToUint32(const Napi::Value& val) {
  if (!val.IsNumber()) return std::nullopt;

  double d = val.As<Napi::Number>().DoubleValue();

  if (std::isnan(d) || std::isinf(d)) return std::nullopt;
  if (d < 0 || d > UINT32_MAX) return std::nullopt;
  if (d != std::trunc(d)) return std::nullopt;

  return static_cast<uint32_t>(d);
}

// Usage
Napi::Value SafeProcess(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  auto index = SafeToUint32(info[0]);
  if (!index) {
    Napi::TypeError::New(env, "Expected valid uint32 index")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }

  ProcessIndex(*index);
  return env.Undefined();
}
```

**BigInt for large integers:**

```cpp
// For integers > 2^53 - 1, use BigInt
Napi::Value ProcessBigInt(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  if (info[0].IsBigInt()) {
    Napi::BigInt bi = info[0].As<Napi::BigInt>();
    bool lossless;
    int64_t value = bi.Int64Value(&lossless);

    if (!lossless) {
      // Value doesn't fit in int64_t
      // Use bi.ToWords() for arbitrary precision
    }
  }

  return env.Undefined();
}

// Return BigInt
Napi::Value ReturnLargeInt(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  uint64_t large_value = 9007199254740993ULL;  // > MAX_SAFE_INTEGER

  return Napi::BigInt::New(env, large_value);
}
```

Reference: [MDN Number](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number)

### 4.5 Use Zero-Copy Buffer Access

**Impact: HIGH (eliminates buffer copying overhead entirely)**

When receiving Buffer or ArrayBuffer from JS, access the underlying memory directly instead of copying.

**Incorrect (unnecessary copy):**

```cpp
Napi::Value ProcessBuffer(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();

  // Copy into vector - wastes memory and CPU
  std::vector<uint8_t> data(buffer.Data(), buffer.Data() + buffer.Length());

  ProcessData(data.data(), data.size());

  return env.Undefined();
}
```

**Correct (direct access):**

```cpp
Napi::Value ProcessBuffer(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();

  // Direct pointer access - no copy
  uint8_t* data = buffer.Data();
  size_t length = buffer.Length();

  ProcessData(data, length);

  return env.Undefined();
}
```

**For ArrayBuffer:**

```cpp
Napi::Value ProcessArrayBuffer(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::ArrayBuffer ab = info[0].As<Napi::ArrayBuffer>();

  // Direct access to ArrayBuffer data
  void* data = ab.Data();
  size_t length = ab.ByteLength();

  ProcessData(static_cast<uint8_t*>(data), length);

  return env.Undefined();
}
```

**Returning data without copy (External Buffer):**

```cpp
class NativeBuffer {
 public:
  NativeBuffer(size_t size) : data_(size) {
    // Fill with native data
    GenerateData(data_.data(), data_.size());
  }

  uint8_t* Data() { return data_.data(); }
  size_t Size() { return data_.size(); }

 private:
  std::vector<uint8_t> data_;
};

Napi::Value CreateExternalBuffer(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  size_t size = info[0].As<Napi::Number>().Uint32Value();

  // Native buffer with our data
  NativeBuffer* native = new NativeBuffer(size);

  // Create JS Buffer wrapping native memory - NO COPY
  return Napi::Buffer<uint8_t>::New(
    env,
    native->Data(),
    native->Size(),
    // Destructor called when JS Buffer is GC'd
    [](Napi::Env, uint8_t*, NativeBuffer* hint) {
      delete hint;
    },
    native
  );
}
```

**Warning - data lifetime:**

```cpp
// DANGEROUS - data may be GC'd during async operation
Napi::Value DangerousAsync(const Napi::CallbackInfo& info) {
  Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();
  uint8_t* data = buffer.Data();  // Pointer to JS-managed memory

  // BUG: buffer may be GC'd while async work is pending!
  QueueAsyncWork([data]() {
    ProcessData(data, ...);  // CRASH - data might be freed
  });

  return info.Env().Undefined();
}

// SAFE - reference prevents GC
Napi::Value SafeAsync(const Napi::CallbackInfo& info) {
  Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();

  // Store reference to prevent GC
  auto ref = Napi::Persistent(buffer);
  uint8_t* data = buffer.Data();
  size_t length = buffer.Length();

  QueueAsyncWork([data, length, ref = std::move(ref)]() {
    ProcessData(data, length);  // Safe - ref keeps buffer alive
  });

  return info.Env().Undefined();
}
```

Reference: [Node.js Buffer Documentation](https://nodejs.org/api/buffer.html)

---

## 5. Handle Management

**Impact: HIGH**

V8 handles must be properly scoped and escaped to prevent crashes and memory leaks. HandleScope misuse is a common source of bugs.

### 5.1 Always Check Value Types Before Conversion

**Impact: HIGH (prevents crashes from type mismatches)**

Calling `.As<T>()` on a value of the wrong type causes undefined behavior or crashes. Always validate types first.

**Incorrect (no validation):**

```cpp
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // CRASH if info[0] is not a number
  int32_t count = info[0].As<Napi::Number>().Int32Value();

  // CRASH if info[1] is not a string
  std::string name = info[1].As<Napi::String>().Utf8Value();

  // CRASH if info[2] is not an array
  Napi::Array items = info[2].As<Napi::Array>();
}
```

**Correct (validated types):**

```cpp
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Validate argument count
  if (info.Length() < 3) {
    Napi::TypeError::New(env, "Expected 3 arguments")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }

  // Validate and convert each argument
  if (!info[0].IsNumber()) {
    Napi::TypeError::New(env, "First argument must be a number")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }
  int32_t count = info[0].As<Napi::Number>().Int32Value();

  if (!info[1].IsString()) {
    Napi::TypeError::New(env, "Second argument must be a string")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }
  std::string name = info[1].As<Napi::String>().Utf8Value();

  if (!info[2].IsArray()) {
    Napi::TypeError::New(env, "Third argument must be an array")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }
  Napi::Array items = info[2].As<Napi::Array>();

  // Now safe to process
  return DoProcess(env, count, name, items);
}
```

**Type checking helper:**

```cpp
template<typename T>
std::optional<T> SafeCast(const Napi::Value& value);

template<>
std::optional<int32_t> SafeCast(const Napi::Value& value) {
  if (!value.IsNumber()) return std::nullopt;
  return value.As<Napi::Number>().Int32Value();
}

template<>
std::optional<std::string> SafeCast(const Napi::Value& value) {
  if (!value.IsString()) return std::nullopt;
  return value.As<Napi::String>().Utf8Value();
}

template<>
std::optional<Napi::Array> SafeCast(const Napi::Value& value) {
  if (!value.IsArray()) return std::nullopt;
  return value.As<Napi::Array>();
}

// Usage
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  auto count = SafeCast<int32_t>(info[0]);
  auto name = SafeCast<std::string>(info[1]);
  auto items = SafeCast<Napi::Array>(info[2]);

  if (!count || !name || !items) {
    Napi::TypeError::New(env, "Invalid argument types")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }

  return DoProcess(env, *count, *name, *items);
}
```

**Check for null/undefined:**

```cpp
Napi::Value ProcessOptional(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // Handle optional arguments
  std::string name = "default";
  if (info.Length() > 0 && !info[0].IsNull() && !info[0].IsUndefined()) {
    if (!info[0].IsString()) {
      Napi::TypeError::New(env, "Name must be a string if provided")
        .ThrowAsJavaScriptException();
      return env.Undefined();
    }
    name = info[0].As<Napi::String>().Utf8Value();
  }

  return Process(env, name);
}
```

Reference: [node-addon-api Type Checking](https://github.com/nodejs/node-addon-api/blob/main/doc/value.md)

### 5.2 Minimize Handle Creation in Hot Paths

**Impact: MEDIUM-HIGH (reduces GC pressure and improves throughput)**

Every `Napi::Value` creation allocates a handle. In hot paths, minimize handle creation by reusing values and batching operations.

**Incorrect (excessive handles):**

```cpp
Napi::Value SumProducts(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();

  double total = 0;
  for (uint32_t i = 0; i < items.Length(); i++) {
    Napi::HandleScope scope(env);
    Napi::Object item = items[i].As<Napi::Object>();

    // Creating string handles on every iteration
    Napi::Value price = item.Get("price");      // "price" → new handle
    Napi::Value quantity = item.Get("quantity"); // "quantity" → new handle

    total += price.As<Napi::Number>().DoubleValue() *
             quantity.As<Napi::Number>().DoubleValue();
  }

  return Napi::Number::New(env, total);
}
```

**Correct (cached property names):**

```cpp
// Module-level cached keys
static Napi::Reference<Napi::String> priceKey;
static Napi::Reference<Napi::String> quantityKey;

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  // Create once at init
  priceKey = Napi::Persistent(Napi::String::New(env, "price"));
  quantityKey = Napi::Persistent(Napi::String::New(env, "quantity"));

  exports.Set("sumProducts",
    Napi::Function::New(env, SumProducts));
  return exports;
}

Napi::Value SumProducts(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();

  // Get cached keys once
  Napi::String pKey = priceKey.Value();
  Napi::String qKey = quantityKey.Value();

  double total = 0;
  for (uint32_t i = 0; i < items.Length(); i++) {
    Napi::HandleScope scope(env);
    Napi::Object item = items[i].As<Napi::Object>();

    // Reuse cached key handles
    total += item.Get(pKey).As<Napi::Number>().DoubleValue() *
             item.Get(qKey).As<Napi::Number>().DoubleValue();
  }

  return Napi::Number::New(env, total);
}
```

**Even better (use TypedArrays):**

```cpp
// JavaScript preprocessing:
// const prices = new Float64Array(items.map(i => i.price));
// const quantities = new Float64Array(items.map(i => i.quantity));
// addon.sumProductsOptimized(prices, quantities);

Napi::Value SumProductsOptimized(const Napi::CallbackInfo& info) {
  Napi::Float64Array prices = info[0].As<Napi::Float64Array>();
  Napi::Float64Array quantities = info[1].As<Napi::Float64Array>();

  double* p = prices.Data();
  double* q = quantities.Data();
  size_t len = prices.ElementLength();

  double total = 0;
  for (size_t i = 0; i < len; i++) {
    total += p[i] * q[i];  // No handles at all in loop!
  }

  return Napi::Number::New(info.Env(), total);
}
```

**Batch return value creation:**

```cpp
// BAD - creates handles in loop then copies to array
Napi::Value ProcessAll(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  std::vector<Napi::Value> results;

  for (size_t i = 0; i < count; i++) {
    results.push_back(Napi::Number::New(env, Process(i)));
  }

  Napi::Array arr = Napi::Array::New(env, results.size());
  for (size_t i = 0; i < results.size(); i++) {
    arr[i] = results[i];
  }
  return arr;
}

// GOOD - create array first, fill directly
Napi::Value ProcessAll(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  Napi::Array arr = Napi::Array::New(env, count);
  for (size_t i = 0; i < count; i++) {
    arr[i] = Napi::Number::New(env, Process(i));
  }
  return arr;
}
```

Reference: [V8 Handles and Garbage Collection](https://v8.dev/docs/embed#handles-and-garbage-collection)

### 5.3 Use EscapableHandleScope for Return Values

**Impact: HIGH (prevents use-after-free crashes)**

When a helper function creates a value that needs to be returned to the caller, use `EscapableHandleScope` and `Escape()` to promote the value out of the local scope.

**Incorrect (dangling handle):**

```cpp
Napi::Object CreateResult(Napi::Env env, int value) {
  // Regular scope - values destroyed on exit
  Napi::HandleScope scope(env);

  Napi::Object result = Napi::Object::New(env);
  result.Set("value", Napi::Number::New(env, value));

  return result;  // BUG: result's handle is invalid after scope exits!
}

Napi::Value GetResult(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  Napi::Object obj = CreateResult(env, 42);  // Dangling handle!
  obj.Set("extra", Napi::Boolean::New(env, true));  // CRASH or corruption

  return obj;
}
```

**Correct (escaped handle):**

```cpp
Napi::Object CreateResult(Napi::Env env, int value) {
  // Escapable scope - allows one value to survive
  Napi::EscapableHandleScope scope(env);

  Napi::Object result = Napi::Object::New(env);
  result.Set("value", Napi::Number::New(env, value));

  // Escape promotes handle to parent scope
  return scope.Escape(result).As<Napi::Object>();
}

Napi::Value GetResult(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  Napi::Object obj = CreateResult(env, 42);  // Valid handle
  obj.Set("extra", Napi::Boolean::New(env, true));  // Safe

  return obj;
}
```

**Escape only once:**

```cpp
Napi::Value CreateMultiple(Napi::Env env) {
  Napi::EscapableHandleScope scope(env);

  Napi::Object a = Napi::Object::New(env);
  Napi::Object b = Napi::Object::New(env);

  // BUG: Can only escape ONE value per scope
  // scope.Escape(a);
  // scope.Escape(b);  // ERROR: already escaped

  // CORRECT: Put both in a container and escape that
  Napi::Array container = Napi::Array::New(env, 2);
  container[uint32_t(0)] = a;
  container[uint32_t(1)] = b;

  return scope.Escape(container);
}
```

**Factory function pattern:**

```cpp
class WidgetFactory {
 public:
  static Napi::Object Create(Napi::Env env, const Config& config) {
    Napi::EscapableHandleScope scope(env);

    Napi::Object widget = Napi::Object::New(env);

    // Set up widget...
    widget.Set("name", Napi::String::New(env, config.name));
    widget.Set("size", CreateSize(env, config.width, config.height));

    // Note: CreateSize should also use EscapableHandleScope

    return scope.Escape(widget).As<Napi::Object>();
  }

 private:
  static Napi::Object CreateSize(Napi::Env env, int w, int h) {
    Napi::EscapableHandleScope scope(env);

    Napi::Object size = Napi::Object::New(env);
    size.Set("width", Napi::Number::New(env, w));
    size.Set("height", Napi::Number::New(env, h));

    return scope.Escape(size).As<Napi::Object>();
  }
};
```

Reference: [node-addon-api HandleScope](https://github.com/nodejs/node-addon-api/blob/main/doc/handle_scope.md)

### 5.4 Use HandleScope in All Native Functions

**Impact: HIGH (prevents handle table overflow and crashes)**

Every V8 value created in C++ needs a handle. Without HandleScope, handles accumulate and overflow V8's handle table.

**Incorrect (no scope management):**

```cpp
void ProcessManyItems(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();

  for (uint32_t i = 0; i < items.Length(); i++) {
    // Each iteration creates handles that never get released
    Napi::Value item = items[i];
    Napi::Object obj = item.As<Napi::Object>();
    Napi::Value name = obj.Get("name");
    Napi::Value value = obj.Get("value");
    // ... process

    // After millions of iterations: CRASH - handle table full
  }
}
```

**Correct (scoped handles):**

```cpp
void ProcessManyItems(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();

  for (uint32_t i = 0; i < items.Length(); i++) {
    // Create scope for loop iteration - handles released each iteration
    Napi::HandleScope scope(env);

    Napi::Value item = items[i];
    Napi::Object obj = item.As<Napi::Object>();
    Napi::Value name = obj.Get("name");
    Napi::Value value = obj.Get("value");
    // ... process

    // Handles released when scope exits
  }
}
```

**Note:** node-addon-api functions like those defined via `Napi::Function::New` or `DefineClass` automatically create a HandleScope. The issue arises in helper functions or loops.

**Helper function pattern:**

```cpp
// Helper that creates many temporaries
std::string ExtractName(Napi::Env env, Napi::Object obj) {
  // HandleScope for helper function
  Napi::HandleScope scope(env);

  Napi::Value nameVal = obj.Get("name");
  if (!nameVal.IsString()) {
    return "";
  }

  // Convert to C++ string before scope exits
  return nameVal.As<Napi::String>().Utf8Value();
}

void ProcessAll(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();

  for (uint32_t i = 0; i < items.Length(); i++) {
    Napi::HandleScope scope(env);
    Napi::Object obj = items[i].As<Napi::Object>();

    // Helper has its own scope
    std::string name = ExtractName(env, obj);
    ProcessName(name);
  }
}
```

**EscapableHandleScope for returning values:**

```cpp
Napi::Value CreateInHelper(Napi::Env env) {
  // Use EscapableHandleScope when returning a handle
  Napi::EscapableHandleScope scope(env);

  Napi::Object result = Napi::Object::New(env);
  result.Set("created", Napi::Boolean::New(env, true));

  // Escape the value so it survives scope exit
  return scope.Escape(result);
}
```

Reference: [V8 Embedder Guide - Handles](https://v8.dev/docs/embed#handles-and-garbage-collection)

### 5.5 Use Persistent References for Long-Lived Values

**Impact: HIGH (prevents premature GC of stored values)**

Local handles are only valid within the current scope. Use `Napi::Reference` (persistent handles) for values that must survive across multiple function calls.

**Incorrect (local handle stored):**

```cpp
class EventEmitter {
 public:
  void SetCallback(const Napi::CallbackInfo& info) {
    // BUG: Local handle stored as member
    callback_ = info[0].As<Napi::Function>();
    // After this function returns, callback_ is INVALID
  }

  void Emit(const Napi::CallbackInfo& info) {
    // CRASH: callback_ is a dangling handle
    callback_.Call({});
  }

 private:
  Napi::Function callback_;  // Local handle - invalid after function returns!
};
```

**Correct (persistent reference):**

```cpp
class EventEmitter {
 public:
  void SetCallback(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Function fn = info[0].As<Napi::Function>();

    // Create persistent reference with ref count 1
    callback_ = Napi::Persistent(fn);
    callback_.SuppressDestruct();  // Manual control of destructor
  }

  void Emit(const Napi::CallbackInfo& info) {
    if (!callback_.IsEmpty()) {
      Napi::Function fn = callback_.Value();
      fn.Call({});
    }
  }

  void ClearCallback(const Napi::CallbackInfo& info) {
    callback_.Reset();  // Release reference
  }

 private:
  Napi::Reference<Napi::Function> callback_;  // Persistent - survives scopes
};
```

**Reference counting:**

```cpp
class SharedResource {
 public:
  void AddUser(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Object user = info[0].As<Napi::Object>();

    // Create reference with initial ref count 1
    auto ref = Napi::Reference<Napi::Object>::New(user, 1);
    users_.push_back(std::move(ref));
  }

  void IncrementRef(size_t index) {
    if (index < users_.size()) {
      users_[index].Ref();  // Increment ref count
    }
  }

  void DecrementRef(size_t index) {
    if (index < users_.size()) {
      uint32_t count = users_[index].Unref();  // Decrement ref count
      if (count == 0) {
        // Reference is now weak - may be GC'd
      }
    }
  }

 private:
  std::vector<Napi::Reference<Napi::Object>> users_;
};
```

**Weak reference pattern:**

```cpp
class Cache {
 public:
  void Store(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string key = info[0].As<Napi::String>().Utf8Value();
    Napi::Object value = info[1].As<Napi::Object>();

    // Weak reference (ref count 0) - doesn't prevent GC
    auto ref = Napi::Reference<Napi::Object>::New(value, 0);
    cache_[key] = std::move(ref);
  }

  Napi::Value Get(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string key = info[0].As<Napi::String>().Utf8Value();

    auto it = cache_.find(key);
    if (it != cache_.end() && !it->second.IsEmpty()) {
      return it->second.Value();
    }

    return env.Undefined();
  }

 private:
  std::unordered_map<std::string, Napi::Reference<Napi::Object>> cache_;
};
```

Reference: [node-addon-api Reference](https://github.com/nodejs/node-addon-api/blob/main/doc/reference.md)

---

## 6. Object Wrapping

**Impact: MEDIUM-HIGH**

Wrapping C++ objects for JS access requires correct prevent GC handling, weak references, and destructor patterns.

### 6.1 Implement Proper Destructor Cleanup

**Impact: MEDIUM-HIGH (prevents resource leaks when objects are garbage collected)**

ObjectWrap instances are destroyed when their JS wrapper is garbage collected. Implement proper cleanup in the destructor.

**Incorrect (resources leak):**

```cpp
class FileHandle : public Napi::ObjectWrap<FileHandle> {
 public:
  FileHandle(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<FileHandle>(info) {
    fd_ = open(path, O_RDONLY);
  }
  // No destructor - file descriptor leaks!

 private:
  int fd_;
};
```

**Correct (cleanup in destructor):**

```cpp
class FileHandle : public Napi::ObjectWrap<FileHandle> {
 public:
  FileHandle(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<FileHandle>(info) {
    fd_ = open(path, O_RDONLY);
  }

  ~FileHandle() {
    if (fd_ >= 0) {
      close(fd_);
      fd_ = -1;
    }
  }

  void Close(const Napi::CallbackInfo& info) {
    if (fd_ >= 0) {
      close(fd_);
      fd_ = -1;
    }
  }

 private:
  int fd_ = -1;
};
```

Reference: [ObjectWrap Documentation](https://github.com/nodejs/node-addon-api/blob/main/doc/object_wrap.md)

### 6.2 Prevent GC During Native Operations

**Impact: MEDIUM-HIGH (prevents crashes from premature garbage collection)**

When passing JS objects to async operations, prevent GC from collecting them while native code holds pointers.

**Incorrect (object may be GC'd):**

```cpp
class AsyncProcessor : public Napi::AsyncWorker {
 public:
  AsyncProcessor(Napi::Function& cb, Napi::Buffer<uint8_t> buf)
      : Napi::AsyncWorker(cb), data_(buf.Data()), length_(buf.Length()) {}

  void Execute() override {
    ProcessData(data_, length_);  // CRASH: buffer may be GC'd!
  }

 private:
  uint8_t* data_;
  size_t length_;
};
```

**Correct (prevent GC with reference):**

```cpp
class AsyncProcessor : public Napi::AsyncWorker {
 public:
  AsyncProcessor(Napi::Function& cb, Napi::Buffer<uint8_t> buf)
      : Napi::AsyncWorker(cb),
        buffer_ref_(Napi::Persistent(buf)),
        data_(buf.Data()),
        length_(buf.Length()) {}

  void Execute() override {
    ProcessData(data_, length_);  // Safe: buffer_ref_ prevents GC
  }

 private:
  Napi::Reference<Napi::Buffer<uint8_t>> buffer_ref_;
  uint8_t* data_;
  size_t length_;
};
```

Reference: [N-API prevent prevent gc](https://nodejs.org/api/n-api.html#prevent-prevent-gc)

### 6.3 Use Weak Pointers for Observer Patterns

**Impact: MEDIUM-HIGH (enables proper cleanup in observer patterns)**

When C++ objects observe JS objects, use weak references to allow JS objects to be garbage collected.

**Incorrect (strong reference prevents GC):**

```cpp
class NativeObserver {
 public:
  void Watch(const Napi::CallbackInfo& info) {
    // Strong reference - target can never be GC'd!
    target_ = Napi::Persistent(info[0].As<Napi::Object>());
  }

 private:
  Napi::Reference<Napi::Object> target_;
};
```

**Correct (weak reference allows GC):**

```cpp
class NativeObserver {
 public:
  void Watch(const Napi::CallbackInfo& info) {
    Napi::Object target = info[0].As<Napi::Object>();
    // Weak reference (ref count = 0)
    target_ = Napi::Reference<Napi::Object>::New(target, 0);
  }

  bool IsTargetAlive() {
    return !target_.IsEmpty();
  }

 private:
  Napi::Reference<Napi::Object> target_;
};
```

Reference: [Weak References in V8](https://v8.dev/features/weak-references)

---

## 7. N-API Best Practices

**Impact: MEDIUM**

N-API provides ABI stability across Node versions. Using it correctly avoids version-specific bugs and simplifies maintenance.

### 7.1 Handle Errors with Exceptions

**Impact: MEDIUM (proper error propagation to JavaScript)**

Use Napi::Error and its subclasses to throw JavaScript exceptions. Check for pending exceptions after calling JS functions.

**Incorrect (silent failures):**

```cpp
Napi::Value Divide(const Napi::CallbackInfo& info) {
  double a = info[0].As<Napi::Number>().DoubleValue();
  double b = info[1].As<Napi::Number>().DoubleValue();

  if (b == 0) {
    return info.Env().Undefined();  // Silent failure!
  }

  return Napi::Number::New(info.Env(), a / b);
}
```

**Correct (proper exceptions):**

```cpp
Napi::Value Divide(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  double a = info[0].As<Napi::Number>().DoubleValue();
  double b = info[1].As<Napi::Number>().DoubleValue();

  if (b == 0) {
    Napi::RangeError::New(env, "Division by zero")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }

  return Napi::Number::New(env, a / b);
}
```

Reference: [N-API Error Handling](https://nodejs.org/api/n-api.html#error-handling)

### 7.2 Register Cleanup Hooks for Module Unload

**Impact: MEDIUM (prevents resource leaks on module unload)**

Register cleanup hooks to release resources when the addon is unloaded or Node.js exits.

**Incorrect (no cleanup):**

```cpp
static Database* global_db = nullptr;

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  global_db = new Database();
  // Memory leak on module unload!
  return exports;
}
```

**Correct (cleanup hook):**

```cpp
static Database* global_db = nullptr;

void Cleanup(void* arg) {
  delete global_db;
  global_db = nullptr;
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  global_db = new Database();

  napi_add_env_cleanup_hook(env, Cleanup, nullptr);

  return exports;
}
```

Reference: [Environment Cleanup Hooks](https://nodejs.org/api/n-api.html#cleanup-on-exit-of-the-current-nodejs-environment)

### 7.3 Target Appropriate N-API Version

**Impact: MEDIUM (ensures compatibility across Node.js versions)**

Set NAPI_VERSION to the lowest version that provides features you need. This maximizes compatibility across Node.js versions.

**Incorrect (implicit latest):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"]
  }]
}
```

**Correct (explicit version):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"],
    "defines": ["NAPI_VERSION=8"]
  }]
}
```

**N-API version features:**
- v8: Node 12.22+, ThreadSafeFunction improvements
- v6: Node 10.20+, BigInt support
- v4: Node 10.16+, AsyncWorker improvements
- v3: Node 8.11+, basic async support

Reference: [N-API Version Matrix](https://nodejs.org/api/n-api.html#node-api-version-matrix)

### 7.4 Use DefineClass for Object-Oriented APIs

**Impact: MEDIUM (cleaner API with proper prototype chain)**

Use `Napi::ObjectWrap` with `DefineClass` to create proper JavaScript classes with methods and properties.

**Incorrect (manual object setup):**

```cpp
Napi::Value CreateCounter(const Napi::CallbackInfo& info) {
  Napi::Object obj = Napi::Object::New(info.Env());
  // Manually adding methods - no prototype, no instanceof
  obj.Set("increment", Napi::Function::New(info.Env(), Increment));
  return obj;
}
```

**Correct (DefineClass):**

```cpp
class Counter : public Napi::ObjectWrap<Counter> {
 public:
  static Napi::Object Init(Napi::Env env, Napi::Object exports) {
    Napi::Function func = DefineClass(env, "Counter", {
      InstanceMethod("increment", &Counter::Increment),
      InstanceAccessor("value", &Counter::GetValue, nullptr),
    });

    exports.Set("Counter", func);
    return exports;
  }

  Counter(const Napi::CallbackInfo& info)
      : Napi::ObjectWrap<Counter>(info), value_(0) {}

 private:
  Napi::Value Increment(const Napi::CallbackInfo& info) {
    return Napi::Number::New(info.Env(), ++value_);
  }

  Napi::Value GetValue(const Napi::CallbackInfo& info) {
    return Napi::Number::New(info.Env(), value_);
  }

  int value_;
};
```

Reference: [ObjectWrap](https://github.com/nodejs/node-addon-api/blob/main/doc/object_wrap.md)

### 7.5 Use node-addon-api Over Raw N-API

**Impact: MEDIUM (reduces boilerplate and prevents common errors)**

node-addon-api provides C++ wrappers with automatic error handling and RAII patterns. Use it instead of raw N-API C functions.

**Incorrect (raw N-API):**

```cpp
napi_value ProcessData(napi_env env, napi_callback_info info) {
  napi_status status;
  size_t argc = 1;
  napi_value argv[1];

  status = napi_get_cb_info(env, info, &argc, argv, nullptr, nullptr);
  if (status != napi_ok) return nullptr;

  napi_valuetype type;
  status = napi_typeof(env, argv[0], &type);
  if (status != napi_ok) return nullptr;

  // Manual error handling throughout...
}
```

**Correct (node-addon-api):**

```cpp
#include <napi.h>

Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  if (!info[0].IsNumber()) {
    Napi::TypeError::New(env, "Expected number")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }

  // Clean, safe, automatic error propagation
  return Napi::Number::New(env, info[0].As<Napi::Number>().DoubleValue() * 2);
}
```

Reference: [node-addon-api](https://github.com/nodejs/node-addon-api)

---

## 8. Build & Module Loading

**Impact: MEDIUM**

Optimizing build configuration and module loading reduces binary size, startup time, and cross-platform issues.

### 8.1 Distribute Prebuilt Binaries

**Impact: MEDIUM (eliminates build time for users)**

Use prebuild/prebuildify to distribute precompiled binaries instead of requiring users to compile.

**Incorrect (compile on install):**

```json
{
  "scripts": {
    "install": "node-gyp rebuild"
  }
}
```

**Correct (prebuilt binaries):**

```json
{
  "scripts": {
    "install": "prebuild-install || node-gyp rebuild",
    "prebuild": "prebuildify --napi --strip"
  },
  "devDependencies": {
    "prebuildify": "^5.0.0"
  },
  "dependencies": {
    "prebuild-install": "^7.0.0"
  }
}
```

Reference: [prebuildify](https://github.com/prebuild/prebuildify)

### 8.2 Minimize Binary Size

**Impact: MEDIUM (faster npm install and reduced memory footprint)**

Strip symbols and disable unnecessary features to reduce binary size.

**Incorrect (bloated binary):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"]
  }]
}
```

**Correct (minimal binary):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"],
    "cflags_cc": ["-fno-rtti", "-fvisibility=hidden"],
    "ldflags": ["-s"],
    "xcode_settings": {
      "GCC_SYMBOLS_PRIVATE_EXTERN": "YES",
      "DEAD_CODE_STRIPPING": "YES"
    }
  }]
}
```

Reference: [Reducing Binary Size](https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html)

### 8.3 Use Context-Aware Addons

**Impact: MEDIUM (enables worker threads and multiple contexts)**

Build context-aware addons to support Worker threads and multiple V8 contexts.

**Incorrect (not context-aware):**

```cpp
// Global state - breaks with workers
static int global_counter = 0;

NODE_MODULE(addon, Init)
```

**Correct (context-aware):**

```cpp
// Per-context state
class AddonData {
 public:
  int counter = 0;
};

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  // Store per-context data
  AddonData* data = new AddonData();
  env.SetInstanceData(data);

  exports.Set("increment", Napi::Function::New(env, [](const Napi::CallbackInfo& info) {
    AddonData* data = info.Env().GetInstanceData<AddonData>();
    return Napi::Number::New(info.Env(), ++data->counter);
  }));

  return exports;
}

NODE_API_MODULE(addon, Init)
```

Reference: [Context-Aware Addons](https://nodejs.org/api/addons.html#context-aware-addons)

### 8.4 Use Lazy Initialization for Heavy Resources

**Impact: MEDIUM (faster module load time)**

Defer expensive initialization until first use instead of module load time.

**Incorrect (eager initialization):**

```cpp
static HeavyResource* resource = nullptr;

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  // Blocks require() for seconds!
  resource = new HeavyResource();
  resource->LoadData();

  return exports;
}
```

**Correct (lazy initialization):**

```cpp
static std::once_flag init_flag;
static HeavyResource* resource = nullptr;

HeavyResource* GetResource() {
  std::call_once(init_flag, []() {
    resource = new HeavyResource();
    resource->LoadData();
  });
  return resource;
}

Napi::Value UseResource(const Napi::CallbackInfo& info) {
  // Initialize on first use
  HeavyResource* res = GetResource();
  return res->Process(info);
}
```

Reference: [std::call_once](https://en.cppreference.com/w/cpp/thread/call_once)

### 8.5 Use Optimal Compiler Flags

**Impact: MEDIUM (10-50% performance improvement)**

Configure gyp to use appropriate optimization flags for release builds.

**Incorrect (debug flags in production):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"]
  }]
}
```

**Correct (optimized release build):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"],
    "cflags_cc": ["-O3", "-fno-exceptions"],
    "xcode_settings": {
      "GCC_OPTIMIZATION_LEVEL": "3",
      "CLANG_CXX_LIBRARY": "libc++"
    },
    "msvs_settings": {
      "VCCLCompilerTool": {
        "Optimization": 2
      }
    }
  }]
}
```

Reference: [node-gyp](https://github.com/nodejs/node-gyp)

---

## References

1. [https://nodejs.org/api/n-api.html](https://nodejs.org/api/n-api.html)
2. [https://github.com/nodejs/node-addon-api](https://github.com/nodejs/node-addon-api)
3. [https://v8.dev/docs/embed](https://v8.dev/docs/embed)
4. [https://nodejs.org/api/addons.html](https://nodejs.org/api/addons.html)
5. [https://docs.libuv.org/en/v1.x/threadpool.html](https://docs.libuv.org/en/v1.x/threadpool.html)
6. [https://v8.dev/blog/pointer-compression](https://v8.dev/blog/pointer-compression)
