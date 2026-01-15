---
title: Use node-addon-api Over Raw N-API
impact: MEDIUM
impactDescription: reduces boilerplate and prevents common errors
tags: napi, addon-api, wrapper, safety
---

## Use node-addon-api Over Raw N-API

node-addon-api provides C++ wrappers with automatic error handling and RAII patterns. Use it instead of raw N-API C functions.

**Incorrect (raw N-API):**

```cpp
napi_value ProcessData(napi_env env, napi_callback_info info) {
  napi_status status;
  size_t argc = 1;
  napi_value argv[1];

  status = napi_get_cb_info(env, info, &argc, argv, nullptr, nullptr);
  if (status != napi_ok) return nullptr;

  napi_valuetype type;
  status = napi_typeof(env, argv[0], &type);
  if (status != napi_ok) return nullptr;

  // Manual error handling throughout...
}
```

**Correct (node-addon-api):**

```cpp
#include <napi.h>

Napi::Value ProcessData(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  if (!info[0].IsNumber()) {
    Napi::TypeError::New(env, "Expected number")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }

  // Clean, safe, automatic error propagation
  return Napi::Number::New(env, info[0].As<Napi::Number>().DoubleValue() * 2);
}
```

Reference: [node-addon-api](https://github.com/nodejs/node-addon-api)
