---
title: Sanitize External Input
impact: LOW-MEDIUM
impactDescription: Prevents injection attacks and undefined behavior from malformed data
tags: security, input-validation, sanitization, defense-in-depth, untrusted
---

# Sanitize External Input

Treat all JavaScript inputs as untrusted. Validate types, ranges, and sizes explicitly. Never assume callers provide well-formed data.

## Why This Matters

- JavaScript is dynamically typed; any value can be passed
- Malicious or buggy callers may provide unexpected types
- Type coercion can produce surprising results
- Defense in depth protects against upstream bugs

## Incorrect

Trusting type assertions without validation:

```cpp
#include <napi.h>
#include <cmath>

// BAD: Assumes inputs are correct types and valid ranges
Napi::Value CalculatePower(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Blindly trust that arguments are numbers
    double base = info[0].As<Napi::Number>().DoubleValue();
    double exponent = info[1].As<Napi::Number>().DoubleValue();

    // Could produce NaN, Infinity, or domain errors
    return Napi::Number::New(env, std::pow(base, exponent));
}

// BAD: No validation of callback function
Napi::Value ProcessWithCallback(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Array data = info[0].As<Napi::Array>();
    // Assumes this is a function - will crash if not
    Napi::Function callback = info[1].As<Napi::Function>();

    for (uint32_t i = 0; i < data.Length(); i++) {
        callback.Call({data.Get(i)});
    }

    return env.Undefined();
}

// BAD: No validation of object properties
Napi::Value ProcessConfig(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Object config = info[0].As<Napi::Object>();

    // Assumes properties exist and are correct types
    int port = config.Get("port").As<Napi::Number>().Int32Value();
    std::string host = config.Get("host").As<Napi::String>().Utf8Value();

    return env.Undefined();
}
```

## Correct

Validate types, ranges, and values explicitly:

```cpp
#include <napi.h>
#include <cmath>
#include <limits>

// GOOD: Complete input validation
Napi::Value SafeCalculatePower(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Validate argument count
    if (info.Length() < 2) {
        Napi::TypeError::New(env, "Expected 2 arguments: base, exponent")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate argument types
    if (!info[0].IsNumber() || !info[1].IsNumber()) {
        Napi::TypeError::New(env, "Both arguments must be numbers")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    double base = info[0].As<Napi::Number>().DoubleValue();
    double exponent = info[1].As<Napi::Number>().DoubleValue();

    // Validate for NaN
    if (std::isnan(base) || std::isnan(exponent)) {
        Napi::RangeError::New(env, "Arguments cannot be NaN")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate for infinity
    if (std::isinf(base) || std::isinf(exponent)) {
        Napi::RangeError::New(env, "Arguments cannot be Infinity")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Domain validation for pow()
    if (base < 0 && std::floor(exponent) != exponent) {
        Napi::RangeError::New(env,
            "Negative base with non-integer exponent is undefined")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    double result = std::pow(base, exponent);

    // Validate result
    if (std::isnan(result) || std::isinf(result)) {
        Napi::RangeError::New(env, "Result overflow or undefined")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    return Napi::Number::New(env, result);
}

// GOOD: Validate callback is actually a function
Napi::Value SafeProcessWithCallback(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 2) {
        Napi::TypeError::New(env, "Expected (array, callback)")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (!info[0].IsArray()) {
        Napi::TypeError::New(env, "First argument must be an array")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (!info[1].IsFunction()) {
        Napi::TypeError::New(env, "Second argument must be a function")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Array data = info[0].As<Napi::Array>();
    Napi::Function callback = info[1].As<Napi::Function>();
    uint32_t length = data.Length();

    // Limit iteration count to prevent DoS
    const uint32_t MAX_ITERATIONS = 1000000;
    if (length > MAX_ITERATIONS) {
        Napi::RangeError::New(env,
            "Array too large (max " + std::to_string(MAX_ITERATIONS) + ")")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    for (uint32_t i = 0; i < length; i++) {
        callback.Call(env.Global(), {data.Get(i)});

        // Check for pending exception after each call
        if (env.IsExceptionPending()) {
            return env.Undefined();
        }
    }

    return env.Undefined();
}

// GOOD: Validate object structure with defaults
Napi::Value SafeProcessConfig(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 1 || !info[0].IsObject()) {
        Napi::TypeError::New(env, "Expected configuration object")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Object config = info[0].As<Napi::Object>();

    // Safe property extraction with validation
    int port = 8080;  // Default
    if (config.Has("port")) {
        Napi::Value portVal = config.Get("port");
        if (!portVal.IsNumber()) {
            Napi::TypeError::New(env, "port must be a number")
                .ThrowAsJavaScriptException();
            return env.Undefined();
        }
        port = portVal.As<Napi::Number>().Int32Value();

        // Validate port range
        if (port < 0 || port > 65535) {
            Napi::RangeError::New(env, "port must be 0-65535")
                .ThrowAsJavaScriptException();
            return env.Undefined();
        }
    }

    std::string host = "localhost";  // Default
    if (config.Has("host")) {
        Napi::Value hostVal = config.Get("host");
        if (!hostVal.IsString()) {
            Napi::TypeError::New(env, "host must be a string")
                .ThrowAsJavaScriptException();
            return env.Undefined();
        }
        host = hostVal.As<Napi::String>().Utf8Value();

        // Validate host length
        if (host.empty() || host.length() > 253) {
            Napi::RangeError::New(env, "host must be 1-253 characters")
                .ThrowAsJavaScriptException();
            return env.Undefined();
        }
    }

    Napi::Object result = Napi::Object::New(env);
    result.Set("port", port);
    result.Set("host", host);
    return result;
}
```

