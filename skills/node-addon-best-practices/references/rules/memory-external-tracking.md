---
title: Track External Memory Allocations
impact: CRITICAL
impactDescription: Enables GC to run at correct time - untracked 500MB native allocation causes OOM while V8 thinks heap is empty
tags: memory, external-memory, gc, allocation, node-addon-api
---

# Track External Memory Allocations

Call `AdjustExternalMemory` to inform V8's garbage collector about large native memory allocations. Without tracking, the GC doesn't know memory pressure exists and may not run when needed. A 500MB native buffer with 10MB JS heap will cause OOM without triggering GC.

## Why This Matters

- **GC Awareness**: V8 needs to know about native memory usage
- **Timely Collection**: GC runs when memory pressure is high
- **OOM Prevention**: Prevents out-of-memory from invisible allocations
- **Resource Management**: Better memory utilization across JS and native

## Understanding External Memory

V8 tracks its own heap but is blind to native allocations. If you allocate 500MB in C++ but V8 only sees 10MB, it won't trigger garbage collection even as total process memory approaches limits.

```
V8's view without tracking:    V8's view with tracking:
JS Heap: 10MB                  JS Heap: 10MB
Native: (invisible)            External: 500MB (tracked)
                               Total: 510MB -> trigger GC!
```

## Incorrect: Large Allocation Without Tracking

```cpp
// PROBLEM: V8 sees 10KB heap but process uses 10GB
// GC never runs because V8 thinks memory is fine - eventual OOM
class LargeBuffer : public Napi::ObjectWrap<LargeBuffer> {
public:
    LargeBuffer(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<LargeBuffer>(info) {

        size_t size = info[0].As<Napi::Number>().Uint32Value();

        // Allocating 100MB+ but V8 doesn't know!
        data_ = new uint8_t[size];
        size_ = size;

        // V8 thinks memory usage is low
        // GC won't run even as process approaches OOM
    }

    ~LargeBuffer() {
        delete[] data_;
        // V8 still doesn't know memory was freed
    }

private:
    uint8_t* data_;
    size_t size_;
};
```

**Problem scenario:**
```javascript
// Each buffer is 100MB, but V8 only sees wrapper objects (~100 bytes each)
const buffers = [];
for (let i = 0; i < 100; i++) {
    buffers.push(new addon.LargeBuffer(100 * 1024 * 1024));
    // Process uses 10GB but V8 thinks heap is ~10KB
    // No GC runs, eventual OOM crash!
}
```

## Correct: Track External Memory

```cpp
// SOLUTION: AdjustExternalMemory tells V8 about native allocations
// GC now triggers when total (JS + external) exceeds threshold
class LargeBuffer : public Napi::ObjectWrap<LargeBuffer> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "LargeBuffer", {
            InstanceMethod("size", &LargeBuffer::Size),
            InstanceMethod("free", &LargeBuffer::Free)
        });
        exports.Set("LargeBuffer", func);
        return exports;
    }

    LargeBuffer(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<LargeBuffer>(info), data_(nullptr), size_(0) {

        Napi::Env env = info.Env();
        size_t size = info[0].As<Napi::Number>().Uint32Value();

        // Allocate native memory
        data_ = new uint8_t[size];
        size_ = size;

        // CRITICAL: Tell V8 about this allocation
        Napi::MemoryManagement::AdjustExternalMemory(env, size_);

        // Now V8 knows total memory pressure
        // GC will run when needed
    }

    ~LargeBuffer() {
        // Note: Can't adjust memory in destructor - no env available
        // Use Release() pattern instead or ensure Free() is called
        if (data_) {
            delete[] data_;
            data_ = nullptr;
        }
    }

    void Free(const Napi::CallbackInfo& info) {
        if (data_) {
            delete[] data_;
            data_ = nullptr;

            // Tell V8 memory was released
            Napi::MemoryManagement::AdjustExternalMemory(info.Env(), -(int64_t)size_);
            size_ = 0;
        }
    }

    Napi::Value Size(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), size_);
    }

private:
    uint8_t* data_;
    size_t size_;
};
```

## Correct: Using Raw N-API

```cpp
// GOOD: Raw N-API external memory tracking
typedef struct {
    uint8_t* data;
    size_t size;
} NativeBuffer;

static void BufferFinalize(napi_env env, void* finalize_data, void* finalize_hint) {
    NativeBuffer* buf = (NativeBuffer*)finalize_data;

    if (buf->data) {
        // Notify V8 memory is being freed
        int64_t change = 0;
        napi_adjust_external_memory(env, -(int64_t)buf->size, &change);

        free(buf->data);
    }
    free(buf);
}

static napi_value CreateBuffer(napi_env env, napi_callback_info info) {
    size_t argc = 1;
    napi_value argv[1];
    napi_get_cb_info(env, info, &argc, argv, NULL, NULL);

    uint32_t size;
    napi_get_value_uint32(env, argv[0], &size);

    // Allocate native buffer
    NativeBuffer* buf = (NativeBuffer*)malloc(sizeof(NativeBuffer));
    buf->data = (uint8_t*)malloc(size);
    buf->size = size;

    if (!buf->data) {
        free(buf);
        napi_throw_error(env, NULL, "Failed to allocate buffer");
        return NULL;
    }

    // CRITICAL: Track the allocation
    int64_t adjusted_value;
    napi_status status = napi_adjust_external_memory(env, size, &adjusted_value);
    if (status != napi_ok) {
        free(buf->data);
        free(buf);
        napi_throw_error(env, NULL, "Failed to adjust external memory");
        return NULL;
    }

    // Create wrapper with destructor
    napi_value wrapper;
    napi_create_external(env, buf, BufferFinalize, NULL, &wrapper);

    return wrapper;
}
```

