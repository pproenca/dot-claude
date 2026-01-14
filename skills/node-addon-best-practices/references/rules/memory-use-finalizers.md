---
title: Register Finalizers for Native Resource Cleanup
impact: CRITICAL
impactDescription: Prevents resource leaks when JavaScript objects are garbage collected
tags: memory, finalizers, gc, cleanup
---

# Register Finalizers for Native Resource Cleanup

When JavaScript objects wrap native resources (memory, file handles, sockets, etc.), register finalizers to clean up those resources when the JavaScript object is garbage collected. Without finalizers, native resources leak when users forget to call cleanup methods.

## Why This Matters

- **Resource Leaks**: File handles, sockets, and memory leak without cleanup
- **Defense in Depth**: Finalizers catch resources missed by manual cleanup
- **Production Safety**: Long-running servers accumulate leaks over time
- **User Convenience**: Users don't need to remember explicit cleanup

## Finalizer vs Destructor

```
┌─────────────────────────────────────────────────────┐
│ JavaScript Object Lifecycle                          │
│                                                      │
│  1. Create: new NativeWrapper(resource)              │
│        ↓                                             │
│  2. Use: wrapper.doSomething()                       │
│        ↓                                             │
│  3. Unreachable: wrapper goes out of scope           │
│        ↓                                             │
│  4. GC Collects: JavaScript object freed             │
│        ↓                                             │
│  5. Finalizer Called: Native cleanup runs            │
│        ↓                                             │
│  6. Resources Released: Memory/handles freed         │
└─────────────────────────────────────────────────────┘

ObjectWrap destructor: Called during GC (step 4-5)
napi_add_finalizer: Explicit finalizer registration
```

## Incorrect: No Finalizer for Native Resources

```cpp
// BAD: Native resources leak when JS object is GC'd
#define NAPI_VERSION 8
#include <napi.h>
#include <cstdio>

class FileReader : public Napi::ObjectWrap<FileReader> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "FileReader", {
            InstanceMethod("read", &FileReader::Read),
            InstanceMethod("close", &FileReader::Close)  // User must remember to call!
        });
        exports.Set("FileReader", func);
        return exports;
    }

    FileReader(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<FileReader>(info), file_(nullptr) {

        std::string path = info[0].As<Napi::String>().Utf8Value();
        file_ = fopen(path.c_str(), "r");
    }

    // BAD: No destructor or finalizer!
    // If user forgets to call close(), file handle leaks

private:
    Napi::Value Read(const Napi::CallbackInfo& info) {
        // ... read implementation
        return info.Env().Undefined();
    }

    Napi::Value Close(const Napi::CallbackInfo& info) {
        if (file_) {
            fclose(file_);
            file_ = nullptr;
        }
        return info.Env().Undefined();
    }

    FILE* file_;
};
```

## Correct: ObjectWrap with Destructor

```cpp
// GOOD: Destructor handles cleanup when GC runs
#define NAPI_VERSION 8
#include <napi.h>
#include <cstdio>

class FileReader : public Napi::ObjectWrap<FileReader> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "FileReader", {
            InstanceMethod("read", &FileReader::Read),
            InstanceMethod("close", &FileReader::Close)
        });
        exports.Set("FileReader", func);
        return exports;
    }

    FileReader(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<FileReader>(info), file_(nullptr) {

        if (info.Length() > 0 && info[0].IsString()) {
            std::string path = info[0].As<Napi::String>().Utf8Value();
            file_ = fopen(path.c_str(), "r");
        }
    }

    // GOOD: Destructor called when JS object is GC'd
    ~FileReader() {
        Cleanup();
    }

private:
    void Cleanup() {
        if (file_) {
            fclose(file_);
            file_ = nullptr;
        }
    }

    Napi::Value Read(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (!file_) {
            Napi::Error::New(env, "File not open").ThrowAsJavaScriptException();
            return env.Undefined();
        }

        char buffer[1024];
        size_t read = fread(buffer, 1, sizeof(buffer) - 1, file_);
        buffer[read] = '\0';

        return Napi::String::New(env, buffer);
    }

    Napi::Value Close(const Napi::CallbackInfo& info) {
        Cleanup();
        return info.Env().Undefined();
    }

    FILE* file_;
};
```

## Correct: Explicit Finalizer with napi_add_finalizer

```cpp
// GOOD: Explicit finalizer for non-ObjectWrap scenarios
#define NAPI_VERSION 8
#include <napi.h>

typedef struct {
    void* data;
    size_t size;
    napi_env env;
} NativeBuffer;

void BufferFinalizer(napi_env env, void* finalize_data, void* finalize_hint) {
    NativeBuffer* buffer = static_cast<NativeBuffer*>(finalize_data);

    if (buffer) {
        // Cleanup native resources
        if (buffer->data) {
            free(buffer->data);

            // Update external memory tracking
            int64_t adjusted;
            napi_adjust_external_memory(env, -static_cast<int64_t>(buffer->size), &adjusted);
        }

        free(buffer);
    }
}

Napi::Value CreateBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    size_t size = info[0].As<Napi::Number>().Uint32Value();

    // Allocate native structure
    NativeBuffer* buffer = static_cast<NativeBuffer*>(malloc(sizeof(NativeBuffer)));
    buffer->size = size;
    buffer->env = env;
    buffer->data = malloc(size);

    if (!buffer->data) {
        free(buffer);
        Napi::Error::New(env, "Allocation failed").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Track external memory
    Napi::MemoryManagement::AdjustExternalMemory(env, size);

    // Create external object with finalizer
    Napi::External<NativeBuffer> external = Napi::External<NativeBuffer>::New(
        env,
        buffer,
        [](Napi::Env env, NativeBuffer* data) {
            // Lambda finalizer
            if (data) {
                if (data->data) {
                    free(data->data);
                    Napi::MemoryManagement::AdjustExternalMemory(env, -static_cast<int64_t>(data->size));
                }
                free(data);
            }
        }
    );

    return external;
}
```

