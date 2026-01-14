---
title: Return Immediately After Throwing Exceptions
impact: MEDIUM-HIGH
impactDescription: Prevents undefined behavior from using invalid state post-exception
tags: error, return, throw, control-flow
---

## Return Immediately After Throwing Exceptions

After throwing a JavaScript exception (via `ThrowAsJavaScriptException()` or setting an error), you must return immediately. Continuing execution with pending exceptions leads to undefined behavior, as the JavaScript engine expects control to return.

**Incorrect (continuing after throw):**

```cpp
#include <napi.h>

Napi::Value ProcessFile(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    std::string filename = info[0].As<Napi::String>().Utf8Value();

    FILE* file = fopen(filename.c_str(), "r");
    if (!file) {
        // WRONG: Throwing but not returning!
        Napi::Error::New(env, "Failed to open file")
            .ThrowAsJavaScriptException();
        // Code continues executing with file == nullptr!
    }

    // CRASH: Dereferencing null pointer
    char buffer[1024];
    fread(buffer, 1, sizeof(buffer), file);
    fclose(file);

    return Napi::String::New(env, buffer);
}

Napi::Value ValidateAndProcess(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsObject()) {
        Napi::TypeError::New(env, "Expected object")
            .ThrowAsJavaScriptException();
        // WRONG: Falling through to next check!
    }

    // This code runs even after exception is thrown!
    if (!info[1].IsFunction()) {
        // Now we have TWO pending exceptions - undefined behavior!
        Napi::TypeError::New(env, "Expected function")
            .ThrowAsJavaScriptException();
    }

    // Even more code running with pending exceptions...
    Napi::Object obj = info[0].As<Napi::Object>();  // May crash!
    return obj;
}
```

**Correct (return immediately after throw):**

```cpp
#include <napi.h>
#include <cstdio>

Napi::Value ProcessFile(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 1 || !info[0].IsString()) {
        Napi::TypeError::New(env, "Expected filename string")
            .ThrowAsJavaScriptException();
        return env.Undefined();  // CORRECT: Return immediately!
    }

    std::string filename = info[0].As<Napi::String>().Utf8Value();

    FILE* file = fopen(filename.c_str(), "r");
    if (!file) {
        Napi::Error::New(env,
            "Failed to open file: " + filename)
            .ThrowAsJavaScriptException();
        return env.Undefined();  // CORRECT: Return immediately!
    }

    // Now we know file is valid
    char buffer[1024];
    size_t bytesRead = fread(buffer, 1, sizeof(buffer) - 1, file);
    buffer[bytesRead] = '\0';
    fclose(file);

    return Napi::String::New(env, buffer);
}

// Pattern: Early return validation
Napi::Value ValidateAndProcess(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Validate all inputs first with early returns
    if (info.Length() < 2) {
        Napi::TypeError::New(env, "Expected 2 arguments")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (!info[0].IsObject()) {
        Napi::TypeError::New(env, "First argument must be object")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (!info[1].IsFunction()) {
        Napi::TypeError::New(env, "Second argument must be function")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // All validation passed - safe to proceed
    Napi::Object obj = info[0].As<Napi::Object>();
    Napi::Function callback = info[1].As<Napi::Function>();

    // Process...
    return callback.Call({obj});
}
```

**Pattern: Using exceptions mode (cleaner):**

```cpp
// With exceptions enabled, throw handles the return automatically
Napi::Value ProcessFileClean(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // With exceptions, this automatically returns if type mismatch
    std::string filename = info[0].As<Napi::String>().Utf8Value();

    FILE* file = fopen(filename.c_str(), "r");
    if (!file) {
        // throw automatically unwinds and returns
        throw Napi::Error::New(env, "Failed to open file: " + filename);
    }

    // RAII ensures cleanup even if exception thrown later
    struct FileGuard {
        FILE* f;
        ~FileGuard() { if (f) fclose(f); }
    } guard{file};

    char buffer[1024];
    size_t bytesRead = fread(buffer, 1, sizeof(buffer) - 1, file);
    buffer[bytesRead] = '\0';

    return Napi::String::New(env, buffer);
}
```

**Pattern: Consistent return values:**

```cpp
// When returning after error, be consistent with return type
Napi::Value GetItem(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsNumber()) {
        Napi::TypeError::New(env, "Index must be number")
            .ThrowAsJavaScriptException();
        return env.Undefined();  // Use Undefined for errors
    }

    int index = info[0].As<Napi::Number>().Int32Value();

    if (index < 0 || index >= items_.size()) {
        Napi::RangeError::New(env, "Index out of bounds")
            .ThrowAsJavaScriptException();
        return env.Undefined();  // Consistent with above
    }

    return Napi::String::New(env, items_[index]);
}

// For nullable returns, use Null for "not found" vs Undefined for "error"
Napi::Value FindItem(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsString()) {
        Napi::TypeError::New(env, "Key must be string")
            .ThrowAsJavaScriptException();
        return env.Undefined();  // Error case
    }

    std::string key = info[0].As<Napi::String>().Utf8Value();

    auto it = map_.find(key);
    if (it == map_.end()) {
        return env.Null();  // Not found (not an error)
    }

    return Napi::String::New(env, it->second);
}
```

Reference: [Error Handling Best Practices](https://github.com/nodejs/node-addon-api/blob/main/doc/error_handling.md)
