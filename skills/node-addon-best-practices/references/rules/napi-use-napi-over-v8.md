---
title: Always Use N-API Over V8
impact: CRITICAL
impactDescription: Eliminates rebuild requirement on Node.js upgrades (saves 2-8 hours per major release cycle)
tags: napi, abi-stability, compatibility, node-api, node-addon-api
---

# Always Use N-API Over V8

Use the stable ABI Node-API (N-API) instead of the V8 C++ API for cross-version compatibility. N-API abstracts the underlying JavaScript engine, allowing your addon to work across Node.js versions without recompilation. V8 API breaks on every Node.js major release - N-API eliminates this maintenance burden entirely.

## Why This Matters

- **ABI Stability**: N-API maintains binary compatibility across Node.js major versions
- **No Recompilation**: Addons built with N-API work on new Node.js releases without rebuilding
- **Future-Proof**: Protects against V8 internal API changes
- **Portability**: Works with alternative JS engines (experimental)

## Incorrect: Using V8 API Directly

```cpp
// PROBLEM: V8 API changes ~3-5 functions per major Node.js release
// This code broke on Node 14->16, 16->18, and 18->20 transitions
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
// SOLUTION: Compile once, run on Node 12-22+ without changes
// node-addon-api provides stable ABI and cleaner syntax
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

## Alternative: Using napi-rs (Rust)

```rust
// For Rust projects, napi-rs provides N-API bindings with memory safety
use napi_derive::napi;

#[napi]
pub fn hello() -> String {
    "world".to_string()
}
```

**When to use:** Prefer napi-rs for new projects if your team has Rust experience. Provides memory safety guarantees that C++ cannot.

**When NOT to use:** V8 API is only appropriate when you need V8-specific features not exposed by N-API (rare), or are building Node.js itself. For 99% of addons, N-API is the correct choice.

## References

- [Node-API Documentation](https://nodejs.org/api/n-api.html)
- [node-addon-api Repository](https://github.com/nodejs/node-addon-api)
- [napi-rs Repository](https://github.com/napi-rs/napi-rs)
- [ABI Stability Guide](https://nodejs.org/en/docs/guides/abi-stability/)
