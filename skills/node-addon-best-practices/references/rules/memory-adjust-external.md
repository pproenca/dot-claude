---
title: Track External Memory with AdjustExternalMemory
impact: CRITICAL
impactDescription: Enables accurate GC triggering, prevents hidden memory bloat
tags: memory, external, gc, tracking
---

# Track External Memory with AdjustExternalMemory

When native addons allocate memory outside V8's heap (malloc, new, mmap, etc.), the V8 garbage collector doesn't know about it. Use `AdjustExternalMemory` to inform V8 about external allocations so it can schedule garbage collection appropriately.

## Why This Matters

- **GC Triggering**: V8 only sees its own heap; large external allocations go unnoticed
- **Memory Pressure**: Without tracking, GC runs infrequently despite high total memory
- **OOM Prevention**: Proper tracking triggers GC before memory exhaustion
- **Memory Accounting**: Accurate memory usage reporting to monitoring tools

## How It Works

```
Without AdjustExternalMemory:
┌────────────────────────────────────────────────┐
│ V8 Heap: 50MB                                  │
│ (V8 sees only this)                            │
├────────────────────────────────────────────────┤
│ External Memory: 2GB                           │
│ (Native buffers, malloc'd data)                │
│ ← V8 DOESN'T KNOW ABOUT THIS!                  │
└────────────────────────────────────────────────┘
GC thinks: "50MB used, no rush to collect"
Reality: 2.05GB used, approaching OOM

With AdjustExternalMemory:
┌────────────────────────────────────────────────┐
│ V8 Heap: 50MB                                  │
├────────────────────────────────────────────────┤
│ External Memory (tracked): 2GB                 │
│ ← V8 knows and adjusts GC thresholds           │
└────────────────────────────────────────────────┘
GC thinks: "2.05GB tracked, schedule collection!"
```

## Incorrect: Untracked External Allocations

```cpp
// BAD: Large allocations without memory tracking
#define NAPI_VERSION 8
#include <napi.h>
#include <cstdlib>

class ImageProcessor : public Napi::ObjectWrap<ImageProcessor> {
public:
    ImageProcessor(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<ImageProcessor>(info), data_(nullptr), size_(0) {}

    ~ImageProcessor() {
        if (data_) {
            free(data_);
            // Memory freed but V8 never knew it existed
        }
    }

    Napi::Value LoadImage(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        size_t width = info[0].As<Napi::Number>().Uint32Value();
        size_t height = info[1].As<Napi::Number>().Uint32Value();
        size_ = width * height * 4;  // RGBA

        // BAD: Allocating potentially gigabytes without telling V8
        data_ = static_cast<uint8_t*>(malloc(size_));
        if (!data_) {
            Napi::Error::New(env, "Allocation failed").ThrowAsJavaScriptException();
            return env.Undefined();
        }

        // V8 has no idea we just allocated this memory!
        // GC won't run even if total process memory is critical

        return env.Undefined();
    }

private:
    uint8_t* data_;
    size_t size_;
};
```

## Correct: Tracked External Memory

```cpp
// GOOD: Track external allocations with AdjustExternalMemory
#define NAPI_VERSION 8
#include <napi.h>
#include <cstdlib>

class ImageProcessor : public Napi::ObjectWrap<ImageProcessor> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "ImageProcessor", {
            InstanceMethod("loadImage", &ImageProcessor::LoadImage),
            InstanceMethod("unloadImage", &ImageProcessor::UnloadImage),
            InstanceMethod("getMemoryUsage", &ImageProcessor::GetMemoryUsage)
        });

        exports.Set("ImageProcessor", func);
        return exports;
    }

    ImageProcessor(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<ImageProcessor>(info),
          env_(info.Env()),
          data_(nullptr),
          size_(0) {}

    ~ImageProcessor() {
        FreeMemory();
    }

private:
    void FreeMemory() {
        if (data_) {
            free(data_);
            data_ = nullptr;

            // Tell V8 we freed the memory
            if (size_ > 0) {
                Napi::MemoryManagement::AdjustExternalMemory(env_, -static_cast<int64_t>(size_));
                size_ = 0;
            }
        }
    }

    Napi::Value LoadImage(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        // Free any existing data first
        FreeMemory();

        size_t width = info[0].As<Napi::Number>().Uint32Value();
        size_t height = info[1].As<Napi::Number>().Uint32Value();
        size_ = width * height * 4;  // RGBA

        data_ = static_cast<uint8_t*>(malloc(size_));
        if (!data_) {
            size_ = 0;
            Napi::Error::New(env, "Allocation failed").ThrowAsJavaScriptException();
            return env.Undefined();
        }

        // GOOD: Tell V8 about the external allocation
        int64_t adjusted = Napi::MemoryManagement::AdjustExternalMemory(env, size_);

        // adjusted contains new total external memory
        // V8 will now factor this into GC decisions

        return Napi::Number::New(env, size_);
    }

    Napi::Value UnloadImage(const Napi::CallbackInfo& info) {
        FreeMemory();
        return info.Env().Undefined();
    }

    Napi::Value GetMemoryUsage(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), size_);
    }

    Napi::Env env_;
    uint8_t* data_;
    size_t size_;
};
```

