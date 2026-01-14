---
title: Use node-addon-api C++ Wrapper
impact: CRITICAL
impactDescription: Raw N-API requires 3x more code and is error-prone; wrapper provides type safety
tags: napi, node-addon-api, cpp, wrapper
---

# Use node-addon-api C++ Wrapper

Prefer the `node-addon-api` C++ wrapper over raw N-API for type safety, automatic error handling, and significantly cleaner code. The wrapper is a header-only library that compiles to the same stable ABI.

## Why This Matters

- **Type Safety**: C++ types catch errors at compile time
- **Automatic Error Handling**: Exceptions propagate correctly to JavaScript
- **Reduced Boilerplate**: 60-70% less code than raw N-API
- **Memory Safety**: RAII ensures proper cleanup
- **Same ABI**: Compiles to identical stable N-API calls

## Incorrect: Raw N-API (Verbose and Error-Prone)

```cpp
// BAD: Raw N-API requires extensive boilerplate
#include <node_api.h>
#include <string.h>

typedef struct {
    double x;
    double y;
} Point;

static void PointFinalize(napi_env env, void* finalize_data, void* finalize_hint) {
    Point* point = (Point*)finalize_data;
    free(point);
}

static napi_value CreatePoint(napi_env env, napi_callback_info info) {
    napi_status status;

    // Get arguments
    size_t argc = 2;
    napi_value argv[2];
    status = napi_get_cb_info(env, info, &argc, argv, NULL, NULL);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to get callback info");
        return NULL;
    }

    // Validate argument count
    if (argc < 2) {
        napi_throw_type_error(env, NULL, "Expected 2 arguments");
        return NULL;
    }

    // Validate and get x
    napi_valuetype type;
    status = napi_typeof(env, argv[0], &type);
    if (status != napi_ok || type != napi_number) {
        napi_throw_type_error(env, NULL, "First argument must be a number");
        return NULL;
    }
    double x;
    status = napi_get_value_double(env, argv[0], &x);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to get x value");
        return NULL;
    }

    // Validate and get y
    status = napi_typeof(env, argv[1], &type);
    if (status != napi_ok || type != napi_number) {
        napi_throw_type_error(env, NULL, "Second argument must be a number");
        return NULL;
    }
    double y;
    status = napi_get_value_double(env, argv[1], &y);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to get y value");
        return NULL;
    }

    // Allocate native data
    Point* point = (Point*)malloc(sizeof(Point));
    if (point == NULL) {
        napi_throw_error(env, NULL, "Failed to allocate memory");
        return NULL;
    }
    point->x = x;
    point->y = y;

    // Create external object
    napi_value result;
    status = napi_create_external(env, point, PointFinalize, NULL, &result);
    if (status != napi_ok) {
        free(point);
        napi_throw_error(env, NULL, "Failed to create external");
        return NULL;
    }

    return result;
}

static napi_value GetX(napi_env env, napi_callback_info info) {
    napi_status status;
    size_t argc = 1;
    napi_value argv[1];

    status = napi_get_cb_info(env, info, &argc, argv, NULL, NULL);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to get callback info");
        return NULL;
    }

    Point* point;
    status = napi_get_value_external(env, argv[0], (void**)&point);
    if (status != napi_ok) {
        napi_throw_type_error(env, NULL, "Expected Point external");
        return NULL;
    }

    napi_value result;
    status = napi_create_double(env, point->x, &result);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to create number");
        return NULL;
    }

    return result;
}

// Similar verbose code for GetY, Distance, etc...

static napi_value Init(napi_env env, napi_value exports) {
    napi_status status;
    napi_value fn;

    status = napi_create_function(env, NULL, 0, CreatePoint, NULL, &fn);
    if (status != napi_ok) return NULL;
    status = napi_set_named_property(env, exports, "createPoint", fn);
    if (status != napi_ok) return NULL;

    status = napi_create_function(env, NULL, 0, GetX, NULL, &fn);
    if (status != napi_ok) return NULL;
    status = napi_set_named_property(env, exports, "getX", fn);
    if (status != napi_ok) return NULL;

    // ... more exports

    return exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

## Correct: node-addon-api (Clean and Safe)

```cpp
// GOOD: node-addon-api provides clean, type-safe API
#include <napi.h>
#include <cmath>

class Point : public Napi::ObjectWrap<Point> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "Point", {
            InstanceAccessor<&Point::GetX, &Point::SetX>("x"),
            InstanceAccessor<&Point::GetY, &Point::SetY>("y"),
            InstanceMethod<&Point::Distance>("distance"),
            InstanceMethod<&Point::ToString>("toString"),
            StaticMethod<&Point::Origin>("origin")
        });

        Napi::FunctionReference* constructor = new Napi::FunctionReference();
        *constructor = Napi::Persistent(func);
        env.SetInstanceData(constructor);

        exports.Set("Point", func);
        return exports;
    }

    Point(const Napi::CallbackInfo& info) : Napi::ObjectWrap<Point>(info) {
        Napi::Env env = info.Env();

        if (info.Length() < 2) {
            throw Napi::TypeError::New(env, "Expected 2 arguments");
        }
        if (!info[0].IsNumber() || !info[1].IsNumber()) {
            throw Napi::TypeError::New(env, "Arguments must be numbers");
        }

        x_ = info[0].As<Napi::Number>().DoubleValue();
        y_ = info[1].As<Napi::Number>().DoubleValue();
    }

