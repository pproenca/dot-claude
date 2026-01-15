---
title: Use HandleScope in All Native Functions
impact: HIGH
impactDescription: prevents handle table overflow and crashes
tags: handle, scope, v8, memory
---

## Use HandleScope in All Native Functions

Every V8 value created in C++ needs a handle. Without HandleScope, handles accumulate and overflow V8's handle table.

**Incorrect (no scope management):**

```cpp
void ProcessManyItems(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();

  for (uint32_t i = 0; i < items.Length(); i++) {
    // Each iteration creates handles that never get released
    Napi::Value item = items[i];
    Napi::Object obj = item.As<Napi::Object>();
    Napi::Value name = obj.Get("name");
    Napi::Value value = obj.Get("value");
    // ... process

    // After millions of iterations: CRASH - handle table full
  }
}
```

**Correct (scoped handles):**

```cpp
void ProcessManyItems(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();

  for (uint32_t i = 0; i < items.Length(); i++) {
    // Create scope for loop iteration - handles released each iteration
    Napi::HandleScope scope(env);

    Napi::Value item = items[i];
    Napi::Object obj = item.As<Napi::Object>();
    Napi::Value name = obj.Get("name");
    Napi::Value value = obj.Get("value");
    // ... process

    // Handles released when scope exits
  }
}
```

**Note:** node-addon-api functions like those defined via `Napi::Function::New` or `DefineClass` automatically create a HandleScope. The issue arises in helper functions or loops.

**Helper function pattern:**

```cpp
// Helper that creates many temporaries
std::string ExtractName(Napi::Env env, Napi::Object obj) {
  // HandleScope for helper function
  Napi::HandleScope scope(env);

  Napi::Value nameVal = obj.Get("name");
  if (!nameVal.IsString()) {
    return "";
  }

  // Convert to C++ string before scope exits
  return nameVal.As<Napi::String>().Utf8Value();
}

void ProcessAll(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array items = info[0].As<Napi::Array>();

  for (uint32_t i = 0; i < items.Length(); i++) {
    Napi::HandleScope scope(env);
    Napi::Object obj = items[i].As<Napi::Object>();

    // Helper has its own scope
    std::string name = ExtractName(env, obj);
    ProcessName(name);
  }
}
```

**EscapableHandleScope for returning values:**

```cpp
Napi::Value CreateInHelper(Napi::Env env) {
  // Use EscapableHandleScope when returning a handle
  Napi::EscapableHandleScope scope(env);

  Napi::Object result = Napi::Object::New(env);
  result.Set("created", Napi::Boolean::New(env, true));

  // Escape the value so it survives scope exit
  return scope.Escape(result);
}
```

Reference: [V8 Embedder Guide - Handles](https://v8.dev/docs/embed#handles-and-garbage-collection)
