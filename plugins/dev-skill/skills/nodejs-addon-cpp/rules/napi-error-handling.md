---
title: Handle Errors with Exceptions
impact: MEDIUM
impactDescription: proper error propagation to JavaScript
tags: napi, errors, exceptions, handling
---

## Handle Errors with Exceptions

Use Napi::Error and its subclasses to throw JavaScript exceptions. Check for pending exceptions after calling JS functions.

**Incorrect (silent failures):**

```cpp
Napi::Value Divide(const Napi::CallbackInfo& info) {
  double a = info[0].As<Napi::Number>().DoubleValue();
  double b = info[1].As<Napi::Number>().DoubleValue();

  if (b == 0) {
    return info.Env().Undefined();  // Silent failure!
  }

  return Napi::Number::New(info.Env(), a / b);
}
```

**Correct (proper exceptions):**

```cpp
Napi::Value Divide(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  double a = info[0].As<Napi::Number>().DoubleValue();
  double b = info[1].As<Napi::Number>().DoubleValue();

  if (b == 0) {
    Napi::RangeError::New(env, "Division by zero")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }

  return Napi::Number::New(env, a / b);
}
```

Reference: [N-API Error Handling](https://nodejs.org/api/n-api.html#error-handling)
