---
title: Use Correct Number Type Conversions
impact: MEDIUM-HIGH
impactDescription: avoids precision loss and range errors
tags: conv, numbers, types, precision
---

## Use Correct Number Type Conversions

JavaScript numbers are IEEE 754 doubles. Using incorrect C++ types causes silent precision loss or crashes.

**Incorrect (wrong types):**

```cpp
Napi::Value ProcessNumber(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // BUG: Int32Value() truncates values > 2^31
  int32_t large = info[0].As<Napi::Number>().Int32Value();
  // Input: 3000000000 → Output: -1294967296

  // BUG: Uint32Value() wraps negative values
  uint32_t positive = info[1].As<Napi::Number>().Uint32Value();
  // Input: -1 → Output: 4294967295

  // BUG: Float loses precision for large integers
  float value = info[2].As<Napi::Number>().FloatValue();
  // Input: 16777217 → Output: 16777216 (precision lost)
}
```

**Correct (appropriate types):**

```cpp
Napi::Value ProcessNumber(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  // For large integers, use int64_t or double
  int64_t large = info[0].As<Napi::Number>().Int64Value();

  // For general numbers, use double (matches JS precision)
  double value = info[1].As<Napi::Number>().DoubleValue();

  // For validated small integers, int32_t is fine
  if (IsValidInt32(info[2])) {
    int32_t small = info[2].As<Napi::Number>().Int32Value();
  }
}

bool IsValidInt32(Napi::Value val) {
  double d = val.As<Napi::Number>().DoubleValue();
  return d >= INT32_MIN && d <= INT32_MAX && d == std::floor(d);
}
```

**Safe conversion helpers:**

```cpp
#include <limits>
#include <cmath>

std::optional<int32_t> SafeToInt32(const Napi::Value& val) {
  if (!val.IsNumber()) return std::nullopt;

  double d = val.As<Napi::Number>().DoubleValue();

  if (std::isnan(d) || std::isinf(d)) return std::nullopt;
  if (d < INT32_MIN || d > INT32_MAX) return std::nullopt;
  if (d != std::trunc(d)) return std::nullopt;  // Not an integer

  return static_cast<int32_t>(d);
}

std::optional<uint32_t> SafeToUint32(const Napi::Value& val) {
  if (!val.IsNumber()) return std::nullopt;

  double d = val.As<Napi::Number>().DoubleValue();

  if (std::isnan(d) || std::isinf(d)) return std::nullopt;
  if (d < 0 || d > UINT32_MAX) return std::nullopt;
  if (d != std::trunc(d)) return std::nullopt;

  return static_cast<uint32_t>(d);
}

// Usage
Napi::Value SafeProcess(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  auto index = SafeToUint32(info[0]);
  if (!index) {
    Napi::TypeError::New(env, "Expected valid uint32 index")
      .ThrowAsJavaScriptException();
    return env.Undefined();
  }

  ProcessIndex(*index);
  return env.Undefined();
}
```

**BigInt for large integers:**

```cpp
// For integers > 2^53 - 1, use BigInt
Napi::Value ProcessBigInt(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();

  if (info[0].IsBigInt()) {
    Napi::BigInt bi = info[0].As<Napi::BigInt>();
    bool lossless;
    int64_t value = bi.Int64Value(&lossless);

    if (!lossless) {
      // Value doesn't fit in int64_t
      // Use bi.ToWords() for arbitrary precision
    }
  }

  return env.Undefined();
}

// Return BigInt
Napi::Value ReturnLargeInt(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  uint64_t large_value = 9007199254740993ULL;  // > MAX_SAFE_INTEGER

  return Napi::BigInt::New(env, large_value);
}
```

Reference: [MDN Number](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number)
