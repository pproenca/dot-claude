---
title: Cache Property Accessors Across Calls
impact: CRITICAL
impactDescription: 5-20× improvement for repeated property access
tags: boundary, caching, property-access, persistent
---

## Cache Property Accessors Across Calls

Looking up object properties by string name requires hash table lookups. Cache `Napi::PropertyDescriptor` or use indexed properties for repeated access patterns.

**Incorrect (string lookup every access):**

```cpp
Napi::Value ProcessObjects(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array objects = info[0].As<Napi::Array>();

  double sum = 0;
  for (uint32_t i = 0; i < objects.Length(); i++) {
    Napi::Object obj = objects[i].As<Napi::Object>();
    // String lookup on EVERY iteration
    sum += obj.Get("value").As<Napi::Number>().DoubleValue();
    sum += obj.Get("weight").As<Napi::Number>().DoubleValue();
  }
  return Napi::Number::New(env, sum);
}
```

**Correct (cached property names):**

```cpp
// Module-level cached property names
static Napi::Reference<Napi::String> cachedValueKey;
static Napi::Reference<Napi::String> cachedWeightKey;

Napi::Object Init(Napi::Env env, Napi::Object exports) {
  // Cache property names once at module init
  cachedValueKey = Napi::Persistent(Napi::String::New(env, "value"));
  cachedWeightKey = Napi::Persistent(Napi::String::New(env, "weight"));
  // ... rest of init
}

Napi::Value ProcessObjects(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array objects = info[0].As<Napi::Array>();

  // Get cached keys once
  Napi::String valueKey = cachedValueKey.Value();
  Napi::String weightKey = cachedWeightKey.Value();

  double sum = 0;
  for (uint32_t i = 0; i < objects.Length(); i++) {
    Napi::Object obj = objects[i].As<Napi::Object>();
    // Use cached keys - faster lookup
    sum += obj.Get(valueKey).As<Napi::Number>().DoubleValue();
    sum += obj.Get(weightKey).As<Napi::Number>().DoubleValue();
  }
  return Napi::Number::New(env, sum);
}
```

**Alternative (use TypedArrays for numeric data):**

```cpp
// Even faster: use Float64Array instead of objects
Napi::Value ProcessTypedArray(const Napi::CallbackInfo& info) {
  Napi::Float64Array data = info[0].As<Napi::Float64Array>();
  double* ptr = data.Data();
  size_t length = data.ElementLength();

  double sum = 0;
  for (size_t i = 0; i < length; i++) {
    sum += ptr[i];  // Direct memory access, no JS overhead
  }
  return Napi::Number::New(info.Env(), sum);
}
```

Reference: [N-API Reference](https://nodejs.org/api/n-api.html#napi_get_named_property)