## Pattern: Image Processing with Memory Tracking

```cpp
// GOOD: Real-world example with large image data
class ImageProcessor : public Napi::ObjectWrap<ImageProcessor> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports);

    ImageProcessor(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<ImageProcessor>(info) {}

    Napi::Value LoadImage(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        std::string path = info[0].As<Napi::String>().Utf8Value();

        // Load image - might be 50MB+ for high-res images
        ImageData img = LoadFromFile(path);

        if (imageData_) {
            // Release previous image memory tracking
            Napi::MemoryManagement::AdjustExternalMemory(env, -(int64_t)imageSize_);
            delete[] imageData_;
        }

        imageData_ = img.data;
        imageSize_ = img.width * img.height * img.channels;

        // Track new allocation
        Napi::MemoryManagement::AdjustExternalMemory(env, imageSize_);

        return Napi::Boolean::New(env, true);
    }

    Napi::Value Process(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        // Allocate output buffer (same size as input)
        size_t outputSize = imageSize_;
        uint8_t* output = new uint8_t[outputSize];

        // Track temporary allocation
        Napi::MemoryManagement::AdjustExternalMemory(env, outputSize);

        // Process image...
        ProcessImage(imageData_, output, imageSize_);

        // Replace input with output
        delete[] imageData_;
        Napi::MemoryManagement::AdjustExternalMemory(env, -(int64_t)imageSize_);

        imageData_ = output;
        // Net change is zero since we freed and allocated same size

        return Napi::Boolean::New(env, true);
    }

    void Release(const Napi::CallbackInfo& info) {
        if (imageData_) {
            Napi::MemoryManagement::AdjustExternalMemory(info.Env(), -(int64_t)imageSize_);
            delete[] imageData_;
            imageData_ = nullptr;
            imageSize_ = 0;
        }
    }

private:
    uint8_t* imageData_ = nullptr;
    size_t imageSize_ = 0;
};
```

## Pattern: Memory Pool with Tracking

```cpp
// GOOD: Memory pool that tracks total external memory
class MemoryPool {
public:
    MemoryPool(Napi::Env env, size_t poolSize)
        : env_(env), poolSize_(poolSize), allocated_(0) {

        pool_ = new uint8_t[poolSize];

        // Track entire pool
        Napi::MemoryManagement::AdjustExternalMemory(env_, poolSize_);
    }

    ~MemoryPool() {
        // Note: Need env to adjust - store it or use Release method
        delete[] pool_;
    }

    void Release() {
        if (pool_) {
            Napi::MemoryManagement::AdjustExternalMemory(env_, -(int64_t)poolSize_);
            delete[] pool_;
            pool_ = nullptr;
        }
    }

    void* Allocate(size_t size) {
        if (allocated_ + size > poolSize_) {
            return nullptr;
        }

        void* ptr = pool_ + allocated_;
        allocated_ += size;
        return ptr;
    }

    void Reset() {
        allocated_ = 0;
    }

private:
    Napi::Env env_;
    uint8_t* pool_;
    size_t poolSize_;
    size_t allocated_;
};
```

**When to use:** Track any native allocation > 1MB that persists beyond a single callback. Image buffers, audio samples, cached data, and file contents all need tracking.

**When NOT to use:** Small allocations (< 1KB), stack allocations, or temporary heap allocations freed within the same callback. The overhead of tracking (~1 microsecond) isn't worth it for small allocations.

## When to Track External Memory

```cpp
// Track allocations that are:
// 1. Large (> 1MB recommended threshold)
// 2. Long-lived (persist across multiple callbacks)
// 3. Numerous (many small allocations adding up)

// Examples of what to track:
// - Image/video buffers
// - Audio samples
// - Large data structures
// - File contents
// - Network buffers
// - Cached data

// Don't bother tracking:
// - Small temporary allocations (< 1KB)
// - Stack allocations
// - Short-lived heap allocations freed in same callback
```

## Monitoring External Memory

```javascript
// JavaScript side - monitor external memory
const v8 = require('v8');

function checkMemory() {
    const stats = v8.getHeapStatistics();
    console.log('Heap used:', stats.used_heap_size);
    console.log('External:', stats.external_memory);  // Your tracked memory
    console.log('Total:', stats.used_heap_size + stats.external_memory);
}

// Check before/after operations
checkMemory();
addon.loadLargeFile('huge.dat');
checkMemory();  // Should show increased external_memory
```

## References

- [N-API Adjust External Memory](https://nodejs.org/api/n-api.html#napi_adjust_external_memory)
- [V8 Memory Management](https://v8.dev/blog/trash-talk)
- [Heap Statistics](https://nodejs.org/api/v8.html#v8getheapstatistics)