## Correct: Raw N-API Memory Tracking

```cpp
// GOOD: Raw N-API version
#include <node_api.h>
#include <stdlib.h>

typedef struct {
    napi_env env;
    void* data;
    size_t size;
} BufferData;

napi_value AllocateBuffer(napi_env env, napi_callback_info info) {
    size_t argc = 1;
    napi_value argv[1];
    napi_get_cb_info(env, info, &argc, argv, NULL, NULL);

    int64_t size;
    napi_get_value_int64(env, argv[0], &size);

    if (size <= 0) {
        napi_throw_range_error(env, NULL, "Size must be positive");
        return NULL;
    }

    void* data = malloc(size);
    if (!data) {
        napi_throw_error(env, NULL, "Allocation failed");
        return NULL;
    }

    // Track the external allocation
    int64_t adjusted_value;
    napi_status status = napi_adjust_external_memory(env, size, &adjusted_value);
    if (status != napi_ok) {
        free(data);
        napi_throw_error(env, NULL, "Failed to adjust external memory");
        return NULL;
    }

    // Store size for later deallocation tracking
    BufferData* buffer_data = malloc(sizeof(BufferData));
    buffer_data->env = env;
    buffer_data->data = data;
    buffer_data->size = size;

    // Create external with destructor
    napi_value result;
    napi_create_external(env, buffer_data, FinalizeBuffer, NULL, &result);

    return result;
}

void FinalizeBuffer(napi_env env, void* finalize_data, void* finalize_hint) {
    BufferData* buffer_data = (BufferData*)finalize_data;

    if (buffer_data->data) {
        free(buffer_data->data);

        // Reduce tracked external memory
        int64_t adjusted_value;
        napi_adjust_external_memory(env, -(int64_t)buffer_data->size, &adjusted_value);
    }

    free(buffer_data);
}
```

## Correct: RAII Wrapper for Automatic Tracking

```cpp
// GOOD: RAII class for automatic memory tracking
#define NAPI_VERSION 8
#include <napi.h>

template<typename T>
class TrackedAllocation {
public:
    TrackedAllocation(Napi::Env env, size_t count)
        : env_(env), data_(nullptr), size_(0) {

        size_ = count * sizeof(T);
        data_ = static_cast<T*>(malloc(size_));

        if (data_) {
            Napi::MemoryManagement::AdjustExternalMemory(env_, size_);
        }
    }

    ~TrackedAllocation() {
        if (data_) {
            free(data_);
            Napi::MemoryManagement::AdjustExternalMemory(env_, -static_cast<int64_t>(size_));
        }
    }

    // Move semantics
    TrackedAllocation(TrackedAllocation&& other) noexcept
        : env_(other.env_), data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    TrackedAllocation& operator=(TrackedAllocation&& other) noexcept {
        if (this != &other) {
            if (data_) {
                free(data_);
                Napi::MemoryManagement::AdjustExternalMemory(env_, -static_cast<int64_t>(size_));
            }

            env_ = other.env_;
            data_ = other.data_;
            size_ = other.size_;

            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    // Prevent copying
    TrackedAllocation(const TrackedAllocation&) = delete;
    TrackedAllocation& operator=(const TrackedAllocation&) = delete;

    T* get() { return data_; }
    const T* get() const { return data_; }
    size_t size() const { return size_; }
    bool valid() const { return data_ != nullptr; }

    T& operator[](size_t index) { return data_[index]; }
    const T& operator[](size_t index) const { return data_[index]; }

private:
    Napi::Env env_;
    T* data_;
    size_t size_;
};

// Usage
class DataProcessor : public Napi::ObjectWrap<DataProcessor> {
public:
    Napi::Value Process(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        size_t count = info[0].As<Napi::Number>().Uint32Value();

        // Automatic tracking with RAII
        TrackedAllocation<double> buffer(env, count);

        if (!buffer.valid()) {
            Napi::Error::New(env, "Allocation failed").ThrowAsJavaScriptException();
            return env.Undefined();
        }

        // Use buffer...
        for (size_t i = 0; i < count; i++) {
            buffer[i] = static_cast<double>(i);
        }

        // Memory automatically tracked on allocation
        // and untracked when buffer goes out of scope

        return Napi::Number::New(env, buffer[0]);
    }
};
```

## Guidelines for External Memory Tracking

| Allocation Type | Track? | Notes |
|-----------------|--------|-------|
| `malloc`/`new` for large data | Yes | Buffers, arrays, images |
| Small structs (<1KB) | Optional | Overhead may not be worth it |
| Memory-mapped files | Yes | Can be gigabytes |
| System resources (handles) | No | Not memory |
| Thread stacks | No | Managed by OS |

## Monitoring External Memory

```javascript
// JavaScript side - check external memory
const v8 = require('v8');
const heapStats = v8.getHeapStatistics();
console.log('External memory:', heapStats.external_memory);
```
