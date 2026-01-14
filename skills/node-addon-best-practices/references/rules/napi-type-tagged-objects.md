---
title: Use Type-Tagged Objects for Safe Native Casting
impact: CRITICAL
impactDescription: Prevents type confusion attacks and crashes from invalid casts
tags: napi, type-safety, security, casting
---

# Use Type-Tagged Objects for Safe Native Casting

Type tags provide runtime type verification for JavaScript objects that wrap native C++ instances. Without type tags, malicious or buggy code can pass arbitrary objects to native functions expecting specific wrapper types, causing crashes or security vulnerabilities.

## Why This Matters

- **Security**: Prevents type confusion attacks where attackers pass fake objects
- **Crash Prevention**: Catches invalid casts before they cause segfaults
- **Debugging**: Clear error messages instead of mysterious crashes
- **Robustness**: Protects against accidental misuse in complex codebases

## The Problem: Type Confusion

```javascript
// JavaScript attack/bug scenario
const addon = require('./addon');

// Create legitimate object
const realObj = new addon.SecureData('secret');

// Attacker creates fake object mimicking the wrapper
const fakeObj = { getValue: () => 'hacked' };
Object.setPrototypeOf(fakeObj, addon.SecureData.prototype);

// Without type tags, native code accepts the fake object
addon.processData(fakeObj);  // CRASH or security vulnerability!
```

## Incorrect: Unchecked Unwrap

```cpp
// BAD: No type verification - vulnerable to type confusion
#define NAPI_VERSION 8
#include <napi.h>

class SecureData : public Napi::ObjectWrap<SecureData> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "SecureData", {
            InstanceMethod("getValue", &SecureData::GetValue)
        });

        constructor = Napi::Persistent(func);
        constructor.SuppressDestruct();
        exports.Set("SecureData", func);
        return exports;
    }

    SecureData(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<SecureData>(info) {
        if (info.Length() > 0 && info[0].IsString()) {
            data_ = info[0].As<Napi::String>().Utf8Value();
        }
    }

    static Napi::FunctionReference constructor;

private:
    Napi::Value GetValue(const Napi::CallbackInfo& info) {
        return Napi::String::New(info.Env(), data_);
    }

    std::string data_;
};

// BAD: Vulnerable function that accepts any object
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // DANGEROUS: Unwrap without type verification
    // If info[0] is a fake object, this causes undefined behavior
    SecureData* obj = Napi::ObjectWrap<SecureData>::Unwrap(info[0].As<Napi::Object>());

    // Access member on potentially invalid pointer
    return obj->GetValue(info);  // CRASH or security hole
}
```

## Correct: Type-Tagged Objects (N-API v8+)

```cpp
// GOOD: Type-tagged objects prevent type confusion
#define NAPI_VERSION 8
#include <napi.h>

// Unique type tag - use UUID or random 128-bit value
static const napi_type_tag SecureDataTypeTag = {
    0xa1b2c3d4e5f60718ULL,  // Lower 64 bits
    0x9abcdef012345678ULL   // Upper 64 bits
};

class SecureData : public Napi::ObjectWrap<SecureData> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "SecureData", {
            InstanceMethod("getValue", &SecureData::GetValue)
        });

        constructor = Napi::Persistent(func);
        constructor.SuppressDestruct();
        exports.Set("SecureData", func);

        return exports;
    }

    SecureData(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<SecureData>(info) {

        // Tag the instance when created
        napi_type_tag_object(info.Env(), info.This(), &SecureDataTypeTag);

        if (info.Length() > 0 && info[0].IsString()) {
            data_ = info[0].As<Napi::String>().Utf8Value();
        }
    }

    // Safe unwrap with type verification
    static SecureData* SafeUnwrap(Napi::Env env, Napi::Value value) {
        if (!value.IsObject()) {
            return nullptr;
        }

        Napi::Object obj = value.As<Napi::Object>();

        // Verify the type tag
        bool isType = false;
        napi_status status = napi_check_object_type_tag(env, obj, &SecureDataTypeTag, &isType);

        if (status != napi_ok || !isType) {
            return nullptr;  // Not a valid SecureData instance
        }

        return Napi::ObjectWrap<SecureData>::Unwrap(obj);
    }

    const std::string& GetData() const { return data_; }

    static Napi::FunctionReference constructor;

private:
    Napi::Value GetValue(const Napi::CallbackInfo& info) {
        return Napi::String::New(info.Env(), data_);
    }

    std::string data_;
};

Napi::FunctionReference SecureData::constructor;

// GOOD: Safe function using type verification
Napi::Value ProcessData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 1) {
        Napi::TypeError::New(env, "Expected SecureData object").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Safe unwrap with type checking
    SecureData* obj = SecureData::SafeUnwrap(env, info[0]);

    if (obj == nullptr) {
        Napi::TypeError::New(env, "Invalid SecureData object").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Now safe to access the native object
    return Napi::String::New(env, "Processed: " + obj->GetData());
}
```

## Correct: Multiple Type Tags for Type Hierarchy

```cpp
// GOOD: Different tags for different native types
#define NAPI_VERSION 8
#include <napi.h>

static const napi_type_tag BufferTypeTag = {0x1111111111111111ULL, 0x1111111111111111ULL};
static const napi_type_tag ImageTypeTag = {0x2222222222222222ULL, 0x2222222222222222ULL};
static const napi_type_tag AudioTypeTag = {0x3333333333333333ULL, 0x3333333333333333ULL};

class NativeBuffer : public Napi::ObjectWrap<NativeBuffer> {
public:
    NativeBuffer(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<NativeBuffer>(info) {
        napi_type_tag_object(info.Env(), info.This(), &BufferTypeTag);
    }

    static bool CheckType(Napi::Env env, Napi::Value value) {
        if (!value.IsObject()) return false;
        bool isType = false;
        napi_check_object_type_tag(env, value.As<Napi::Object>(), &BufferTypeTag, &isType);
        return isType;
    }
};

class Image : public Napi::ObjectWrap<Image> {
public:
    Image(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<Image>(info) {
        napi_type_tag_object(info.Env(), info.This(), &ImageTypeTag);
    }

    static bool CheckType(Napi::Env env, Napi::Value value) {
        if (!value.IsObject()) return false;
        bool isType = false;
        napi_check_object_type_tag(env, value.As<Napi::Object>(), &ImageTypeTag, &isType);
        return isType;
    }
};

// Safe processing that dispatches by type
Napi::Value ProcessAny(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Value arg = info[0];

    if (NativeBuffer::CheckType(env, arg)) {
        auto* buffer = Napi::ObjectWrap<NativeBuffer>::Unwrap(arg.As<Napi::Object>());
        return Napi::String::New(env, "Processed buffer");
    }

    if (Image::CheckType(env, arg)) {
        auto* image = Napi::ObjectWrap<Image>::Unwrap(arg.As<Napi::Object>());
        return Napi::String::New(env, "Processed image");
    }

    Napi::TypeError::New(env, "Expected NativeBuffer or Image").ThrowAsJavaScriptException();
    return env.Undefined();
}
```

## Type Tag Generation Guidelines

1. **Use UUIDs or random values** - Never use predictable patterns
2. **Different tag per class** - Each native type needs unique tag
3. **Include in version control** - Tags are part of ABI contract
4. **Consider versioning** - Change tags when class layout changes significantly

```cpp
// Generate type tags using uuidgen or similar tool
// Example: uuidgen → "550e8400-e29b-41d4-a716-446655440000"
static const napi_type_tag MyTypeTag = {
    0x550e8400e29b41d4ULL,
    0xa716446655440000ULL
};
```