## Correct: Raw N-API Finalizer

```cpp
// GOOD: Raw N-API with explicit finalizer
#include <node_api.h>
#include <stdlib.h>

typedef struct {
    int socket_fd;
    char* buffer;
    size_t buffer_size;
} ConnectionData;

// Finalizer callback
void FinalizeConnection(napi_env env, void* finalize_data, void* finalize_hint) {
    ConnectionData* conn = (ConnectionData*)finalize_data;

    if (conn) {
        // Close socket if still open
        if (conn->socket_fd >= 0) {
            close(conn->socket_fd);
        }

        // Free buffer
        if (conn->buffer) {
            free(conn->buffer);

            // Update external memory
            int64_t adjusted;
            napi_adjust_external_memory(env, -(int64_t)conn->buffer_size, &adjusted);
        }

        free(conn);
    }
}

napi_value CreateConnection(napi_env env, napi_callback_info info) {
    // Allocate connection data
    ConnectionData* conn = malloc(sizeof(ConnectionData));
    conn->socket_fd = -1;  // Would be real socket in practice
    conn->buffer_size = 65536;
    conn->buffer = malloc(conn->buffer_size);

    // Track external memory
    int64_t adjusted;
    napi_adjust_external_memory(env, conn->buffer_size, &adjusted);

    // Create wrapper object
    napi_value wrapper;
    napi_create_object(env, &wrapper);

    // Store native data
    napi_value external;
    napi_create_external(env, conn, FinalizeConnection, NULL, &external);
    napi_set_named_property(env, wrapper, "_native", external);

    return wrapper;
}
```

## Correct: Multiple Resource Cleanup

```cpp
// GOOD: Complex resource management with finalizer
#define NAPI_VERSION 8
#include <napi.h>
#include <vector>
#include <mutex>

class ResourceManager : public Napi::ObjectWrap<ResourceManager> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "ResourceManager", {
            InstanceMethod("allocate", &ResourceManager::Allocate),
            InstanceMethod("release", &ResourceManager::Release),
            InstanceMethod("releaseAll", &ResourceManager::ReleaseAll)
        });
        exports.Set("ResourceManager", func);
        return exports;
    }

    ResourceManager(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<ResourceManager>(info),
          env_(info.Env()),
          total_allocated_(0) {}

    ~ResourceManager() {
        // Destructor acts as finalizer
        std::lock_guard<std::mutex> lock(mutex_);

        for (void* ptr : allocations_) {
            free(ptr);
        }

        if (total_allocated_ > 0) {
            Napi::MemoryManagement::AdjustExternalMemory(env_, -static_cast<int64_t>(total_allocated_));
        }

        allocations_.clear();
        total_allocated_ = 0;
    }

private:
    Napi::Value Allocate(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        size_t size = info[0].As<Napi::Number>().Uint32Value();

        void* ptr = malloc(size);
        if (!ptr) {
            Napi::Error::New(env, "Allocation failed").ThrowAsJavaScriptException();
            return env.Undefined();
        }

        {
            std::lock_guard<std::mutex> lock(mutex_);
            allocations_.push_back(ptr);
            total_allocated_ += size;
        }

        Napi::MemoryManagement::AdjustExternalMemory(env, size);

        return Napi::Number::New(env, allocations_.size());
    }

    Napi::Value Release(const Napi::CallbackInfo& info) {
        // Manual release of specific allocation
        // ... implementation
        return info.Env().Undefined();
    }

    Napi::Value ReleaseAll(const Napi::CallbackInfo& info) {
        std::lock_guard<std::mutex> lock(mutex_);

        for (void* ptr : allocations_) {
            free(ptr);
        }

        if (total_allocated_ > 0) {
            Napi::MemoryManagement::AdjustExternalMemory(env_, -static_cast<int64_t>(total_allocated_));
        }

        allocations_.clear();
        total_allocated_ = 0;

        return info.Env().Undefined();
    }

    Napi::Env env_;
    std::vector<void*> allocations_;
    size_t total_allocated_;
    std::mutex mutex_;
};
```

## Finalizer Best Practices

| Scenario | Approach |
|----------|----------|
| ObjectWrap class | Destructor is your finalizer |
| External data | `Napi::External::New` with cleanup callback |
| Raw N-API | `napi_add_finalizer` or external with finalizer |
| Multiple resources | Single finalizer cleans all |
| Thread safety | Lock mutex in finalizer |

## Finalizer Limitations

1. **No N-API Calls**: Finalizers run during GC; most N-API calls are unsafe
2. **Order Undefined**: Don't depend on finalizer order
3. **May Not Run**: Process exit may skip finalizers
4. **Not Immediate**: Runs when GC decides, not immediately

```cpp
// CAUTION: Limited operations allowed in finalizer
void SafeFinalizer(napi_env env, void* data, void* hint) {
    // SAFE: Free native memory
    free(data);

    // SAFE: Adjust external memory (special case)
    int64_t adjusted;
    napi_adjust_external_memory(env, -1024, &adjusted);

    // UNSAFE: Most other N-API calls
    // napi_create_string_utf8(...);  // DON'T DO THIS
    // napi_call_function(...);       // DON'T DO THIS
}
```
