---
title: Enable C++ Exceptions for Cleaner Error Handling
impact: MEDIUM-HIGH
impactDescription: Reduces boilerplate by 50%, provides stack-unwinding for RAII
tags: error, exceptions, configuration, binding-gyp
---

## Enable C++ Exceptions for Cleaner Error Handling

node-addon-api supports two error handling modes: C++ exceptions (default) or return-value checking. Enable exceptions for cleaner code, automatic stack unwinding, and proper RAII behavior. Set `NAPI_DISABLE_CPP_EXCEPTIONS` only when exceptions are prohibited by your project.

**Incorrect (verbose status checking without exceptions):**

```cpp
// With NAPI_DISABLE_CPP_EXCEPTIONS defined
#include <napi.h>

Napi::Value ParseConfig(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Must check every operation manually
    if (info.Length() < 1) {
        Napi::TypeError::New(env, "Expected 1 argument").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (!info[0].IsObject()) {
        Napi::TypeError::New(env, "Expected object").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Object config = info[0].As<Napi::Object>();

    // Every property access needs checking
    Napi::Value hostVal = config.Get("host");
    if (env.IsExceptionPending()) {
        return env.Undefined();
    }
    if (!hostVal.IsString()) {
        Napi::TypeError::New(env, "host must be string").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Value portVal = config.Get("port");
    if (env.IsExceptionPending()) {
        return env.Undefined();
    }
    if (!portVal.IsNumber()) {
        Napi::TypeError::New(env, "port must be number").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // ... continues for every operation
    return env.Undefined();
}
```

**Correct (clean exception-based handling):**

```cpp
// binding.gyp: DO NOT define NAPI_DISABLE_CPP_EXCEPTIONS
// Or explicitly enable: 'cflags!': [ '-fno-exceptions' ]
#include <napi.h>

Napi::Value ParseConfig(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Exceptions propagate automatically - clean code!
    Napi::Object config = info[0].As<Napi::Object>();

    std::string host = config.Get("host").As<Napi::String>().Utf8Value();
    int port = config.Get("port").As<Napi::Number>().Int32Value();
    bool useTls = config.Get("tls").As<Napi::Boolean>().Value();

    // If any of the above fails, a Napi::Error is thrown
    // and automatically converted to a JavaScript exception

    return Napi::String::New(env,
        "Connecting to " + host + ":" + std::to_string(port));
}
```

**binding.gyp configuration:**

```python
# Correct - exceptions enabled (default)
{
    "targets": [{
        "target_name": "addon",
        "sources": ["src/addon.cpp"],
        "include_dirs": [
            "<!@(node -p \"require('node-addon-api').include\")"
        ],
        "dependencies": [
            "<!(node -p \"require('node-addon-api').gyp\")"
        ],
        # Ensure exceptions are enabled (GCC/Clang)
        "cflags!": ["-fno-exceptions"],
        "cflags_cc!": ["-fno-exceptions"],
        # For MSVC
        "msvs_settings": {
            "VCCLCompilerTool": {
                "ExceptionHandling": 1
            }
        },
        # For macOS
        "xcode_settings": {
            "GCC_ENABLE_CPP_EXCEPTIONS": "YES",
            "CLANG_CXX_LIBRARY": "libc++",
            "MACOSX_DEPLOYMENT_TARGET": "10.15"
        }
    }]
}

# If you MUST disable exceptions (rare):
{
    "targets": [{
        "target_name": "addon",
        "defines": ["NAPI_DISABLE_CPP_EXCEPTIONS"],
        # ... rest of config
    }]
}
```

**Custom exception types:**

```cpp
// Define domain-specific exceptions for better error messages
class ConfigurationError : public Napi::Error {
public:
    static ConfigurationError New(Napi::Env env, const std::string& message) {
        return ConfigurationError(env, message);
    }

private:
    ConfigurationError(Napi::Env env, const std::string& message)
        : Napi::Error(Error::New(env,
            "ConfigurationError: " + message)) {}
};

Napi::Value ValidateConfig(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Object config = info[0].As<Napi::Object>();

    int port = config.Get("port").As<Napi::Number>().Int32Value();
    if (port < 1 || port > 65535) {
        throw ConfigurationError::New(env,
            "Port must be between 1 and 65535, got " + std::to_string(port));
    }

    return env.Undefined();
}
```

Reference: [node-addon-api Error Handling](https://github.com/nodejs/node-addon-api/blob/main/doc/error_handling.md)
