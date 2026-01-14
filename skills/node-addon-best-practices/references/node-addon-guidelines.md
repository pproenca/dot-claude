# Node.js Native Addon Best Practices

**Version 0.1.0**
Node-API and node-addon-api Documentation
January 2026

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring Node.js native addons in C++. Humans may also
> find it useful, but guidance here is optimized for automation and
> consistency by AI-assisted workflows.

---

## Abstract

Comprehensive best practices guide for Node.js native addon development in C++, designed for AI agents and LLMs. Contains 46 rules across 8 categories, prioritized by impact from critical (ensuring ABI stability across Node.js versions without recompilation, preventing memory leaks and GC-related crashes) to incremental (avoiding common pitfalls that cause subtle bugs). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.

---

## Table of Contents

1. [Node-API & N-API Fundamentals](#1-node-api--n-api-fundamentals) — **CRITICAL**
   - 1.1 [Always Use N-API Over V8](#11-always-use-n-api-over-v8)
   - 1.2 [Define NAPI_VERSION Early](#12-define-napi_version-early)
   - 1.3 [Check All Return Status Codes](#13-check-all-return-status-codes)
   - 1.4 [Use node-addon-api C++ Wrapper](#14-use-node-addon-api-c-wrapper)
   - 1.5 [Use Type-Tagged Objects](#15-use-type-tagged-objects)
   - 1.6 [Validate Input Argument Counts](#16-validate-input-argument-counts)
2. [Memory Management & GC Integration](#2-memory-management--gc-integration) — **CRITICAL**
   - 2.1 [Use Handle Scopes Properly](#21-use-handle-scopes-properly)
   - 2.2 [Use Pointers for Wrap Data](#22-use-pointers-for-wrap-data)
   - 2.3 [Prevent Double-Free in Weak References](#23-prevent-double-free-in-weak-references)
   - 2.4 [Use Reference Pointers Not Values](#24-use-reference-pointers-not-values)
   - 2.5 [Prevent GC From Collecting Active Objects](#25-prevent-gc-from-collecting-active-objects)
   - 2.6 [Clean Up External Buffers](#26-clean-up-external-buffers)
3. [Thread Safety & Async Operations](#3-thread-safety--async-operations) — **HIGH**
   - 3.1 [Use ThreadSafeFunction for Callbacks](#31-use-threadsafefunction-for-callbacks)
   - 3.2 [Never Access V8/N-API From Worker Threads](#32-never-access-v8n-api-from-worker-threads)
   - 3.3 [Use AsyncWorker for CPU Tasks](#33-use-asyncworker-for-cpu-tasks)
   - 3.4 [Handle TSFN Lifecycle Correctly](#34-handle-tsfn-lifecycle-correctly)
   - 3.5 [Use Proper Locking for Shared State](#35-use-proper-locking-for-shared-state)
   - 3.6 [Avoid Blocking the Event Loop](#36-avoid-blocking-the-event-loop)
   - 3.7 [Use AsyncContext for Async Hooks](#37-use-asynccontext-for-async-hooks)
4. [Error Handling & Exception Management](#4-error-handling--exception-management) — **MEDIUM-HIGH**
   - 4.1 [Always Check for Pending Exceptions](#41-always-check-for-pending-exceptions)
   - 4.2 [Use Typed Error Classes](#42-use-typed-error-classes)
   - 4.3 [Never Throw Across Async Boundaries](#43-never-throw-across-async-boundaries)
   - 4.4 [Handle C++ Exceptions at Boundaries](#44-handle-c-exceptions-at-boundaries)
   - 4.5 [Provide Detailed Error Context](#45-provide-detailed-error-context)
   - 4.6 [Use Maybe Pattern for Fallible Operations](#46-use-maybe-pattern-for-fallible-operations)
5. [Performance Optimization](#5-performance-optimization) — **MEDIUM**
   - 5.1 [Minimize JS-Native Boundary Crossings](#51-minimize-js-native-boundary-crossings)
   - 5.2 [Use TypedArrays for Bulk Data](#52-use-typedarrays-for-bulk-data)
   - 5.3 [Cache Frequently Used Values](#53-cache-frequently-used-values)
   - 5.4 [Use ArrayBuffer for Zero-Copy](#54-use-arraybuffer-for-zero-copy)
   - 5.5 [Batch Operations When Possible](#55-batch-operations-when-possible)
   - 5.6 [Profile Before Optimizing](#56-profile-before-optimizing)
6. [Build Systems & Compilation](#6-build-systems--compilation) — **MEDIUM**
   - 6.1 [Use node-gyp or cmake-js](#61-use-node-gyp-or-cmake-js)
   - 6.2 [Support Multiple Platforms](#62-support-multiple-platforms)
   - 6.3 [Use Prebuild for Distribution](#63-use-prebuild-for-distribution)
   - 6.4 [Configure Compiler Warnings](#64-configure-compiler-warnings)
   - 6.5 [Handle Node.js Worker Threads](#65-handle-nodejs-worker-threads)
7. [Security & Input Validation](#7-security--input-validation) — **LOW-MEDIUM**
   - 7.1 [Validate All JavaScript Inputs](#71-validate-all-javascript-inputs)
   - 7.2 [Prevent Buffer Overflows](#72-prevent-buffer-overflows)
   - 7.3 [Sanitize String Inputs](#73-sanitize-string-inputs)
   - 7.4 [Handle Untrusted Data Safely](#74-handle-untrusted-data-safely)
   - 7.5 [Use Secure Memory for Sensitive Data](#75-use-secure-memory-for-sensitive-data)
8. [Common Pitfalls & Anti-Patterns](#8-common-pitfalls--anti-patterns) — **LOW**
   - 8.1 [Avoid Capturing Local Variables](#81-avoid-capturing-local-variables)
   - 8.2 [Don't Store Env Long-Term](#82-dont-store-env-long-term)
   - 8.3 [Handle Module Unload](#83-handle-module-unload)
   - 8.4 [Avoid Recursive N-API Calls](#84-avoid-recursive-n-api-calls)
   - 8.5 [Test Across Node Versions](#85-test-across-node-versions)

---

## 1. Node-API & N-API Fundamentals

**Impact: CRITICAL**

Core N-API patterns for stable ABI, version compatibility, and type-safe JavaScript-C++ interop. These patterns ensure your addon works across Node.js versions without recompilation.

### 1.1 Always Use N-API Over V8

Use stable ABI Node-API instead of V8 C++ API for cross-version compatibility. N-API addons compile once and run on all Node.js versions that support that N-API version.

**Incorrect: Using V8 directly (breaks on Node.js upgrade)**

```cpp
#include <v8.h>
#include <node.h>

void Hello(const v8::FunctionCallbackInfo<v8::Value>& args) {
    v8::Isolate* isolate = args.GetIsolate();
    args.GetReturnValue().Set(
        v8::String::NewFromUtf8(isolate, "world").ToLocalChecked()
    );
}

void Initialize(v8::Local<v8::Object> exports) {
    NODE_SET_METHOD(exports, "hello", Hello);
}

NODE_MODULE(NODE_GYP_MODULE_NAME, Initialize)
```

**Correct: Using node-addon-api (stable ABI)**

```cpp
#include <napi.h>

Napi::String Hello(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    return Napi::String::New(env, "world");
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    exports.Set(Napi::String::New(env, "hello"),
                Napi::Function::New(env, Hello));
    return exports;
}

NODE_API_MODULE(addon, Init)
```

V8 API changes with each Node.js major version, requiring recompilation and code changes. N-API provides a stable C ABI that is forward-compatible across Node.js versions.

---

### 1.2 Define NAPI_VERSION Early

Define `NAPI_VERSION` before including any N-API headers to specify the minimum API version your addon requires. This enables compile-time checking of available features.

**Incorrect: No version defined (unpredictable behavior)**

```cpp
#include <napi.h>  // Uses default version, may vary

Napi::Value UseAsyncCleanup(const Napi::CallbackInfo& info) {
    // napi_add_async_cleanup_hook requires NAPI_VERSION >= 8
    // May fail at runtime without clear error
}
```

**Correct: Explicit version requirement**

```cpp
// In binding.gyp or before includes
#define NAPI_VERSION 8

#include <napi.h>

Napi::Value UseAsyncCleanup(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    // Compiler will error if targeting N-API < 8
    // Runtime guaranteed to have async cleanup hooks
    return env.Undefined();
}
```

**binding.gyp configuration:**

```python
{
  "targets": [{
    "target_name": "addon",
    "defines": ["NAPI_VERSION=8"],
    "sources": ["src/addon.cc"],
    "include_dirs": [
      "<!@(node -p \"require('node-addon-api').include\")"
    ]
  }]
}
```

---

### 1.3 Check All Return Status Codes

Every N-API function returns `napi_status`. Always check for `napi_ok` to catch errors early rather than causing crashes or undefined behavior later.

**Incorrect: Ignoring status codes**

```cpp
napi_value CreateObject(napi_env env) {
    napi_value obj;
    napi_create_object(env, &obj);  // Status ignored!

    napi_value value;
    napi_create_int32(env, 42, &value);  // Status ignored!

    napi_set_named_property(env, obj, "value", value);  // Status ignored!

    return obj;  // May be garbage if any call failed
}
```

**Correct: Checking every status**

```cpp
// Helper macro for status checking
#define NAPI_CALL(env, call)                                    \
    do {                                                        \
        napi_status status = (call);                            \
        if (status != napi_ok) {                                \
            const napi_extended_error_info* error_info;         \
            napi_get_last_error_info((env), &error_info);       \
            napi_throw_error((env), nullptr,                    \
                error_info->error_message);                     \
            return nullptr;                                     \
        }                                                       \
    } while (0)

napi_value CreateObject(napi_env env) {
    napi_value obj;
    NAPI_CALL(env, napi_create_object(env, &obj));

    napi_value value;
    NAPI_CALL(env, napi_create_int32(env, 42, &value));

    NAPI_CALL(env, napi_set_named_property(env, obj, "value", value));

    return obj;
}
```

**With node-addon-api (exceptions handle this automatically):**

```cpp
#define NAPI_CPP_EXCEPTIONS

#include <napi.h>

Napi::Object CreateObject(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Object obj = Napi::Object::New(env);
    obj.Set("value", Napi::Number::New(env, 42));
    // Exceptions thrown automatically on error
    return obj;
}
```

---

### 1.4 Use node-addon-api C++ Wrapper

Prefer the node-addon-api C++ wrapper over raw N-API C functions. It provides RAII, type safety, and exception handling while maintaining ABI stability.

**Incorrect: Raw N-API with manual resource management**

```cpp
#include <node_api.h>

napi_value Add(napi_env env, napi_callback_info info) {
    size_t argc = 2;
    napi_value argv[2];
    napi_get_cb_info(env, info, &argc, argv, nullptr, nullptr);

    if (argc < 2) {
        napi_throw_type_error(env, nullptr, "Expected 2 arguments");
        return nullptr;
    }

    napi_valuetype type0, type1;
    napi_typeof(env, argv[0], &type0);
    napi_typeof(env, argv[1], &type1);

    if (type0 != napi_number || type1 != napi_number) {
        napi_throw_type_error(env, nullptr, "Expected numbers");
        return nullptr;
    }

    double a, b;
    napi_get_value_double(env, argv[0], &a);
    napi_get_value_double(env, argv[1], &b);

    napi_value result;
    napi_create_double(env, a + b, &result);
    return result;
}
```

**Correct: node-addon-api with automatic handling**

```cpp
#include <napi.h>

Napi::Number Add(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 2) {
        Napi::TypeError::New(env, "Expected 2 arguments").ThrowAsJavaScriptException();
        return Napi::Number();
    }

    if (!info[0].IsNumber() || !info[1].IsNumber()) {
        Napi::TypeError::New(env, "Expected numbers").ThrowAsJavaScriptException();
        return Napi::Number();
    }

    double a = info[0].As<Napi::Number>().DoubleValue();
    double b = info[1].As<Napi::Number>().DoubleValue();

    return Napi::Number::New(env, a + b);
}
```

---

### 1.5 Use Type-Tagged Objects

Use `napi_type_tag` to verify that wrapped objects are the correct type, preventing type confusion attacks and crashes from invalid casts.

**Incorrect: No type verification**

```cpp
class MyClass {
public:
    int value = 42;
};

Napi::Value GetValue(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Dangerous: No verification that this is actually a MyClass wrapper
    MyClass* obj = Napi::ObjectWrap<MyClass>::Unwrap(info.This().ToObject());
    return Napi::Number::New(env, obj->value);  // Crash if wrong type!
}
```

**Correct: Using type tags (N-API >= 8)**

```cpp
#define NAPI_VERSION 8
#include <napi.h>

// Unique type tag for this class
static const napi_type_tag MyClassTypeTag = {
    0x1234567890abcdef,  // Lower 64 bits
    0xfedcba0987654321   // Upper 64 bits
};

class MyClass : public Napi::ObjectWrap<MyClass> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "MyClass", {
            InstanceMethod("getValue", &MyClass::GetValue),
        });

        constructor = Napi::Persistent(func);
        constructor.SuppressDestruct();
        exports.Set("MyClass", func);
        return exports;
    }

    MyClass(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<MyClass>(info), value_(42) {
        // Tag the object after creation
        napi_type_tag_object(info.Env(), info.This(), &MyClassTypeTag);
    }

    static MyClass* Unwrap(Napi::Object obj) {
        bool isTagged;
        napi_status status = napi_check_object_type_tag(
            obj.Env(), obj, &MyClassTypeTag, &isTagged);

        if (status != napi_ok || !isTagged) {
            Napi::TypeError::New(obj.Env(),
                "Invalid object type").ThrowAsJavaScriptException();
            return nullptr;
        }

        return Napi::ObjectWrap<MyClass>::Unwrap(obj);
    }

    Napi::Value GetValue(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), value_);
    }

private:
    static Napi::FunctionReference constructor;
    int value_;
};

Napi::FunctionReference MyClass::constructor;
```

---

### 1.6 Validate Input Argument Counts

Always validate argument count and types before accessing. JavaScript can call functions with any number of arguments, including none.

**Incorrect: Assuming arguments exist**

```cpp
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Crash if info.Length() == 0
    std::string path = info[0].As<Napi::String>().Utf8Value();

    // Crash if info.Length() < 2
    Napi::Function callback = info[1].As<Napi::Function>();

    // Process...
}
```

**Correct: Full validation with helpful errors**

```cpp
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Validate argument count
    if (info.Length() < 2) {
        Napi::TypeError::New(env,
            "processData requires 2 arguments: (path: string, callback: function)")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate first argument type
    if (!info[0].IsString()) {
        Napi::TypeError::New(env,
            "First argument 'path' must be a string")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate second argument type
    if (!info[1].IsFunction()) {
        Napi::TypeError::New(env,
            "Second argument 'callback' must be a function")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    std::string path = info[0].As<Napi::String>().Utf8Value();
    Napi::Function callback = info[1].As<Napi::Function>();

    // Process safely...
    return env.Undefined();
}
```

---

## 2. Memory Management & GC Integration

**Impact: CRITICAL**

Proper memory management is essential to prevent leaks, crashes, and GC-related issues. JavaScript's garbage collector must be coordinated with C++ object lifetimes.

### 2.1 Use Handle Scopes Properly

Create `HandleScope` in callbacks to ensure temporary handles are cleaned up. Without scopes, handles accumulate until the JavaScript function returns.

**Incorrect: No handle scope in loop**

```cpp
Napi::Value ProcessMany(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array input = info[0].As<Napi::Array>();

    for (uint32_t i = 0; i < input.Length(); i++) {
        // Each iteration creates handles that accumulate
        Napi::Value item = input.Get(i);
        Napi::Object obj = Napi::Object::New(env);
        obj.Set("index", i);
        obj.Set("value", item);
        // Handles leak until function returns!
    }

    return env.Undefined();
}
```

**Correct: HandleScope in loop body**

```cpp
Napi::Value ProcessMany(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array input = info[0].As<Napi::Array>();
    Napi::Array results = Napi::Array::New(env, input.Length());

    for (uint32_t i = 0; i < input.Length(); i++) {
        // Create scope for temporary handles
        Napi::HandleScope scope(env);

        Napi::Value item = input.Get(i);
        Napi::Object obj = Napi::Object::New(env);
        obj.Set("index", i);
        obj.Set("value", item);

        // Escape the result we need to keep
        results.Set(i, obj);
        // Temporaries cleaned up when scope exits
    }

    return results;
}
```

**For values that must outlive the scope:**

```cpp
Napi::Value CreatePersistent(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    {
        Napi::EscapableHandleScope scope(env);
        Napi::Object obj = Napi::Object::New(env);
        obj.Set("escaped", true);

        // Escape moves handle to outer scope
        return scope.Escape(obj);
    }
}
```

---

### 2.2 Use Pointers for Wrap Data

When using `Wrap()`, always pass heap-allocated pointers. Stack-allocated or member data will become invalid when the frame exits.

**Incorrect: Wrapping stack-allocated data**

```cpp
class Container : public Napi::ObjectWrap<Container> {
public:
    Container(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<Container>(info) {
        // DANGER: Stack-allocated, becomes invalid!
        InnerData data;
        data.value = 42;

        Napi::Object inner = Napi::Object::New(info.Env());
        inner.TypeTag(&InnerTypeTag);
        napi_wrap(info.Env(), inner, &data, nullptr, nullptr, nullptr);
        // &data is garbage after constructor returns!
    }
};
```

**Correct: Wrapping heap-allocated data**

```cpp
class Container : public Napi::ObjectWrap<Container> {
public:
    Container(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<Container>(info) {
        // Heap-allocated, persists until explicitly deleted
        InnerData* data = new InnerData();
        data->value = 42;

        Napi::Object inner = Napi::Object::New(info.Env());

        // Set up destructor to clean up when JS object is GC'd
        napi_wrap(info.Env(), inner, data,
            [](napi_env env, void* data, void* hint) {
                delete static_cast<InnerData*>(data);
            },
            nullptr, nullptr);

        inner_ = Napi::Persistent(inner);
    }

    ~Container() {
        inner_.Reset();  // Allow GC to collect inner object
    }

private:
    Napi::ObjectReference inner_;
};
```

---

### 2.3 Prevent Double-Free in Weak References

When using weak references with pointers, prevent double-free when both GC and destructor try to clean up. Use flag coordination.

**Incorrect: Double-free on weak reference**

```cpp
class Observer {
public:
    Observer(Napi::Env env, Napi::Object target) {
        ref_ = Napi::Weak(target);
        ref_.SuppressDestruct();  // We'll handle cleanup
        data_ = new ObserverData();
    }

    ~Observer() {
        delete data_;  // First delete
    }

    static void Release(Napi::Env env, Observer* observer) {
        delete observer->data_;  // Second delete - CRASH!
        delete observer;
    }

private:
    Napi::WeakReference ref_;
    ObserverData* data_;
};
```

**Correct: Flag-based cleanup coordination**

```cpp
class Observer {
public:
    Observer(Napi::Env env, Napi::Object target)
        : data_(new ObserverData()), released_(false) {
        ref_ = Napi::Weak(target);

        // Add weak callback for GC notification
        ref_.SetPointer(this, OnGC);
    }

    ~Observer() {
        Cleanup();
    }

    void Cleanup() {
        if (!released_) {
            released_ = true;
            delete data_;
            data_ = nullptr;
        }
    }

    static void OnGC(Napi::Env env, void* data) {
        Observer* self = static_cast<Observer*>(data);
        self->Cleanup();  // Safe - checks flag
    }

private:
    Napi::WeakReference ref_;
    ObserverData* data_;
    bool released_;
};
```

---

### 2.4 Use Reference Pointers Not Values

Store `Reference` objects as pointers or in containers, not as class values. References have move-only semantics that cause issues when copied.

**Incorrect: Reference as class member value**

```cpp
class Handler {
public:
    Handler(Napi::Function callback)
        : callback_(Napi::Persistent(callback)) {  // Implicit copy issues
    }

    Handler(const Handler& other) = default;  // Tries to copy Reference!

private:
    Napi::FunctionReference callback_;  // Value semantics problematic
};

std::vector<Handler> handlers;  // Copies happen, References break
```

**Correct: Reference as pointer or unique_ptr**

```cpp
class Handler {
public:
    Handler(Napi::Function callback)
        : callback_(std::make_unique<Napi::FunctionReference>(
            Napi::Persistent(callback))) {
    }

    Handler(Handler&&) = default;  // Move only
    Handler& operator=(Handler&&) = default;

    Handler(const Handler&) = delete;
    Handler& operator=(const Handler&) = delete;

    void Call(Napi::Env env) {
        if (callback_ && !callback_->IsEmpty()) {
            callback_->Call({});
        }
    }

private:
    std::unique_ptr<Napi::FunctionReference> callback_;
};

std::vector<Handler> handlers;  // Moves work correctly
```

---

### 2.5 Prevent GC From Collecting Active Objects

Ensure JavaScript objects backing async operations remain alive. Use persistent references to prevent premature GC.

**Incorrect: Object may be GC'd during async**

```cpp
class AsyncProcessor : public Napi::AsyncWorker {
public:
    AsyncProcessor(Napi::Function callback, Napi::Buffer<uint8_t> data)
        : Napi::AsyncWorker(callback),
          data_(data.Data()),           // Raw pointer to buffer data
          length_(data.Length()) {      // Buffer may be GC'd!
    }

    void Execute() override {
        // DANGER: data_ may point to freed memory if Buffer was GC'd
        Process(data_, length_);
    }

private:
    uint8_t* data_;
    size_t length_;
};
```

**Correct: Hold persistent reference**

```cpp
class AsyncProcessor : public Napi::AsyncWorker {
public:
    AsyncProcessor(Napi::Function callback, Napi::Buffer<uint8_t> data)
        : Napi::AsyncWorker(callback),
          dataRef_(Napi::Persistent(data)),  // Prevents GC
          data_(data.Data()),
          length_(data.Length()) {
    }

    void Execute() override {
        // Safe: dataRef_ keeps Buffer alive
        Process(data_, length_);
    }

    void OnOK() override {
        dataRef_.Reset();  // Release reference
        Callback().Call({Env().Null()});
    }

    void OnError(const Napi::Error& e) override {
        dataRef_.Reset();
        Callback().Call({e.Value()});
    }

private:
    Napi::Reference<Napi::Buffer<uint8_t>> dataRef_;
    uint8_t* data_;
    size_t length_;
};
```

---

### 2.6 Clean Up External Buffers

When creating external buffers with custom data, always provide a destructor to free the data when the buffer is garbage collected.

**Incorrect: Memory leak with external buffer**

```cpp
Napi::Value CreateBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    size_t size = 1024;
    uint8_t* data = new uint8_t[size];
    std::fill_n(data, size, 0);

    // Memory leak! No way to free 'data' when buffer is GC'd
    return Napi::Buffer<uint8_t>::New(env, data, size);
}
```

**Correct: Destructor callback frees memory**

```cpp
Napi::Value CreateBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    size_t size = 1024;
    uint8_t* data = new uint8_t[size];
    std::fill_n(data, size, 0);

    // Destructor called when buffer is GC'd
    return Napi::Buffer<uint8_t>::New(
        env,
        data,
        size,
        [](Napi::Env /*env*/, uint8_t* data) {
            delete[] data;
        }
    );
}

// For more complex cleanup with hint data
Napi::Value CreateBufferWithContext(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    struct BufferContext {
        uint8_t* data;
        size_t size;
        std::string source;
    };

    auto* ctx = new BufferContext();
    ctx->size = 1024;
    ctx->data = new uint8_t[ctx->size];
    ctx->source = "dynamic allocation";

    return Napi::Buffer<uint8_t>::New(
        env,
        ctx->data,
        ctx->size,
        [](Napi::Env /*env*/, uint8_t* /*data*/, BufferContext* ctx) {
            delete[] ctx->data;
            delete ctx;
        },
        ctx  // Hint passed to destructor
    );
}
```

---

## 3. Thread Safety & Async Operations

**Impact: HIGH**

Node.js runs JavaScript in a single thread. Native addons must carefully coordinate worker threads with the main thread to avoid crashes and data races.

### 3.1 Use ThreadSafeFunction for Callbacks

Call JavaScript callbacks from worker threads using `ThreadSafeFunction`. Direct callback invocation from non-main threads causes undefined behavior.

**Incorrect: Calling JS from worker thread**

```cpp
class BadWorker {
public:
    void Start(Napi::Function callback) {
        callback_ = Napi::Persistent(callback);

        worker_ = std::thread([this]() {
            // CRASH: Cannot call JS from worker thread!
            callback_.Call({});
        });
    }

private:
    Napi::FunctionReference callback_;
    std::thread worker_;
};
```

**Correct: Using ThreadSafeFunction**

```cpp
class SafeWorker {
public:
    SafeWorker(Napi::Env env, Napi::Function callback) {
        tsfn_ = Napi::ThreadSafeFunction::New(
            env,
            callback,
            "SafeWorker",   // Resource name for async_hooks
            0,              // Max queue size (0 = unlimited)
            1               // Initial thread count
        );
    }

    void Start() {
        worker_ = std::thread([this]() {
            // Simulate work
            std::this_thread::sleep_for(std::chrono::milliseconds(100));

            // Safe: TSFN queues call to main thread
            tsfn_.BlockingCall([](Napi::Env env, Napi::Function callback) {
                callback.Call({Napi::String::New(env, "done")});
            });

            tsfn_.Release();
        });
    }

    ~SafeWorker() {
        if (worker_.joinable()) {
            worker_.join();
        }
    }

private:
    Napi::ThreadSafeFunction tsfn_;
    std::thread worker_;
};
```

---

### 3.2 Never Access V8/N-API From Worker Threads

N-API handles and values are only valid on the main thread. Pass primitive data between threads, not Napi objects.

**Incorrect: Passing Napi::Value to worker thread**

```cpp
class BadAsync {
public:
    void Process(Napi::Value input) {
        worker_ = std::thread([this, input]() {  // Captures Napi::Value!
            // CRASH: input handle invalid on worker thread
            if (input.IsString()) {
                std::string s = input.As<Napi::String>().Utf8Value();
            }
        });
    }
};
```

**Correct: Convert to C++ types before threading**

```cpp
class SafeAsync {
public:
    void Process(Napi::Env env, Napi::Value input, Napi::Function callback) {
        // Convert to C++ types on main thread
        std::string inputStr;
        if (input.IsString()) {
            inputStr = input.As<Napi::String>().Utf8Value();
        }

        auto tsfn = Napi::ThreadSafeFunction::New(
            env, callback, "SafeAsync", 0, 1);

        worker_ = std::thread([inputStr, tsfn]() mutable {
            // Process C++ string (safe)
            std::string result = ProcessString(inputStr);

            tsfn.BlockingCall([result](Napi::Env env, Napi::Function cb) {
                // Convert back to JS on main thread
                cb.Call({env.Null(), Napi::String::New(env, result)});
            });

            tsfn.Release();
        });
        worker_.detach();
    }

private:
    std::thread worker_;
};
```

---

### 3.3 Use AsyncWorker for CPU Tasks

For CPU-bound work, extend `Napi::AsyncWorker` to run work off the main thread with proper lifecycle management.

**Incorrect: Blocking the event loop**

```cpp
Napi::Value ComputeSync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    int n = info[0].As<Napi::Number>().Int32Value();

    // BLOCKS event loop for entire computation!
    long long result = 0;
    for (int i = 0; i < n * 1000000; i++) {
        result += ExpensiveCalculation(i);
    }

    return Napi::Number::New(env, static_cast<double>(result));
}
```

**Correct: Using AsyncWorker**

```cpp
class ComputeWorker : public Napi::AsyncWorker {
public:
    ComputeWorker(Napi::Function callback, int iterations)
        : Napi::AsyncWorker(callback), iterations_(iterations), result_(0) {}

    // Runs on worker thread - no Napi calls!
    void Execute() override {
        for (int i = 0; i < iterations_ * 1000000; i++) {
            result_ += ExpensiveCalculation(i);
        }
    }

    // Runs on main thread after Execute completes
    void OnOK() override {
        Napi::HandleScope scope(Env());
        Callback().Call({
            Env().Null(),
            Napi::Number::New(Env(), static_cast<double>(result_))
        });
    }

    void OnError(const Napi::Error& e) override {
        Napi::HandleScope scope(Env());
        Callback().Call({e.Value()});
    }

private:
    int iterations_;
    long long result_;
};

Napi::Value ComputeAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    int iterations = info[0].As<Napi::Number>().Int32Value();
    Napi::Function callback = info[1].As<Napi::Function>();

    ComputeWorker* worker = new ComputeWorker(callback, iterations);
    worker->Queue();  // Transfers ownership, will be deleted automatically

    return env.Undefined();
}
```

---

### 3.4 Handle TSFN Lifecycle Correctly

ThreadSafeFunction has reference counting. Call `Acquire()` for new threads and `Release()` when done. The TSFN is destroyed when count reaches zero.

**Incorrect: Improper TSFN lifecycle**

```cpp
class BadTSFN {
    Napi::ThreadSafeFunction tsfn_;

    void Start(Napi::Env env, Napi::Function cb) {
        tsfn_ = Napi::ThreadSafeFunction::New(env, cb, "Bad", 0, 1);

        // Start multiple threads without acquiring
        for (int i = 0; i < 5; i++) {
            std::thread([this, i]() {
                tsfn_.BlockingCall();  // May fail - only 1 thread registered!
            }).detach();
        }
    }

    // TSFN may be released while threads still running!
};
```

**Correct: Proper acquire/release pattern**

```cpp
class GoodTSFN {
    Napi::ThreadSafeFunction tsfn_;
    std::vector<std::thread> workers_;
    std::atomic<int> completedCount_{0};

public:
    void Start(Napi::Env env, Napi::Function cb, int numThreads) {
        // Initial thread count matches number of workers
        tsfn_ = Napi::ThreadSafeFunction::New(
            env, cb, "Good", 0, numThreads);

        for (int i = 0; i < numThreads; i++) {
            workers_.emplace_back([this, i, numThreads]() {
                // Do work
                DoWork(i);

                // Signal completion
                tsfn_.BlockingCall([i](Napi::Env env, Napi::Function cb) {
                    cb.Call({
                        env.Null(),
                        Napi::Number::New(env, i)
                    });
                });

                // Release our reference
                // When all threads release, TSFN is destroyed
                tsfn_.Release();
            });
        }
    }

    ~GoodTSFN() {
        for (auto& w : workers_) {
            if (w.joinable()) w.join();
        }
    }
};
```

---

### 3.5 Use Proper Locking for Shared State

Protect shared state accessed by multiple threads with mutexes. Node-API itself is not thread-safe.

**Incorrect: Unprotected shared state**

```cpp
class UnsafeCounter {
    int count_ = 0;  // Shared, unprotected!

public:
    void IncrementFromWorker() {
        std::thread([this]() {
            for (int i = 0; i < 1000; i++) {
                count_++;  // Data race!
            }
        }).detach();
    }

    int GetCount() { return count_; }  // May read torn value!
};
```

**Correct: Mutex-protected state**

```cpp
class SafeCounter {
    std::atomic<int> count_{0};  // For simple counters

    // For complex state:
    mutable std::mutex mutex_;
    std::vector<int> data_;

public:
    void IncrementFromWorker() {
        std::thread([this]() {
            for (int i = 0; i < 1000; i++) {
                count_.fetch_add(1, std::memory_order_relaxed);
            }
        }).detach();
    }

    void AddData(int value) {
        std::lock_guard<std::mutex> lock(mutex_);
        data_.push_back(value);
    }

    std::vector<int> GetData() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return data_;  // Return copy while holding lock
    }

    int GetCount() const {
        return count_.load(std::memory_order_relaxed);
    }
};
```

---

### 3.6 Avoid Blocking the Event Loop

Long-running synchronous operations block all JavaScript. Use async patterns or break work into chunks.

**Incorrect: Blocking sync operation**

```cpp
Napi::Value ReadLargeFile(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string path = info[0].As<Napi::String>().Utf8Value();

    // Blocks event loop for entire read!
    std::ifstream file(path, std::ios::binary | std::ios::ate);
    size_t size = file.tellg();
    file.seekg(0);

    std::vector<char> buffer(size);
    file.read(buffer.data(), size);  // Blocking I/O

    return Napi::Buffer<char>::Copy(env, buffer.data(), size);
}
```

**Correct: Async file read**

```cpp
class FileReadWorker : public Napi::AsyncWorker {
public:
    FileReadWorker(Napi::Function callback, std::string path)
        : Napi::AsyncWorker(callback), path_(std::move(path)) {}

    void Execute() override {
        std::ifstream file(path_, std::ios::binary | std::ios::ate);
        if (!file) {
            SetError("Failed to open file: " + path_);
            return;
        }

        size_t size = file.tellg();
        file.seekg(0);

        data_.resize(size);
        file.read(data_.data(), size);

        if (!file) {
            SetError("Failed to read file: " + path_);
        }
    }

    void OnOK() override {
        Napi::HandleScope scope(Env());
        auto buffer = Napi::Buffer<char>::Copy(
            Env(), data_.data(), data_.size());
        Callback().Call({Env().Null(), buffer});
    }

private:
    std::string path_;
    std::vector<char> data_;
};

Napi::Value ReadLargeFileAsync(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    std::string path = info[0].As<Napi::String>().Utf8Value();
    Napi::Function callback = info[1].As<Napi::Function>();

    auto* worker = new FileReadWorker(callback, path);
    worker->Queue();

    return env.Undefined();
}
```

---

### 3.7 Use AsyncContext for Async Hooks

Wrap async operations in `AsyncContext` to integrate with Node.js async_hooks for proper tracing and debugging.

**Incorrect: Breaking async_hooks chain**

```cpp
void StartOperation(Napi::Function callback) {
    auto tsfn = Napi::ThreadSafeFunction::New(
        callback.Env(),
        callback,
        "operation",  // Resource name only
        0, 1
    );

    std::thread([tsfn]() mutable {
        // async_hooks won't see this as connected to original call
        tsfn.BlockingCall();
        tsfn.Release();
    }).detach();
}
```

**Correct: Using AsyncContext**

```cpp
class TrackedOperation {
public:
    TrackedOperation(Napi::Env env, Napi::Function callback)
        : context_(env, "TrackedOperation") {

        tsfn_ = Napi::ThreadSafeFunction::New(
            env,
            callback,
            context_,  // Pass AsyncContext
            "TrackedOperation",
            0, 1
        );
    }

    void Start() {
        std::thread([this]() {
            DoWork();

            tsfn_.BlockingCall([](Napi::Env env, Napi::Function callback) {
                // async_hooks properly tracks this callback
                callback.Call({env.Null()});
            });

            tsfn_.Release();
        }).detach();
    }

private:
    Napi::AsyncContext context_;
    Napi::ThreadSafeFunction tsfn_;
};
```

---

## 4. Error Handling & Exception Management

**Impact: MEDIUM-HIGH**

Proper error handling prevents crashes, provides useful debugging information, and maintains JavaScript's error conventions.

### 4.1 Always Check for Pending Exceptions

After any N-API call that might throw, check for pending exceptions before continuing. Operations on invalid state cause crashes.

**Incorrect: Ignoring pending exceptions**

```cpp
Napi::Value ParseJSON(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Object json = env.Global().Get("JSON").As<Napi::Object>();
    Napi::Function parse = json.Get("parse").As<Napi::Function>();

    // May throw if input is invalid JSON
    Napi::Value result = parse.Call(json, {info[0]});

    // CRASH: Accessing result when exception is pending!
    return result.As<Napi::Object>().Get("data");
}
```

**Correct: Check for exceptions**

```cpp
Napi::Value ParseJSON(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Object json = env.Global().Get("JSON").As<Napi::Object>();
    Napi::Function parse = json.Get("parse").As<Napi::Function>();

    Napi::Value result = parse.Call(json, {info[0]});

    // Check if JSON.parse threw
    if (env.IsExceptionPending()) {
        return env.Undefined();  // Let exception propagate
    }

    if (!result.IsObject()) {
        Napi::TypeError::New(env, "Expected object from JSON.parse")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    return result.As<Napi::Object>().Get("data");
}
```

**With C++ exceptions enabled:**

```cpp
#define NAPI_CPP_EXCEPTIONS
#include <napi.h>

Napi::Value ParseJSON(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    try {
        Napi::Object json = env.Global().Get("JSON").As<Napi::Object>();
        Napi::Function parse = json.Get("parse").As<Napi::Function>();
        Napi::Value result = parse.Call(json, {info[0]});
        return result.As<Napi::Object>().Get("data");
    } catch (const Napi::Error& e) {
        // Re-throw to JavaScript
        e.ThrowAsJavaScriptException();
        return env.Undefined();
    }
}
```

---

### 4.2 Use Typed Error Classes

Use specific error types (`TypeError`, `RangeError`, etc.) for appropriate errors. This helps JavaScript catch blocks and debugging tools.

**Incorrect: Generic errors only**

```cpp
Napi::Value SetPort(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsNumber()) {
        // Generic Error - hard to catch specifically
        Napi::Error::New(env, "Invalid argument").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    int port = info[0].As<Napi::Number>().Int32Value();
    if (port < 0 || port > 65535) {
        // Generic Error - doesn't indicate range issue
        Napi::Error::New(env, "Invalid port").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    return env.Undefined();
}
```

**Correct: Typed errors with context**

```cpp
Napi::Value SetPort(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 1) {
        Napi::TypeError::New(env,
            "setPort requires 1 argument: port number")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (!info[0].IsNumber()) {
        Napi::TypeError::New(env,
            "Port must be a number, got " +
            std::string(info[0].Type() == napi_string ? "string" : "non-number"))
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    int port = info[0].As<Napi::Number>().Int32Value();
    if (port < 0 || port > 65535) {
        Napi::RangeError::New(env,
            "Port must be between 0 and 65535, got " + std::to_string(port))
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Valid port...
    return env.Undefined();
}
```

---

### 4.3 Never Throw Across Async Boundaries

Errors in async callbacks can't be caught by surrounding try/catch. Always pass errors through callback's error parameter.

**Incorrect: Throwing in async callback**

```cpp
class BadAsyncWorker : public Napi::AsyncWorker {
public:
    BadAsyncWorker(Napi::Function cb) : Napi::AsyncWorker(cb) {}

    void Execute() override {
        if (!DoWork()) {
            // This doesn't work! Execute runs on worker thread
            throw std::runtime_error("Work failed");
        }
    }

    void OnOK() override {
        // Throwing here is also problematic
        if (!Validate()) {
            throw Napi::Error::New(Env(), "Validation failed");
        }
        Callback().Call({Env().Null()});
    }
};
```

**Correct: Use SetError and callback error parameter**

```cpp
class GoodAsyncWorker : public Napi::AsyncWorker {
public:
    GoodAsyncWorker(Napi::Function cb) : Napi::AsyncWorker(cb) {}

    void Execute() override {
        try {
            if (!DoWork()) {
                SetError("Work failed: " + GetLastError());
                return;
            }

            if (!Validate()) {
                SetError("Validation failed");
                return;
            }
        } catch (const std::exception& e) {
            SetError(std::string("Exception: ") + e.what());
        }
    }

    void OnOK() override {
        Napi::HandleScope scope(Env());
        // Pass null as first arg to indicate success
        Callback().Call({Env().Null(), Napi::String::New(Env(), "success")});
    }

    void OnError(const Napi::Error& e) override {
        Napi::HandleScope scope(Env());
        // Pass error as first arg (Node.js convention)
        Callback().Call({e.Value()});
    }
};
```

---

### 4.4 Handle C++ Exceptions at Boundaries

C++ exceptions must be caught at the JavaScript boundary. Uncaught exceptions cause process termination.

**Incorrect: C++ exception escapes to JavaScript**

```cpp
Napi::Value ProcessFile(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string path = info[0].As<Napi::String>().Utf8Value();

    // If ReadFile throws, process crashes!
    std::string content = ReadFile(path);  // May throw std::ios_base::failure

    return Napi::String::New(env, content);
}
```

**Correct: Catch and convert to JavaScript error**

```cpp
Napi::Value ProcessFile(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    try {
        std::string path = info[0].As<Napi::String>().Utf8Value();
        std::string content = ReadFile(path);
        return Napi::String::New(env, content);

    } catch (const std::ios_base::failure& e) {
        Napi::Error::New(env,
            std::string("File I/O error: ") + e.what())
            .ThrowAsJavaScriptException();
        return env.Undefined();

    } catch (const std::invalid_argument& e) {
        Napi::TypeError::New(env, e.what())
            .ThrowAsJavaScriptException();
        return env.Undefined();

    } catch (const std::exception& e) {
        Napi::Error::New(env,
            std::string("Native error: ") + e.what())
            .ThrowAsJavaScriptException();
        return env.Undefined();

    } catch (...) {
        Napi::Error::New(env, "Unknown native exception")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }
}
```

---

### 4.5 Provide Detailed Error Context

Include operation name, parameter values, and state information in error messages for easier debugging.

**Incorrect: Vague error messages**

```cpp
Napi::Value Connect(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsString()) {
        Napi::TypeError::New(env, "Invalid argument")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    std::string host = info[0].As<Napi::String>().Utf8Value();
    if (!DoConnect(host)) {
        Napi::Error::New(env, "Connection failed")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    return env.Undefined();
}
```

**Correct: Detailed contextual errors**

```cpp
Napi::Value Connect(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Validate argument count
    if (info.Length() < 1) {
        Napi::TypeError::New(env,
            "connect() requires 1 argument (host: string), got 0")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate argument type with actual type info
    if (!info[0].IsString()) {
        std::string actualType = GetTypeName(info[0]);
        Napi::TypeError::New(env,
            "connect() argument 'host' must be string, got " + actualType)
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    std::string host = info[0].As<Napi::String>().Utf8Value();

    // Validate string content
    if (host.empty()) {
        Napi::RangeError::New(env,
            "connect() argument 'host' cannot be empty string")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Include context in operation errors
    int errorCode = 0;
    if (!DoConnect(host, &errorCode)) {
        std::ostringstream msg;
        msg << "connect() failed for host '" << host << "': "
            << GetErrorDescription(errorCode)
            << " (error code: " << errorCode << ")";
        Napi::Error::New(env, msg.str())
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    return env.Undefined();
}

std::string GetTypeName(Napi::Value value) {
    switch (value.Type()) {
        case napi_undefined: return "undefined";
        case napi_null: return "null";
        case napi_boolean: return "boolean";
        case napi_number: return "number";
        case napi_string: return "string";
        case napi_symbol: return "symbol";
        case napi_object: return "object";
        case napi_function: return "function";
        case napi_external: return "external";
        case napi_bigint: return "bigint";
        default: return "unknown";
    }
}
```

---

### 4.6 Use Maybe Pattern for Fallible Operations

For operations that might fail, use return values to indicate success/failure rather than only exceptions. This supports both exception and non-exception modes.

**Incorrect: Only exception-based error handling**

```cpp
class Parser {
public:
    // Only works with NAPI_CPP_EXCEPTIONS
    Napi::Value Parse(const Napi::CallbackInfo& info) {
        std::string input = info[0].As<Napi::String>().Utf8Value();

        // Throws on failure - no way to check without catching
        Result result = ParseInput(input);
        return ResultToJS(info.Env(), result);
    }
};
```

**Correct: Maybe/Optional pattern**

```cpp
#include <optional>

class Parser {
public:
    Napi::Value Parse(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        if (!info[0].IsString()) {
            return env.Undefined();
        }

        std::string input = info[0].As<Napi::String>().Utf8Value();

        std::string errorMsg;
        std::optional<Result> result = TryParseInput(input, errorMsg);

        if (!result.has_value()) {
            Napi::Error::New(env, "Parse error: " + errorMsg)
                .ThrowAsJavaScriptException();
            return env.Undefined();
        }

        return ResultToJS(env, *result);
    }

    // Alternative: Return object with success/error fields
    Napi::Value SafeParse(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        Napi::Object response = Napi::Object::New(env);

        if (!info[0].IsString()) {
            response.Set("success", false);
            response.Set("error", "Input must be a string");
            return response;
        }

        std::string input = info[0].As<Napi::String>().Utf8Value();
        std::string errorMsg;
        std::optional<Result> result = TryParseInput(input, errorMsg);

        if (result.has_value()) {
            response.Set("success", true);
            response.Set("value", ResultToJS(env, *result));
        } else {
            response.Set("success", false);
            response.Set("error", errorMsg);
        }

        return response;
    }
};
```

---

## 5. Performance Optimization

**Impact: MEDIUM**

Native addons should be faster than pure JavaScript. These patterns ensure you get the performance benefits of C++ without hidden overhead.

### 5.1 Minimize JS-Native Boundary Crossings

Each call between JavaScript and native code has overhead. Batch operations to reduce crossing count.

**Incorrect: Many small calls**

```cpp
// JavaScript calls this once per item - N crossings!
Napi::Value ProcessItem(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    int item = info[0].As<Napi::Number>().Int32Value();
    return Napi::Number::New(env, ComputeItem(item));
}

// In JavaScript:
// items.map(item => addon.processItem(item))  // N boundary crossings
```

**Correct: Batch processing**

```cpp
// Process all items in one call - 1 crossing!
Napi::Value ProcessItems(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array input = info[0].As<Napi::Array>();
    uint32_t length = input.Length();

    Napi::Array output = Napi::Array::New(env, length);

    for (uint32_t i = 0; i < length; i++) {
        int item = input.Get(i).As<Napi::Number>().Int32Value();
        output.Set(i, Napi::Number::New(env, ComputeItem(item)));
    }

    return output;
}

// In JavaScript:
// const results = addon.processItems(items);  // 1 boundary crossing
```

---

### 5.2 Use TypedArrays for Bulk Data

TypedArrays (`Float64Array`, `Int32Array`, etc.) provide direct memory access without per-element conversion overhead.

**Incorrect: Regular arrays with per-element access**

```cpp
Napi::Value SumArray(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array arr = info[0].As<Napi::Array>();

    double sum = 0;
    for (uint32_t i = 0; i < arr.Length(); i++) {
        // Each Get() creates a handle and does type conversion
        sum += arr.Get(i).As<Napi::Number>().DoubleValue();
    }

    return Napi::Number::New(env, sum);
}
```

**Correct: TypedArray with direct memory access**

```cpp
Napi::Value SumFloat64Array(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsTypedArray()) {
        Napi::TypeError::New(env, "Expected TypedArray")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::TypedArray typedArray = info[0].As<Napi::TypedArray>();

    if (typedArray.TypedArrayType() != napi_float64_array) {
        Napi::TypeError::New(env, "Expected Float64Array")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Float64Array arr = info[0].As<Napi::Float64Array>();
    double* data = arr.Data();  // Direct pointer to memory
    size_t length = arr.ElementLength();

    double sum = 0;
    for (size_t i = 0; i < length; i++) {
        sum += data[i];  // No handles, no conversion
    }

    return Napi::Number::New(env, sum);
}
```

---

### 5.3 Cache Frequently Used Values

Cache `Napi::FunctionReference`, property names, and other values that are used repeatedly rather than looking them up each time.

**Incorrect: Repeated lookups**

```cpp
class Logger {
public:
    void Log(Napi::Env env, const std::string& message) {
        // These lookups happen EVERY call
        Napi::Object console = env.Global().Get("console").As<Napi::Object>();
        Napi::Function log = console.Get("log").As<Napi::Function>();
        log.Call(console, {Napi::String::New(env, message)});
    }
};
```

**Correct: Cache at initialization**

```cpp
class Logger : public Napi::ObjectWrap<Logger> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "Logger", {
            InstanceMethod("log", &Logger::Log),
        });

        constructor = Napi::Persistent(func);
        constructor.SuppressDestruct();
        exports.Set("Logger", func);
        return exports;
    }

    Logger(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<Logger>(info) {
        Napi::Env env = info.Env();

        // Cache console.log at construction time
        Napi::Object console = env.Global().Get("console").As<Napi::Object>();
        Napi::Function logFn = console.Get("log").As<Napi::Function>();

        consoleRef_ = Napi::Persistent(console);
        logRef_ = Napi::Persistent(logFn);
    }

    Napi::Value Log(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        // Use cached references - no lookup!
        logRef_.Call(consoleRef_.Value(), {info[0]});

        return env.Undefined();
    }

private:
    static Napi::FunctionReference constructor;
    Napi::ObjectReference consoleRef_;
    Napi::FunctionReference logRef_;
};

Napi::FunctionReference Logger::constructor;
```

---

### 5.4 Use ArrayBuffer for Zero-Copy

Share memory between JavaScript and C++ without copying using `ArrayBuffer` with external data.

**Incorrect: Copying data between JS and C++**

```cpp
class ImageProcessor {
    std::vector<uint8_t> imageData_;

public:
    Napi::Value GetData(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        // Creates copy of entire image buffer!
        return Napi::Buffer<uint8_t>::Copy(
            env, imageData_.data(), imageData_.size());
    }

    void SetData(const Napi::CallbackInfo& info) {
        Napi::Buffer<uint8_t> buf = info[0].As<Napi::Buffer<uint8_t>>();

        // Another copy!
        imageData_.assign(buf.Data(), buf.Data() + buf.Length());
    }
};
```

**Correct: Zero-copy with external ArrayBuffer**

```cpp
class ImageProcessor {
    uint8_t* imageData_ = nullptr;
    size_t imageSize_ = 0;
    Napi::Reference<Napi::ArrayBuffer> bufferRef_;

public:
    void Initialize(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        size_t size = info[0].As<Napi::Number>().Uint32Value();

        // Allocate memory owned by C++
        imageData_ = new uint8_t[size];
        imageSize_ = size;

        // Create ArrayBuffer backed by our memory
        Napi::ArrayBuffer ab = Napi::ArrayBuffer::New(
            env,
            imageData_,
            imageSize_,
            [](Napi::Env /*env*/, void* data) {
                delete[] static_cast<uint8_t*>(data);
            }
        );

        // Keep reference to prevent GC
        bufferRef_ = Napi::Persistent(ab);
    }

    Napi::Value GetBuffer(const Napi::CallbackInfo& info) {
        // No copy - returns view of same memory
        return bufferRef_.Value();
    }

    void ProcessInPlace() {
        // Modify imageData_ directly
        // JavaScript sees changes immediately through same ArrayBuffer
        for (size_t i = 0; i < imageSize_; i++) {
            imageData_[i] = ProcessPixel(imageData_[i]);
        }
    }
};
```

---

### 5.5 Batch Operations When Possible

Combine multiple related operations into single calls to amortize overhead.

**Incorrect: Multiple separate operations**

```cpp
// In JavaScript: separate calls for each operation
// const db = new Database();
// db.prepare(sql);
// db.bind(0, value1);
// db.bind(1, value2);
// db.bind(2, value3);
// const result = db.execute();

class Database : public Napi::ObjectWrap<Database> {
    void Prepare(const Napi::CallbackInfo& info);
    void Bind(const Napi::CallbackInfo& info);
    Napi::Value Execute(const Napi::CallbackInfo& info);
};
```

**Correct: Combined operation with options object**

```cpp
// In JavaScript: single call with all parameters
// const result = db.query(sql, [value1, value2, value3]);

class Database : public Napi::ObjectWrap<Database> {
    Napi::Value Query(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        std::string sql = info[0].As<Napi::String>().Utf8Value();

        // All parameters in one call
        std::vector<std::string> params;
        if (info.Length() > 1 && info[1].IsArray()) {
            Napi::Array arr = info[1].As<Napi::Array>();
            for (uint32_t i = 0; i < arr.Length(); i++) {
                params.push_back(arr.Get(i).ToString().Utf8Value());
            }
        }

        // Options in third argument
        QueryOptions opts;
        if (info.Length() > 2 && info[2].IsObject()) {
            Napi::Object options = info[2].As<Napi::Object>();
            if (options.Has("timeout")) {
                opts.timeout = options.Get("timeout").As<Napi::Number>().Int32Value();
            }
            if (options.Has("rowLimit")) {
                opts.rowLimit = options.Get("rowLimit").As<Napi::Number>().Int32Value();
            }
        }

        // Single native call does everything
        Result result = ExecuteQuery(sql, params, opts);
        return ResultToJS(env, result);
    }
};
```

---

### 5.6 Profile Before Optimizing

Measure actual performance before and after optimizations. Premature optimization often adds complexity without meaningful improvement.

**Profiling setup:**

```cpp
#include <chrono>

class Profiler {
public:
    void Start(const std::string& name) {
        name_ = name;
        start_ = std::chrono::high_resolution_clock::now();
    }

    void End() {
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
            end - start_).count();
        printf("[%s] %lld us\n", name_.c_str(), duration);
    }

private:
    std::string name_;
    std::chrono::high_resolution_clock::time_point start_;
};

// Use in addon
Napi::Value BenchmarkedOperation(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    #ifdef ENABLE_PROFILING
    Profiler p;
    p.Start("BenchmarkedOperation");
    #endif

    // Do work...

    #ifdef ENABLE_PROFILING
    p.End();
    #endif

    return result;
}
```

**JavaScript-side profiling:**

```javascript
// benchmark.js
const addon = require('./build/Release/addon');

function benchmark(name, fn, iterations = 10000) {
    // Warmup
    for (let i = 0; i < 100; i++) fn();

    const start = process.hrtime.bigint();
    for (let i = 0; i < iterations; i++) {
        fn();
    }
    const end = process.hrtime.bigint();

    const totalNs = Number(end - start);
    const avgNs = totalNs / iterations;
    console.log(`${name}: ${avgNs.toFixed(2)} ns/op (${iterations} iterations)`);
}

// Compare implementations
benchmark('processArray', () => addon.processArray(testData));
benchmark('processTypedArray', () => addon.processTypedArray(typedData));
```

---

## 6. Build Systems & Compilation

**Impact: MEDIUM**

Proper build configuration ensures reliable compilation across platforms and Node.js versions.

### 6.1 Use node-gyp or cmake-js

Use established build systems that handle Node.js/N-API paths and configurations automatically.

**binding.gyp (node-gyp):**

```python
{
  "targets": [{
    "target_name": "addon",
    "cflags!": ["-fno-exceptions"],
    "cflags_cc!": ["-fno-exceptions"],
    "defines": [
      "NAPI_VERSION=8",
      "NAPI_CPP_EXCEPTIONS"
    ],
    "sources": [
      "src/addon.cc",
      "src/worker.cc"
    ],
    "include_dirs": [
      "<!@(node -p \"require('node-addon-api').include\")",
      "src/include"
    ],
    "dependencies": [
      "<!(node -p \"require('node-addon-api').gyp\")"
    ],
    "conditions": [
      ["OS=='mac'", {
        "xcode_settings": {
          "GCC_ENABLE_CPP_EXCEPTIONS": "YES",
          "CLANG_CXX_LIBRARY": "libc++",
          "MACOSX_DEPLOYMENT_TARGET": "10.15"
        }
      }],
      ["OS=='win'", {
        "msvs_settings": {
          "VCCLCompilerTool": {
            "ExceptionHandling": 1
          }
        }
      }]
    ]
  }]
}
```

**CMakeLists.txt (cmake-js):**

```cmake
cmake_minimum_required(VERSION 3.15)
project(addon)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include cmake-js helpers
include_directories(${CMAKE_JS_INC})

# Include node-addon-api
execute_process(
    COMMAND node -p "require('node-addon-api').include"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    OUTPUT_VARIABLE NODE_ADDON_API_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
include_directories(${NODE_ADDON_API_DIR})

# Define N-API version
add_definitions(-DNAPI_VERSION=8)
add_definitions(-DNAPI_CPP_EXCEPTIONS)

# Source files
file(GLOB SOURCE_FILES "src/*.cc")

# Create library
add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES} ${CMAKE_JS_SRC})

# Set output name and extension
set_target_properties(${PROJECT_NAME} PROPERTIES
    PREFIX ""
    SUFFIX ".node"
)

# Link libraries
target_link_libraries(${PROJECT_NAME} ${CMAKE_JS_LIB})

# Platform-specific settings
if(MSVC)
    set(CMAKE_CXX_FLAGS_RELEASE "/EHsc /O2")
    target_compile_definitions(${PROJECT_NAME} PRIVATE _HAS_EXCEPTIONS=1)
endif()

if(APPLE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fexceptions")
endif()
```

---

### 6.2 Support Multiple Platforms

Write platform-aware code and configuration for Windows, macOS, and Linux compatibility.

**Platform-specific code:**

```cpp
#include <napi.h>

#ifdef _WIN32
    #include <windows.h>
    #define PATH_SEPARATOR '\\'
#else
    #include <unistd.h>
    #include <dlfcn.h>
    #define PATH_SEPARATOR '/'
#endif

class PlatformHelper {
public:
    static std::string GetHomeDirectory() {
        #ifdef _WIN32
        char* home = getenv("USERPROFILE");
        #else
        char* home = getenv("HOME");
        #endif
        return home ? home : "";
    }

    static void* LoadLibrary(const std::string& path) {
        #ifdef _WIN32
        return LoadLibraryA(path.c_str());
        #else
        return dlopen(path.c_str(), RTLD_LAZY);
        #endif
    }

    static void FreeLibrary(void* handle) {
        #ifdef _WIN32
        ::FreeLibrary(static_cast<HMODULE>(handle));
        #else
        dlclose(handle);
        #endif
    }

    static std::string GetLastErrorString() {
        #ifdef _WIN32
        DWORD error = GetLastError();
        if (error == 0) return "";

        LPSTR buffer = nullptr;
        FormatMessageA(
            FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
            nullptr, error, 0, (LPSTR)&buffer, 0, nullptr);

        std::string message(buffer);
        LocalFree(buffer);
        return message;
        #else
        return dlerror() ? dlerror() : "";
        #endif
    }
};
```

---

### 6.3 Use Prebuild for Distribution

Pre-compile binaries for common platforms to avoid requiring users to have build tools installed.

**package.json configuration:**

```json
{
  "name": "my-native-addon",
  "version": "1.0.0",
  "main": "lib/binding.js",
  "scripts": {
    "install": "prebuild-install || node-gyp rebuild",
    "build": "node-gyp rebuild",
    "prebuild": "prebuild --all --strip",
    "prebuild-upload": "prebuild --all --strip -u $GITHUB_TOKEN"
  },
  "dependencies": {
    "node-addon-api": "^7.0.0",
    "prebuild-install": "^7.1.0"
  },
  "devDependencies": {
    "node-gyp": "^10.0.0",
    "prebuild": "^12.0.0"
  },
  "binary": {
    "napi_versions": [8]
  }
}
```

**lib/binding.js (loader with fallback):**

```javascript
const path = require('path');

function loadBinding() {
    // Try prebuild first
    try {
        return require('prebuild-install/rc')(
            require('../package.json').name,
            { napi: true }
        );
    } catch (e) {
        // Fall back to local build
        try {
            return require('../build/Release/addon.node');
        } catch (e2) {
            try {
                return require('../build/Debug/addon.node');
            } catch (e3) {
                throw new Error(
                    'Native addon not found. Run `npm run build` to compile.'
                );
            }
        }
    }
}

module.exports = loadBinding();
```

---

### 6.4 Configure Compiler Warnings

Enable comprehensive warnings to catch issues early. Treat warnings as errors in CI.

**binding.gyp with warnings:**

```python
{
  "targets": [{
    "target_name": "addon",
    "sources": ["src/addon.cc"],
    "include_dirs": [
      "<!@(node -p \"require('node-addon-api').include\")"
    ],
    "cflags": [
      "-Wall",
      "-Wextra",
      "-Wpedantic",
      "-Wno-unused-parameter",
      "-Werror"
    ],
    "cflags_cc": [
      "-Wall",
      "-Wextra",
      "-Wpedantic",
      "-Wno-unused-parameter",
      "-Werror"
    ],
    "conditions": [
      ["OS=='mac'", {
        "xcode_settings": {
          "WARNING_CFLAGS": [
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-Wno-unused-parameter"
          ],
          "GCC_TREAT_WARNINGS_AS_ERRORS": "YES"
        }
      }],
      ["OS=='win'", {
        "msvs_settings": {
          "VCCLCompilerTool": {
            "WarningLevel": 4,
            "WarnAsError": "true",
            "DisableSpecificWarnings": ["4100"]
          }
        }
      }]
    ]
  }]
}
```

---

### 6.5 Handle Node.js Worker Threads

Ensure addon works correctly when loaded in Worker threads (multiple instances per process).

**Context-aware addon:**

```cpp
#include <napi.h>
#include <mutex>
#include <map>

// Per-instance state (supports Worker threads)
class AddonData {
public:
    static AddonData* Get(Napi::Env env) {
        void* data = nullptr;
        napi_get_instance_data(env, &data);
        return static_cast<AddonData*>(data);
    }

    int counter = 0;
    std::mutex mutex;
};

// Context-aware initialization
Napi::Object Init(Napi::Env env, Napi::Object exports) {
    // Create per-instance data
    auto* data = new AddonData();

    // Set instance data with destructor
    napi_set_instance_data(
        env,
        data,
        [](napi_env env, void* data, void* hint) {
            delete static_cast<AddonData*>(data);
        },
        nullptr
    );

    exports.Set("increment", Napi::Function::New(env, [](const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        AddonData* data = AddonData::Get(env);

        std::lock_guard<std::mutex> lock(data->mutex);
        data->counter++;

        return Napi::Number::New(env, data->counter);
    }));

    return exports;
}

// Use NAPI_MODULE_INIT for context-aware modules
NODE_API_MODULE(addon, Init)
```

**Testing with Worker threads:**

```javascript
// test-workers.js
const { Worker, isMainThread, parentPort } = require('worker_threads');
const addon = require('./build/Release/addon');

if (isMainThread) {
    // Main thread
    console.log('Main:', addon.increment());  // 1
    console.log('Main:', addon.increment());  // 2

    // Create worker
    const worker = new Worker(__filename);
    worker.on('message', (msg) => {
        console.log('Worker result:', msg);
    });
} else {
    // Worker thread - has its own addon instance
    const result1 = addon.increment();  // 1 (separate counter)
    const result2 = addon.increment();  // 2
    parentPort.postMessage({ result1, result2 });
}
```

---

## 7. Security & Input Validation

**Impact: LOW-MEDIUM**

Native addons can access system resources directly. Proper input validation prevents exploits and crashes.

### 7.1 Validate All JavaScript Inputs

Never trust JavaScript input. Validate types, ranges, and content before use in native code.

**Incorrect: No validation**

```cpp
Napi::Value UnsafeRead(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // No validation - crashes on wrong type, empty input, etc.
    std::string path = info[0].As<Napi::String>().Utf8Value();
    int offset = info[1].As<Napi::Number>().Int32Value();
    int length = info[2].As<Napi::Number>().Int32Value();

    return ReadFileChunk(env, path, offset, length);
}
```

**Correct: Comprehensive validation**

```cpp
Napi::Value SafeRead(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Validate argument count
    if (info.Length() < 3) {
        Napi::TypeError::New(env,
            "read requires 3 arguments: (path: string, offset: number, length: number)")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate path argument
    if (!info[0].IsString()) {
        Napi::TypeError::New(env, "path must be a string")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    std::string path = info[0].As<Napi::String>().Utf8Value();

    // Validate path content
    if (path.empty()) {
        Napi::RangeError::New(env, "path cannot be empty")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (path.find("..") != std::string::npos) {
        Napi::Error::New(env, "path cannot contain '..'")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate offset
    if (!info[1].IsNumber()) {
        Napi::TypeError::New(env, "offset must be a number")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    int64_t offset = info[1].As<Napi::Number>().Int64Value();
    if (offset < 0) {
        Napi::RangeError::New(env, "offset must be non-negative")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate length
    if (!info[2].IsNumber()) {
        Napi::TypeError::New(env, "length must be a number")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    int64_t length = info[2].As<Napi::Number>().Int64Value();
    if (length <= 0 || length > MAX_READ_LENGTH) {
        Napi::RangeError::New(env,
            "length must be between 1 and " + std::to_string(MAX_READ_LENGTH))
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    return ReadFileChunk(env, path, offset, static_cast<size_t>(length));
}
```

---

### 7.2 Prevent Buffer Overflows

Always check buffer bounds before reading or writing. Use safe functions and container types.

**Incorrect: Unbounded buffer operations**

```cpp
Napi::Value UnsafeCopy(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Buffer<char> src = info[0].As<Napi::Buffer<char>>();
    Napi::Buffer<char> dst = info[1].As<Napi::Buffer<char>>();
    size_t count = info[2].As<Napi::Number>().Uint32Value();

    // DANGER: No bounds check - may overflow dst!
    memcpy(dst.Data(), src.Data(), count);

    return env.Undefined();
}
```

**Correct: Bounds-checked operations**

```cpp
Napi::Value SafeCopy(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsBuffer() || !info[1].IsBuffer() || !info[2].IsNumber()) {
        Napi::TypeError::New(env, "Expected (Buffer, Buffer, number)")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Buffer<char> src = info[0].As<Napi::Buffer<char>>();
    Napi::Buffer<char> dst = info[1].As<Napi::Buffer<char>>();
    size_t count = info[2].As<Napi::Number>().Uint32Value();

    // Bounds checking
    if (count > src.Length()) {
        Napi::RangeError::New(env,
            "count (" + std::to_string(count) + ") exceeds source length (" +
            std::to_string(src.Length()) + ")")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (count > dst.Length()) {
        Napi::RangeError::New(env,
            "count (" + std::to_string(count) + ") exceeds destination length (" +
            std::to_string(dst.Length()) + ")")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Safe to copy
    memcpy(dst.Data(), src.Data(), count);

    return Napi::Number::New(env, count);
}
```

---

### 7.3 Sanitize String Inputs

Validate and sanitize string inputs before use in file paths, shell commands, or SQL queries.

**Incorrect: Unsanitized path**

```cpp
Napi::Value UnsafeOpen(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    std::string filename = info[0].As<Napi::String>().Utf8Value();

    // Path traversal vulnerability!
    // Input: "../../../etc/passwd" exposes system files
    std::string fullPath = basePath_ + "/" + filename;
    return OpenFile(env, fullPath);
}
```

**Correct: Sanitized and validated path**

```cpp
#include <filesystem>

Napi::Value SafeOpen(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsString()) {
        Napi::TypeError::New(env, "filename must be a string")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    std::string filename = info[0].As<Napi::String>().Utf8Value();

    // Reject obviously malicious patterns
    if (filename.find("..") != std::string::npos ||
        filename.find('\0') != std::string::npos ||
        filename[0] == '/' ||
        filename[0] == '\\') {
        Napi::Error::New(env, "Invalid filename")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Construct and canonicalize path
    std::filesystem::path basePath(basePath_);
    std::filesystem::path fullPath = basePath / filename;

    // Resolve to absolute path
    std::filesystem::path canonical;
    try {
        canonical = std::filesystem::weakly_canonical(fullPath);
    } catch (const std::exception& e) {
        Napi::Error::New(env, "Invalid path")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Verify path is still under base directory
    std::filesystem::path canonicalBase = std::filesystem::canonical(basePath);

    auto [baseEnd, pathIt] = std::mismatch(
        canonicalBase.begin(), canonicalBase.end(),
        canonical.begin(), canonical.end());

    if (baseEnd != canonicalBase.end()) {
        Napi::Error::New(env, "Path traversal detected")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    return OpenFile(env, canonical.string());
}
```

---

### 7.4 Handle Untrusted Data Safely

When processing data from untrusted sources (network, files), assume it may be malicious.

**Incorrect: Trusting input structure**

```cpp
struct Header {
    uint32_t version;
    uint32_t dataSize;
    uint32_t flags;
};

Napi::Value ParseUntrusted(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Buffer<uint8_t> data = info[0].As<Napi::Buffer<uint8_t>>();

    // Trust the header's claimed size - DANGEROUS!
    Header* header = reinterpret_cast<Header*>(data.Data());

    // Attacker can set dataSize to huge value
    std::vector<uint8_t> content(header->dataSize);  // OOM or overflow!
    memcpy(content.data(), data.Data() + sizeof(Header), header->dataSize);

    return ProcessContent(env, content);
}
```

**Correct: Defensive parsing**

```cpp
Napi::Value ParseUntrustedSafe(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsBuffer()) {
        Napi::TypeError::New(env, "Expected Buffer")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Buffer<uint8_t> data = info[0].As<Napi::Buffer<uint8_t>>();
    size_t bufferSize = data.Length();

    // Validate minimum size for header
    if (bufferSize < sizeof(Header)) {
        Napi::Error::New(env, "Buffer too small for header")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Read header fields individually (handles alignment)
    uint8_t* ptr = data.Data();
    uint32_t version, dataSize, flags;

    memcpy(&version, ptr, sizeof(version));
    memcpy(&dataSize, ptr + 4, sizeof(dataSize));
    memcpy(&flags, ptr + 8, sizeof(flags));

    // Validate version
    if (version > MAX_SUPPORTED_VERSION) {
        Napi::Error::New(env, "Unsupported version: " + std::to_string(version))
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate claimed size against actual buffer
    size_t headerSize = sizeof(Header);
    size_t availableData = bufferSize - headerSize;

    if (dataSize > availableData) {
        Napi::Error::New(env,
            "Claimed data size (" + std::to_string(dataSize) +
            ") exceeds available data (" + std::to_string(availableData) + ")")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate against maximum allowed size
    if (dataSize > MAX_DATA_SIZE) {
        Napi::Error::New(env, "Data size exceeds maximum allowed")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Now safe to process
    std::vector<uint8_t> content(ptr + headerSize, ptr + headerSize + dataSize);
    return ProcessContent(env, content);
}
```

---

### 7.5 Use Secure Memory for Sensitive Data

Clear sensitive data from memory after use. Prevent compiler optimizations from removing clearing code.

**Incorrect: Sensitive data lingers in memory**

```cpp
class UnsafeCredentials {
    std::string password_;

public:
    void SetPassword(const Napi::CallbackInfo& info) {
        password_ = info[0].As<Napi::String>().Utf8Value();
    }

    ~UnsafeCredentials() {
        // password_ memory may not be cleared
        // Could be recovered from memory dump
    }
};
```

**Correct: Secure memory handling**

```cpp
#include <cstring>

// Secure memory clearing that won't be optimized away
void SecureClear(void* ptr, size_t size) {
    volatile unsigned char* p = static_cast<volatile unsigned char*>(ptr);
    while (size--) {
        *p++ = 0;
    }
}

// Or use platform-specific secure functions
#ifdef _WIN32
#include <windows.h>
#define SecureZeroMemory(ptr, size) SecureZeroMemory(ptr, size)
#else
#include <string.h>
// explicit_bzero is available on most Unix systems
#define SecureZeroMemory(ptr, size) explicit_bzero(ptr, size)
#endif

class SecureCredentials {
    std::vector<char> password_;

public:
    void SetPassword(const Napi::CallbackInfo& info) {
        // Clear any existing password first
        ClearPassword();

        std::string temp = info[0].As<Napi::String>().Utf8Value();
        password_.assign(temp.begin(), temp.end());

        // Clear the temporary string
        SecureClear(temp.data(), temp.size());
    }

    bool Verify(const std::string& input) {
        if (input.size() != password_.size()) {
            return false;
        }

        // Constant-time comparison to prevent timing attacks
        int result = 0;
        for (size_t i = 0; i < password_.size(); i++) {
            result |= password_[i] ^ input[i];
        }
        return result == 0;
    }

    void ClearPassword() {
        if (!password_.empty()) {
            SecureClear(password_.data(), password_.size());
            password_.clear();
            password_.shrink_to_fit();
        }
    }

    ~SecureCredentials() {
        ClearPassword();
    }
};
```

---

## 8. Common Pitfalls & Anti-Patterns

**Impact: LOW**

These patterns cause subtle bugs that are difficult to debug. Avoiding them prevents hard-to-track issues.

### 8.1 Avoid Capturing Local Variables

Lambda captures of local variables become invalid when the enclosing function returns. Only capture by value or heap-allocated data.

**Incorrect: Capturing local by reference**

```cpp
Napi::Value StartTimer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    int intervalMs = info[0].As<Napi::Number>().Int32Value();
    std::string message = info[1].As<Napi::String>().Utf8Value();

    auto tsfn = Napi::ThreadSafeFunction::New(env, info[2].As<Napi::Function>(),
        "Timer", 0, 1);

    std::thread([&message, tsfn, intervalMs]() mutable {
        // BUG: 'message' reference is dangling after StartTimer returns!
        std::this_thread::sleep_for(std::chrono::milliseconds(intervalMs));

        tsfn.BlockingCall([&message](Napi::Env env, Napi::Function cb) {
            cb.Call({Napi::String::New(env, message)});  // CRASH!
        });

        tsfn.Release();
    }).detach();

    return env.Undefined();
}
```

**Correct: Capture by value or shared_ptr**

```cpp
Napi::Value StartTimer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    int intervalMs = info[0].As<Napi::Number>().Int32Value();

    // Copy the string for the lambda
    std::string message = info[1].As<Napi::String>().Utf8Value();

    auto tsfn = Napi::ThreadSafeFunction::New(env, info[2].As<Napi::Function>(),
        "Timer", 0, 1);

    // Capture message BY VALUE (makes a copy)
    std::thread([message, tsfn, intervalMs]() mutable {
        std::this_thread::sleep_for(std::chrono::milliseconds(intervalMs));

        // Capture by value again for inner lambda
        tsfn.BlockingCall([message](Napi::Env env, Napi::Function cb) {
            cb.Call({Napi::String::New(env, message)});  // Safe!
        });

        tsfn.Release();
    }).detach();

    return env.Undefined();
}

// Alternative: Use shared_ptr for large objects
Napi::Value StartTimerWithContext(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    struct Context {
        int intervalMs;
        std::string message;
        std::vector<uint8_t> largeData;  // Too expensive to copy
    };

    auto ctx = std::make_shared<Context>();
    ctx->intervalMs = info[0].As<Napi::Number>().Int32Value();
    ctx->message = info[1].As<Napi::String>().Utf8Value();
    // ... populate largeData

    auto tsfn = Napi::ThreadSafeFunction::New(env, info[2].As<Napi::Function>(),
        "Timer", 0, 1);

    std::thread([ctx, tsfn]() mutable {
        std::this_thread::sleep_for(std::chrono::milliseconds(ctx->intervalMs));

        tsfn.BlockingCall([ctx](Napi::Env env, Napi::Function cb) {
            cb.Call({Napi::String::New(env, ctx->message)});
        });

        tsfn.Release();
    }).detach();

    return env.Undefined();
}
```

---

### 8.2 Don't Store Env Long-Term

`Napi::Env` is only valid during a single call into the addon. Storing it for later use leads to undefined behavior.

**Incorrect: Storing env for later**

```cpp
class BadStore {
    Napi::Env storedEnv_;  // WRONG!

public:
    void Initialize(const Napi::CallbackInfo& info) {
        storedEnv_ = info.Env();  // Store for "later"
    }

    void UseLater() {
        // CRASH: storedEnv_ is invalid!
        Napi::String::New(storedEnv_, "hello");
    }
};
```

**Correct: Pass env to each method or use callbacks**

```cpp
class GoodStore {
public:
    // Option 1: Pass env each time
    Napi::Value DoSomething(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();  // Fresh env from callback
        return Napi::String::New(env, "hello");
    }

    // Option 2: Use ThreadSafeFunction for deferred work
    void ScheduleWork(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        tsfn_ = Napi::ThreadSafeFunction::New(
            env,
            info[0].As<Napi::Function>(),
            "GoodStore", 0, 1);

        // Later, when we need to call back into JS:
        tsfn_.BlockingCall([](Napi::Env env, Napi::Function callback) {
            // 'env' is valid here during the callback
            callback.Call({Napi::String::New(env, "result")});
        });
    }

private:
    Napi::ThreadSafeFunction tsfn_;
};
```

---

### 8.3 Handle Module Unload

Clean up resources when the addon is unloaded (e.g., worker thread termination). Use cleanup hooks.

**Incorrect: No cleanup**

```cpp
// Global resources that leak on unload
static std::thread* backgroundThread = nullptr;
static bool running = true;

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    backgroundThread = new std::thread([]() {
        while (running) {
            DoBackgroundWork();
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    });

    // Thread and 'running' flag never cleaned up!
    return exports;
}
```

**Correct: Register cleanup hooks**

```cpp
#define NAPI_VERSION 8
#include <napi.h>

struct AddonContext {
    std::thread* backgroundThread = nullptr;
    std::atomic<bool> running{true};
};

void CleanupHook(void* arg) {
    auto* ctx = static_cast<AddonContext*>(arg);

    // Signal thread to stop
    ctx->running = false;

    // Wait for thread to finish
    if (ctx->backgroundThread && ctx->backgroundThread->joinable()) {
        ctx->backgroundThread->join();
    }

    delete ctx->backgroundThread;
    delete ctx;
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    auto* ctx = new AddonContext();

    // Register cleanup hook
    napi_add_env_cleanup_hook(env, CleanupHook, ctx);

    // Store context for access
    napi_set_instance_data(env, ctx,
        [](napi_env env, void* data, void* hint) {
            // Instance destructor - called when env is destroyed
            // Our cleanup hook handles everything
        },
        nullptr);

    ctx->backgroundThread = new std::thread([ctx]() {
        while (ctx->running) {
            DoBackgroundWork();
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    });

    exports.Set("stop", Napi::Function::New(env, [](const Napi::CallbackInfo& info) {
        auto* ctx = static_cast<AddonContext*>(nullptr);
        napi_get_instance_data(info.Env(), reinterpret_cast<void**>(&ctx));

        if (ctx) {
            ctx->running = false;
        }

        return info.Env().Undefined();
    }));

    return exports;
}

NODE_API_MODULE(addon, Init)
```

---

### 8.4 Avoid Recursive N-API Calls

Calling JavaScript that calls back into the addon can cause stack overflow or deadlock. Design APIs to avoid recursion.

**Incorrect: Recursive callback pattern**

```cpp
class BadRecursive : public Napi::ObjectWrap<BadRecursive> {
    std::mutex mutex_;

public:
    Napi::Value Process(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        std::lock_guard<std::mutex> lock(mutex_);  // Lock acquired

        // Call JavaScript callback
        Napi::Function callback = info[0].As<Napi::Function>();
        callback.Call({});  // JS might call back into Process() - DEADLOCK!

        return env.Undefined();
    }
};
```

**Correct: Avoid holding locks during callbacks**

```cpp
class GoodNonRecursive : public Napi::ObjectWrap<GoodNonRecursive> {
    std::mutex mutex_;
    std::vector<int> data_;

public:
    Napi::Value Process(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        // Get data under lock
        std::vector<int> dataCopy;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            dataCopy = data_;  // Copy data
        }  // Lock released before callback

        // Call JavaScript callback without holding lock
        Napi::Function callback = info[0].As<Napi::Function>();

        for (int item : dataCopy) {
            Napi::Value result = callback.Call({Napi::Number::New(env, item)});

            // Check for exception
            if (env.IsExceptionPending()) {
                return env.Undefined();
            }

            // Process result...
        }

        return env.Undefined();
    }

    // Alternative: Use async pattern to break call chain
    Napi::Value ProcessAsync(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        Napi::Function callback = info[0].As<Napi::Function>();

        // Schedule callback via setImmediate to break recursion
        Napi::Function setImmediate = env.Global()
            .Get("setImmediate").As<Napi::Function>();

        setImmediate.Call({callback});

        return env.Undefined();
    }
};
```

---

### 8.5 Test Across Node Versions

Test your addon on multiple Node.js versions to catch compatibility issues early. Use CI matrices.

**GitHub Actions workflow:**

```yaml
# .github/workflows/test.yml
name: Test Native Addon

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node: [18, 20, 22]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}

      - name: Install dependencies
        run: npm ci

      - name: Build addon
        run: npm run build

      - name: Run tests
        run: npm test

      - name: Test in worker thread
        run: node test/worker-test.js

  # Test N-API version compatibility
  napi-versions:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        napi-version: [6, 7, 8, 9]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Build with N-API ${{ matrix.napi-version }}
        run: |
          npm ci
          npx node-gyp rebuild --napi_version=${{ matrix.napi-version }}

      - name: Test
        run: npm test
```

**Local testing script:**

```javascript
// test/version-check.js
const addon = require('../');
const assert = require('assert');

// Check addon reports correct N-API version
assert(addon.napiVersion >= 8,
    `Expected N-API version >= 8, got ${addon.napiVersion}`);

// Test basic functionality
assert.strictEqual(addon.hello(), 'world');

// Test in worker thread
const { Worker, isMainThread, parentPort } = require('worker_threads');

if (isMainThread) {
    const worker = new Worker(__filename);

    worker.on('message', (msg) => {
        assert.strictEqual(msg.success, true, 'Worker test failed');
        console.log('All tests passed!');
    });

    worker.on('error', (err) => {
        console.error('Worker error:', err);
        process.exit(1);
    });
} else {
    try {
        const result = addon.hello();
        parentPort.postMessage({ success: result === 'world' });
    } catch (e) {
        parentPort.postMessage({ success: false, error: e.message });
    }
}
```

---

## References

### Official Documentation

- [Node-API Documentation](https://nodejs.org/api/n-api.html) - Official Node.js N-API reference
- [node-addon-api Documentation](https://github.com/nodejs/node-addon-api) - C++ wrapper documentation
- [Node-API Version History](https://nodejs.org/api/n-api.html#node-api-version-matrix) - N-API version compatibility matrix

### Guides and Tutorials

- [Node.js Native Modules](https://nodejs.org/api/addons.html) - Node.js addons overview
- [N-API Resource](https://napi.inspiredware.com/) - Community N-API guides and examples
- [Building Node.js Addons](https://github.com/nicklockwood/node-native-addons-guide) - Comprehensive tutorial

### Build Tools

- [node-gyp](https://github.com/nodejs/node-gyp) - Node.js native addon build tool
- [cmake-js](https://github.com/nicklockwood/cmake-js) - CMake-based build tool for Node.js addons
- [prebuild](https://github.com/prebuild/prebuild) - Build and distribute prebuilt binaries

### Example Projects

- [node-addon-examples](https://github.com/nodejs/node-addon-examples) - Official example collection
- [node-sqlite3](https://github.com/TryGhost/node-sqlite3) - Production native addon example
- [sharp](https://github.com/lovell/sharp) - High-performance image processing addon

---

## Changelog

### Version 0.1.0 (January 2026)

- Initial release with 46 rules across 8 categories
- Comprehensive coverage of N-API, memory management, threading, and security
- Production-ready code examples for all rules
