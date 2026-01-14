---
title: Use Finalizers for Cleanup
impact: CRITICAL
impactDescription: Prevents 100% of resource leaks - missing finalizers exhaust file handles (default 1024) in <1 hour under load
tags: memory, finalizers, cleanup, gc, node-addon-api
---

# Use Finalizers for Cleanup

Register destructor callbacks (finalizers) to automatically free native resources when JavaScript objects are garbage collected. This ensures proper cleanup without requiring explicit user action. Without finalizers, file handles and memory leak until process crashes.

## Why This Matters

- **Automatic Cleanup**: Resources freed when JS objects are collected
- **Leak Prevention**: No manual cleanup required from JavaScript
- **Resource Management**: File handles, sockets, etc. properly closed
- **RAII Pattern**: C++ idiom works correctly with GC

## Understanding Finalizers

Finalizers are callbacks invoked by V8 when wrapped objects are garbage collected. They provide a hook to free native memory, close handles, and release resources.

```
Object lifecycle with finalizer:
1. JavaScript: const obj = new NativeWrapper()
2. C++: Constructor allocates native resources
3. JavaScript: obj goes out of scope
4. GC: Detects object is unreachable
5. C++: Finalizer called - free resources
```

## Incorrect: No Finalizer - Memory Leak

```cpp
// PROBLEM: File handles leak - with default ulimit of 1024
// Server crashes after ~1000 requests with "EMFILE: too many open files"
class FileReader {
public:
    void Open(const Napi::CallbackInfo& info) {
        std::string path = info[0].As<Napi::String>().Utf8Value();

        // Opens file handle
        file_ = fopen(path.c_str(), "rb");
        if (!file_) {
            throw Napi::Error::New(info.Env(), "Failed to open file");
        }

        // Get file size for buffer
        fseek(file_, 0, SEEK_END);
        size_ = ftell(file_);
        fseek(file_, 0, SEEK_SET);

        // Allocate buffer
        buffer_ = new uint8_t[size_];
    }

    // NO DESTRUCTOR/FINALIZER!
    // When JS object is collected:
    // - File handle is leaked
    // - Buffer memory is leaked
    // - Eventually run out of file handles or memory

private:
    FILE* file_ = nullptr;
    uint8_t* buffer_ = nullptr;
    size_t size_ = 0;
};
```

## Incorrect: Destructor Without Wrap

```cpp
// BAD: C++ destructor won't be called without proper wrap
class NativeResource : public Napi::ObjectWrap<NativeResource> {
public:
    NativeResource(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<NativeResource>(info) {
        data_ = new uint8_t[1024 * 1024];  // 1MB
    }

    // This destructor exists but may not be called!
    // If Wrap isn't set up correctly, GC won't invoke it
    ~NativeResource() {
        delete[] data_;  // May never execute
    }

private:
    uint8_t* data_;
};

// Missing proper Init with DefineClass...
```

## Correct: ObjectWrap with Destructor

```cpp
// SOLUTION: ObjectWrap destructor is called automatically when GC collects
// Resources are freed even if user forgets to call close()
#include <napi.h>
#include <cstdio>

class FileReader : public Napi::ObjectWrap<FileReader> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "FileReader", {
            InstanceMethod("open", &FileReader::Open),
            InstanceMethod("read", &FileReader::Read),
            InstanceMethod("close", &FileReader::Close),
            InstanceAccessor("isOpen", &FileReader::IsOpen, nullptr)
        });

        exports.Set("FileReader", func);
        return exports;
    }

    FileReader(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<FileReader>(info),
          file_(nullptr), buffer_(nullptr), size_(0) {}

    // CORRECT: Destructor is called when GC collects the JS object
    ~FileReader() {
        Cleanup();
    }

    void Open(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        // Close previous file if any
        Cleanup();

        std::string path = info[0].As<Napi::String>().Utf8Value();
        file_ = fopen(path.c_str(), "rb");
        if (!file_) {
            throw Napi::Error::New(env, "Failed to open file");
        }

        fseek(file_, 0, SEEK_END);
        size_ = ftell(file_);
        fseek(file_, 0, SEEK_SET);

        buffer_ = new uint8_t[size_];
    }

    Napi::Value Read(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        if (!file_) {
            throw Napi::Error::New(env, "File not open");
        }

        size_t bytesRead = fread(buffer_, 1, size_, file_);
        return Napi::Buffer<uint8_t>::Copy(env, buffer_, bytesRead);
    }

    void Close(const Napi::CallbackInfo& info) {
        Cleanup();
    }

    Napi::Value IsOpen(const Napi::CallbackInfo& info) {
        return Napi::Boolean::New(info.Env(), file_ != nullptr);
    }

private:
    void Cleanup() {
        if (file_) {
            fclose(file_);
            file_ = nullptr;
        }
        if (buffer_) {
            delete[] buffer_;
            buffer_ = nullptr;
        }
        size_ = 0;
    }

    FILE* file_;
    uint8_t* buffer_;
    size_t size_;
};

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    return FileReader::Init(env, exports);
}

NODE_API_MODULE(filereader, Init)
```

## Correct: External with Finalizer (Raw N-API)