private:
    Napi::Value GetX(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), x_);
    }

    void SetX(const Napi::CallbackInfo& info, const Napi::Value& value) {
        x_ = value.As<Napi::Number>().DoubleValue();
    }

    Napi::Value GetY(const Napi::CallbackInfo& info) {
        return Napi::Number::New(info.Env(), y_);
    }

    void SetY(const Napi::CallbackInfo& info, const Napi::Value& value) {
        y_ = value.As<Napi::Number>().DoubleValue();
    }

    Napi::Value Distance(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();

        double otherX = 0, otherY = 0;
        if (info.Length() >= 1 && info[0].IsObject()) {
            Point* other = Napi::ObjectWrap<Point>::Unwrap(info[0].As<Napi::Object>());
            otherX = other->x_;
            otherY = other->y_;
        }

        double dx = x_ - otherX;
        double dy = y_ - otherY;
        return Napi::Number::New(env, std::sqrt(dx * dx + dy * dy));
    }

    Napi::Value ToString(const Napi::CallbackInfo& info) {
        return Napi::String::New(info.Env(),
            "Point(" + std::to_string(x_) + ", " + std::to_string(y_) + ")");
    }

    static Napi::Value Origin(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        Napi::FunctionReference* constructor = env.GetInstanceData<Napi::FunctionReference>();
        return constructor->New({ Napi::Number::New(env, 0), Napi::Number::New(env, 0) });
    }

    double x_;
    double y_;
};

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    return Point::Init(env, exports);
}

NODE_API_MODULE(point, Init)
```

## Feature Comparison

| Feature | Raw N-API | node-addon-api |
|---------|-----------|----------------|
| Type checking | Manual | Automatic |
| Error handling | Manual status checks | C++ exceptions |
| Object wrapping | Complex | `ObjectWrap<T>` |
| Accessors | Manual property setup | `InstanceAccessor` |
| Cleanup | Manual release | RAII/destructors |
| Code volume | ~3x more | Minimal |
| Compile-time safety | None | Strong |

## Common Patterns with node-addon-api

### Type-Safe Value Extraction

```cpp
Napi::Value ProcessArgs(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Safe type checking with Is* methods
    if (info.Length() < 1) {
        throw Napi::TypeError::New(env, "Missing argument");
    }

    if (info[0].IsString()) {
        std::string str = info[0].As<Napi::String>().Utf8Value();
        return Napi::String::New(env, "String: " + str);
    }

    if (info[0].IsNumber()) {
        double num = info[0].As<Napi::Number>().DoubleValue();
        return Napi::String::New(env, "Number: " + std::to_string(num));
    }

    if (info[0].IsArray()) {
        Napi::Array arr = info[0].As<Napi::Array>();
        return Napi::String::New(env, "Array length: " + std::to_string(arr.Length()));
    }

    if (info[0].IsObject()) {
        Napi::Object obj = info[0].As<Napi::Object>();
        Napi::Array keys = obj.GetPropertyNames();
        return Napi::String::New(env, "Object keys: " + std::to_string(keys.Length()));
    }

    throw Napi::TypeError::New(env, "Unsupported type");
}
```

### Safe Object Property Access

```cpp
Napi::Value ProcessObject(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Object obj = info[0].As<Napi::Object>();

    // Safe property access with defaults
    std::string name = "unknown";
    if (obj.Has("name") && obj.Get("name").IsString()) {
        name = obj.Get("name").As<Napi::String>().Utf8Value();
    }

    int32_t age = 0;
    if (obj.Has("age") && obj.Get("age").IsNumber()) {
        age = obj.Get("age").As<Napi::Number>().Int32Value();
    }

    return Napi::String::New(env, name + " is " + std::to_string(age));
}
```

## Setup Instructions

### package.json

```json
{
    "name": "my-addon",
    "dependencies": {
        "node-addon-api": "^7.0.0"
    }
}
```

### binding.gyp

```python
{
    "targets": [{
        "target_name": "addon",
        "sources": ["src/addon.cpp"],
        "include_dirs": [
            "<!@(node -p \"require('node-addon-api').include\")"
        ],
        "defines": ["NAPI_DISABLE_CPP_EXCEPTIONS"],
        "cflags!": ["-fno-exceptions"],
        "cflags_cc!": ["-fno-exceptions"],
        "xcode_settings": {
            "GCC_ENABLE_CPP_EXCEPTIONS": "YES",
            "CLANG_CXX_LIBRARY": "libc++",
            "MACOSX_DEPLOYMENT_TARGET": "10.15"
        },
        "msvs_settings": {
            "VCCLCompilerTool": {
                "ExceptionHandling": 1
            }
        }
    }]
}
```

## References

- [node-addon-api Documentation](https://github.com/nodejs/node-addon-api/blob/main/doc/README.md)
- [node-addon-api Examples](https://github.com/nodejs/node-addon-examples)
