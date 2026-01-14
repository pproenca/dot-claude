---
title: Define NAPI_VERSION Early
impact: CRITICAL
impactDescription: Missing version definition causes API unavailability or undefined behavior
tags: napi, version, configuration, compatibility
---

# Define NAPI_VERSION Early

Set `#define NAPI_VERSION` before including `node_api.h` to specify which N-API version your addon targets. This ensures you have access to the correct API surface and enables version-specific features.

## Why This Matters

- **API Availability**: Higher versions unlock newer APIs (e.g., type tags in v8)
- **Compile-Time Safety**: Prevents accidental use of unavailable APIs
- **Runtime Compatibility**: Node.js validates version at module load
- **Documentation Clarity**: Explicit version makes requirements clear

## N-API Version History

| Version | Node.js | Key Features |
|---------|---------|--------------|
| 1 | 8.0.0+ | Core API |
| 3 | 10.0.0+ | BigInt support |
| 4 | 10.16.0+ | Thread-safe functions |
| 5 | 12.0.0+ | Date object support |
| 6 | 12.11.0+ | Key conversion APIs |
| 7 | 14.12.0+ | ArrayBuffer detach |
| 8 | 15.0.0+ | Type tags, async cleanup |
| 9 | 18.17.0+ | Node-API lifecycle |

## Incorrect: Missing Version Definition

```cpp
// BAD: No version defined - may get unexpected API surface
#include <node_api.h>

static napi_value Init(napi_env env, napi_value exports) {
    // This might fail if using APIs from newer versions
    napi_value result;

    // Type tags require NAPI_VERSION >= 8
    // Without defining version, this may not compile or work
    static const napi_type_tag type_tag = {
        0x1234567890abcdef, 0xfedcba0987654321
    };
    napi_type_tag_object(env, result, &type_tag);  // May fail!

    return exports;
}
```

## Incorrect: Version Defined After Include

```cpp
// BAD: Version defined AFTER include has no effect
#include <node_api.h>
#define NAPI_VERSION 8  // Too late! Include already processed

static napi_value Init(napi_env env, napi_value exports) {
    return exports;
}
```

## Correct: Version Defined Before Include

```cpp
// GOOD: Version defined before any N-API includes
#define NAPI_VERSION 8
#include <node_api.h>

static napi_value CreateTaggedObject(napi_env env, napi_callback_info info) {
    napi_value obj;
    napi_status status;

    status = napi_create_object(env, &obj);
    if (status != napi_ok) return NULL;

    // Type tags available because NAPI_VERSION >= 8
    static const napi_type_tag type_tag = {
        0x1234567890abcdef,
        0xfedcba0987654321
    };
    status = napi_type_tag_object(env, obj, &type_tag);
    if (status != napi_ok) return NULL;

    return obj;
}

static napi_value Init(napi_env env, napi_value exports) {
    napi_value fn;
    napi_create_function(env, NULL, 0, CreateTaggedObject, NULL, &fn);
    napi_set_named_property(env, exports, "createTagged", fn);
    return exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

## Correct: Using node-addon-api with Version

```cpp
// GOOD: node-addon-api handles version, but you can still specify
#define NAPI_VERSION 8
#include <napi.h>

class TypedWrapper : public Napi::ObjectWrap<TypedWrapper> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "TypedWrapper", {
            InstanceMethod("getValue", &TypedWrapper::GetValue)
        });

        // Type tag for safe downcasting
        Napi::Object prototype = func.Get("prototype").As<Napi::Object>();
        prototype.TypeTag(&typeTag_);

        exports.Set("TypedWrapper", func);
        return exports;
    }

    TypedWrapper(const Napi::CallbackInfo& info)
        : Napi::ObjectWrap<TypedWrapper>(info) {}

private:
    Napi::Value GetValue(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), 42);
    }

    static inline napi_type_tag typeTag_ = {
        0x1234567890abcdef, 0xfedcba0987654321
    };
};

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    return TypedWrapper::Init(env, exports);
}

NODE_API_MODULE(addon, Init)
```

## Best Practice: Header File Configuration

```cpp
// config.h - Centralized version configuration
#ifndef ADDON_CONFIG_H
#define ADDON_CONFIG_H

// Target N-API version 8 for type tags and async cleanup
#define NAPI_VERSION 8

// Enable experimental features if needed (use with caution)
// #define NAPI_EXPERIMENTAL

#endif // ADDON_CONFIG_H
```

```cpp
// addon.cpp - Include config first
#include "config.h"
#include <napi.h>

// Rest of implementation...
```

## binding.gyp Configuration

```python
{
    "targets": [{
        "target_name": "addon",
        "sources": ["src/addon.cpp"],
        "include_dirs": [
            "<!@(node -p \"require('node-addon-api').include\")"
        ],
        "defines": [
            "NAPI_VERSION=8"  # Can also define here
        ]
    }]
}
```

## Version Selection Guidelines

1. **Choose minimum required version** - Don't target higher than needed
2. **Document Node.js requirements** - Update package.json engines field
3. **Test on target versions** - Verify addon works on minimum Node.js
4. **Consider LTS schedule** - Align with Node.js LTS for production

```json
{
    "name": "my-addon",
    "engines": {
        "node": ">=15.0.0"
    }
}
```

## References

- [N-API Version Matrix](https://nodejs.org/api/n-api.html#node-api-version-matrix)
- [Node.js Release Schedule](https://nodejs.org/en/about/releases/)