```cpp
// GOOD: Use napi_wrap or napi_create_external with finalizer
#include <node_api.h>
#include <stdlib.h>
#include <stdio.h>

typedef struct {
    FILE* file;
    uint8_t* buffer;
    size_t size;
} FileContext;

// Finalizer called when JS object is garbage collected
static void FileContextFinalizer(napi_env env, void* finalize_data, void* finalize_hint) {
    FileContext* ctx = (FileContext*)finalize_data;

    // Clean up all resources
    if (ctx->file) {
        fclose(ctx->file);
    }
    if (ctx->buffer) {
        free(ctx->buffer);
    }
    free(ctx);

    // Note: Can't throw errors in finalizer
    // Just log if needed
}

static napi_value CreateFileReader(napi_env env, napi_callback_info info) {
    napi_value wrapper;

    // Allocate native context
    FileContext* ctx = (FileContext*)calloc(1, sizeof(FileContext));
    if (!ctx) {
        napi_throw_error(env, NULL, "Failed to allocate context");
        return NULL;
    }

    // Create JS object
    napi_create_object(env, &wrapper);

    // Wrap with finalizer
    napi_status status = napi_wrap(env, wrapper, ctx, FileContextFinalizer, NULL, NULL);
    if (status != napi_ok) {
        free(ctx);
        napi_throw_error(env, NULL, "Failed to wrap object");
        return NULL;
    }

    return wrapper;
}
```

## Pattern: Buffer with Custom Finalizer

```cpp
// GOOD: External buffer with cleanup callback
Napi::Value CreateExternalBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    size_t size = info[0].As<Napi::Number>().Uint32Value();

    // Allocate native memory
    uint8_t* data = new uint8_t[size];

    // Create Buffer with finalizer
    return Napi::Buffer<uint8_t>::New(
        env,
        data,
        size,
        // Destructor called when Buffer is collected
        [](Napi::Env /*env*/, uint8_t* data) {
            delete[] data;
        }
    );
}
```

## Pattern: Complex Resource with Hint Data

```cpp
// GOOD: Pass hint data to finalizer for context
typedef struct {
    size_t size;
    const char* source;
} AllocationInfo;

static void ComplexFinalizer(napi_env env, void* data, void* hint) {
    AllocationInfo* info = (AllocationInfo*)hint;

    // Log for debugging
    printf("Freeing %zu bytes from %s\n", info->size, info->source);

    // Update external memory tracking
    int64_t change;
    napi_adjust_external_memory(env, -(int64_t)info->size, &change);

    // Free the data
    free(data);
    free(info);
}

napi_value AllocateTracked(napi_env env, size_t size, const char* source) {
    void* data = malloc(size);
    if (!data) return NULL;

    AllocationInfo* info = (AllocationInfo*)malloc(sizeof(AllocationInfo));
    info->size = size;
    info->source = source;

    // Track allocation
    int64_t change;
    napi_adjust_external_memory(env, size, &change);

    napi_value external;
    napi_create_external(env, data, ComplexFinalizer, info, &external);

    return external;
}
```

## Pattern: Weak Reference Cleanup

```cpp
// GOOD: Clean up associated data when weak reference target is collected
class ResourceTracker : public Napi::ObjectWrap<ResourceTracker> {
public:
    void Track(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        Napi::Object target = info[0].As<Napi::Object>();
        std::string name = info[1].As<Napi::String>().Utf8Value();

        // Create weak reference with destructor callback
        auto ref = Napi::Reference<Napi::Object>::New(target, 0);

        // Store tracking info
        auto* trackInfo = new TrackInfo{ name, this };
        trackedObjects_[trackInfo] = std::move(ref);
    }

private:
    struct TrackInfo {
        std::string name;
        ResourceTracker* tracker;
    };

    std::map<TrackInfo*, Napi::Reference<Napi::Object>> trackedObjects_;
};
```

## Finalizer Safety Rules

```cpp
// CRITICAL: What you CANNOT do in finalizers:

static void UnsafeFinalizer(napi_env env, void* data, void* hint) {
    // 1. CANNOT throw exceptions
    // napi_throw_error(env, NULL, "error");  // CRASH!

    // 2. CANNOT call JavaScript
    // napi_call_function(...);  // UNDEFINED BEHAVIOR!

    // 3. CANNOT create new JavaScript values
    // napi_create_string(...);  // MAY CRASH!

    // 4. SHOULD minimize work - GC is paused
    // Avoid: Heavy computation, blocking I/O

    // SAFE operations:
    // - Free native memory (free, delete)
    // - Close file handles (fclose)
    // - Close network connections
    // - Adjust external memory (special case - allowed)
    // - Log to stderr/file
}
```

**When to use:** Always register finalizers for objects that own native resources - file handles, sockets, database connections, large memory allocations, or any OS resource.

**When NOT to use:** Objects that only hold JavaScript values or small amounts of memory (< 1KB) may not need explicit finalizers if using ObjectWrap (destructor is automatic).

## References

- [N-API Object Wrap](https://nodejs.org/api/n-api.html#napi_wrap)
- [N-API Destructor](https://nodejs.org/api/n-api.html#type-definitions)
- [node-addon-api ObjectWrap](https://github.com/nodejs/node-addon-api/blob/main/doc/object_wrap.md)
