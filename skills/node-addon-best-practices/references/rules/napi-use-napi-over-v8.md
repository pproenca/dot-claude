---
title: Always Use N-API Over V8
impact: CRITICAL
impactDescription: V8 API changes break addons on Node.js upgrades; N-API provides ABI stability across versions
tags: napi, abi-stability, compatibility, node-api
---

# Always Use N-API Over V8

Use the stable ABI Node-API (N-API) instead of the V8 C++ API for cross-version compatibility. N-API abstracts the underlying JavaScript engine, allowing your addon to work across Node.js versions without recompilation.

## Why This Matters

- **ABI Stability**: N-API maintains binary compatibility across Node.js major versions
- **No Recompilation**: Addons built with N-API work on new Node.js releases without rebuilding
- **Future-Proof**: Protects against V8 internal API changes
- **Portability**: Works with alternative JS engines (experimental)

## Incorrect: Using V8 API Directly

```cpp
// BAD: Direct V8 API usage - breaks on Node.js upgrades
#include <v8.h>
#include <node.h>

void Initialize(v8::Local<v8::Object> exports) {
    v8::Isolate* isolate = exports->GetIsolate();
    v8::Local<v8::Context> context = isolate->GetCurrentContext();

    // V8-specific handle creation
    v8::Local<v8::String> key = v8::String::NewFromUtf8(
        isolate, "hello", v8::NewStringType::kNormal).ToLocalChecked();
    v8::Local<v8::FunctionTemplate> tpl = v8::FunctionTemplate::New(isolate, Hello);

    exports->Set(context, key, tpl->GetFunction(context).ToLocalChecked()).Check();
}

void Hello(const v8::FunctionCallbackInfo<v8::Value>& args) {
    v8::Isolate* isolate = args.GetIsolate();
    v8::Local<v8::String> result = v8::String::NewFromUtf8(
        isolate, "world", v8::NewStringType::kNormal).ToLocalChecked();
    args.GetReturnValue().Set(result);
}

NODE_MODULE(addon, Initialize)
```

## Correct: Using node-addon-api (N-API C++ Wrapper)

```cpp
// GOOD: node-addon-api provides stable ABI and cleaner syntax
#include <napi.h>

Napi::String Hello(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    return Napi::String::New(env, "world");
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    exports.Set(
        Napi::String::New(env, "hello"),
        Napi::Function::New(env, Hello)
    );
    return exports;
}

NODE_API_MODULE(addon, Init)
```

## Correct: Using Raw N-API (C API)

```cpp
// GOOD: Raw N-API for C projects or maximum control
#include <node_api.h>

static napi_value Hello(napi_env env, napi_callback_info info) {
    napi_value result;
    napi_status status = napi_create_string_utf8(env, "world", NAPI_AUTO_LENGTH, &result);
    if (status != napi_ok) {
        napi_throw_error(env, NULL, "Failed to create string");
        return NULL;
    }
    return result;
}

static napi_value Init(napi_env env, napi_value exports) {
    napi_value fn;
    napi_status status;

    status = napi_create_function(env, NULL, 0, Hello, NULL, &fn);
    if (status != napi_ok) return NULL;

    status = napi_set_named_property(env, exports, "hello", fn);
    if (status != napi_ok) return NULL;

    return exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

## Migration Checklist

- [ ] Replace `#include <v8.h>` with `#include <napi.h>`
- [ ] Replace `v8::Local<T>` with `Napi::T` types
- [ ] Replace `v8::Isolate*` access with `Napi::Env`
- [ ] Replace `NODE_MODULE` with `NODE_API_MODULE`
- [ ] Update binding.gyp to include node-addon-api

## binding.gyp Configuration

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
        "cflags_cc!": ["-fno-exceptions"]
    }]
}
```

## References

- [Node-API Documentation](https://nodejs.org/api/n-api.html)
- [node-addon-api Repository](https://github.com/nodejs/node-addon-api)
- [ABI Stability Guide](https://nodejs.org/en/docs/guides/abi-stability/)
