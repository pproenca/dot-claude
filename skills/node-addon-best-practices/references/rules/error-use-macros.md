---
title: Use NAPI_THROW Macros for Consistent Error Propagation
impact: MEDIUM-HIGH
impactDescription: Standardizes error handling, works in both exception modes
tags: error, macros, throw, consistency
---

## Use NAPI_THROW Macros for Consistent Error Propagation

node-addon-api provides `NAPI_THROW*` macros that work correctly in both exception and non-exception modes. Use these instead of manual throw/return patterns for consistent, portable error handling.

**Incorrect (inconsistent error handling):**

```cpp
#include <napi.h>

Napi::Value ValidateInput(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Inconsistent: Sometimes throwing, sometimes returning
    if (info.Length() < 2) {
        // This only works with exceptions enabled!
        throw Napi::TypeError::New(env, "Expected 2 arguments");
    }

    if (!info[0].IsString()) {
        // This only works with exceptions disabled!
        Napi::TypeError::New(env, "First arg must be string")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Mixed patterns - hard to maintain
    if (!info[1].IsNumber()) {
        Napi::Error::New(env, "Second arg must be number")
            .ThrowAsJavaScriptException();
        return env.Null();  // Inconsistent return value!
    }

    return env.Undefined();
}
```

**Correct (using NAPI_THROW macros):**

```cpp
#include <napi.h>

// These macros work in both exception modes!

Napi::Value ValidateInput(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // NAPI_THROW_IF_FAILED - use after operations that can fail
    // Works correctly whether exceptions are enabled or not

    if (info.Length() < 2) {
        // For void returns or when you want to return undefined
        NAPI_THROW(Napi::TypeError::New(env, "Expected 2 arguments"),
                   env.Undefined());
    }

    if (!info[0].IsString()) {
        NAPI_THROW(Napi::TypeError::New(env, "First arg must be string"),
                   env.Undefined());
    }

    if (!info[1].IsNumber()) {
        NAPI_THROW(Napi::TypeError::New(env, "Second arg must be number"),
                   env.Undefined());
    }

    std::string name = info[0].As<Napi::String>().Utf8Value();
    int32_t value = info[1].As<Napi::Number>().Int32Value();

    return Napi::String::New(env, name + "=" + std::to_string(value));
}

// For methods that return void
void SetValue(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 1) {
        // NAPI_THROW_VOID for void functions
        NAPI_THROW_VOID(Napi::TypeError::New(env, "Expected 1 argument"));
    }

    // Process...
}
```

**Define your own domain-specific macros:**

```cpp
#include <napi.h>

// Custom validation macros for common patterns
#define NAPI_REQUIRE_ARGS(info, count) \
    do { \
        if ((info).Length() < (count)) { \
            NAPI_THROW(Napi::TypeError::New((info).Env(), \
                "Expected " #count " arguments, got " + \
                std::to_string((info).Length())), \
                (info).Env().Undefined()); \
        } \
    } while (0)

#define NAPI_REQUIRE_STRING(info, index, name) \
    do { \
        if (!(info)[(index)].IsString()) { \
            NAPI_THROW(Napi::TypeError::New((info).Env(), \
                #name " must be a string"), \
                (info).Env().Undefined()); \
        } \
    } while (0)

#define NAPI_REQUIRE_NUMBER(info, index, name) \
    do { \
        if (!(info)[(index)].IsNumber()) { \
            NAPI_THROW(Napi::TypeError::New((info).Env(), \
                #name " must be a number"), \
                (info).Env().Undefined()); \
        } \
    } while (0)

#define NAPI_REQUIRE_OBJECT(info, index, name) \
    do { \
        if (!(info)[(index)].IsObject()) { \
            NAPI_THROW(Napi::TypeError::New((info).Env(), \
                #name " must be an object"), \
                (info).Env().Undefined()); \
        } \
    } while (0)

#define NAPI_REQUIRE_FUNCTION(info, index, name) \
    do { \
        if (!(info)[(index)].IsFunction()) { \
            NAPI_THROW(Napi::TypeError::New((info).Env(), \
                #name " must be a function"), \
                (info).Env().Undefined()); \
        } \
    } while (0)

// Clean validation with custom macros
Napi::Value ConnectDatabase(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    NAPI_REQUIRE_ARGS(info, 3);
    NAPI_REQUIRE_STRING(info, 0, host);
    NAPI_REQUIRE_NUMBER(info, 1, port);
    NAPI_REQUIRE_OBJECT(info, 2, options);

    std::string host = info[0].As<Napi::String>().Utf8Value();
    int port = info[1].As<Napi::Number>().Int32Value();
    Napi::Object options = info[2].As<Napi::Object>();

    // Continue with valid arguments...
    return env.Undefined();
}

// Range validation macro
#define NAPI_REQUIRE_RANGE(env, value, min, max, name) \
    do { \
        if ((value) < (min) || (value) > (max)) { \
            NAPI_THROW(Napi::RangeError::New((env), \
                #name " must be between " #min " and " #max), \
                (env).Undefined()); \
        } \
    } while (0)

Napi::Value SetPort(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    NAPI_REQUIRE_ARGS(info, 1);
    NAPI_REQUIRE_NUMBER(info, 0, port);

    int port = info[0].As<Napi::Number>().Int32Value();
    NAPI_REQUIRE_RANGE(env, port, 1, 65535, port);

    // Port is valid...
    return env.Undefined();
}
```

Reference: [NAPI_THROW Macros](https://github.com/nodejs/node-addon-api/blob/main/napi.h)