## Input Validation Helper

```cpp
#include <napi.h>
#include <string>

class InputValidator {
public:
    explicit InputValidator(const Napi::CallbackInfo& info)
        : env_(info.Env()), info_(info), valid_(true) {}

    InputValidator& requireArgCount(size_t min, size_t max = SIZE_MAX) {
        if (!valid_) return *this;

        if (info_.Length() < min) {
            setError("Expected at least " + std::to_string(min) + " arguments");
        } else if (info_.Length() > max) {
            setError("Expected at most " + std::to_string(max) + " arguments");
        }
        return *this;
    }

    InputValidator& requireNumber(size_t index, const char* name) {
        if (!valid_ || index >= info_.Length()) return *this;

        if (!info_[index].IsNumber()) {
            setError(std::string(name) + " must be a number");
        }
        return *this;
    }

    InputValidator& requireString(size_t index, const char* name) {
        if (!valid_ || index >= info_.Length()) return *this;

        if (!info_[index].IsString()) {
            setError(std::string(name) + " must be a string");
        }
        return *this;
    }

    InputValidator& requireBuffer(size_t index, const char* name) {
        if (!valid_ || index >= info_.Length()) return *this;

        if (!info_[index].IsBuffer()) {
            setError(std::string(name) + " must be a Buffer");
        }
        return *this;
    }

    bool isValid() const { return valid_; }

    void throwIfInvalid() {
        if (!valid_) {
            Napi::TypeError::New(env_, error_).ThrowAsJavaScriptException();
        }
    }

private:
    void setError(const std::string& msg) {
        valid_ = false;
        error_ = msg;
    }

    Napi::Env env_;
    const Napi::CallbackInfo& info_;
    bool valid_;
    std::string error_;
};

// Usage
Napi::Value Example(const Napi::CallbackInfo& info) {
    InputValidator validator(info);
    validator
        .requireArgCount(2)
        .requireString(0, "name")
        .requireNumber(1, "age");

    if (!validator.isValid()) {
        validator.throwIfInvalid();
        return info.Env().Undefined();
    }

    // Process validated inputs...
    return info.Env().Undefined();
}
```
