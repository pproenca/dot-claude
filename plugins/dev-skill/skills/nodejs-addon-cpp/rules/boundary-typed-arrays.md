---
title: Use TypedArrays for Numeric Data
impact: CRITICAL
impactDescription: 20-100× improvement over JS arrays
tags: boundary, typed-arrays, zero-copy, numeric-data
---

## Use TypedArrays for Numeric Data

TypedArrays provide direct memory access without per-element JS↔C++ conversion. This eliminates boxing/unboxing overhead and enables SIMD optimization.

**Incorrect (JS Array with boxing):**

```cpp
Napi::Value SumArray(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Array arr = info[0].As<Napi::Array>();

  double sum = 0;
  for (uint32_t i = 0; i < arr.Length(); i++) {
    // Each access: boundary crossing + unboxing
    sum += arr.Get(i).As<Napi::Number>().DoubleValue();
  }
  return Napi::Number::New(env, sum);
}
```

```javascript
// JS side - using regular array
const data = [1.0, 2.0, 3.0, /* ... thousands more */];
const result = addon.sumArray(data);
```

**Correct (TypedArray with direct access):**

```cpp
Napi::Value SumTypedArray(const Napi::CallbackInfo& info) {
  Napi::Env env = info.Env();
  Napi::Float64Array arr = info[0].As<Napi::Float64Array>();

  double* data = arr.Data();  // Direct pointer to memory
  size_t length = arr.ElementLength();

  double sum = 0;
  for (size_t i = 0; i < length; i++) {
    sum += data[i];  // Pure C++ memory access
  }
  return Napi::Number::New(env, sum);
}
```

```javascript
// JS side - using Float64Array
const data = new Float64Array([1.0, 2.0, 3.0, /* ... thousands more */]);
const result = addon.sumTypedArray(data);
```

**SIMD-optimized version:**

```cpp
#include <immintrin.h>

Napi::Value SumTypedArraySIMD(const Napi::CallbackInfo& info) {
  Napi::Float64Array arr = info[0].As<Napi::Float64Array>();
  double* data = arr.Data();
  size_t length = arr.ElementLength();

  __m256d sum_vec = _mm256_setzero_pd();
  size_t i = 0;

  // Process 4 doubles at a time
  for (; i + 4 <= length; i += 4) {
    __m256d vec = _mm256_loadu_pd(&data[i]);
    sum_vec = _mm256_add_pd(sum_vec, vec);
  }

  // Horizontal sum
  double temp[4];
  _mm256_storeu_pd(temp, sum_vec);
  double sum = temp[0] + temp[1] + temp[2] + temp[3];

  // Handle remaining elements
  for (; i < length; i++) {
    sum += data[i];
  }

  return Napi::Number::New(info.Env(), sum);
}
```

**Benefits:**
- Zero-copy data sharing between JS and C++
- Cache-friendly contiguous memory layout
- Enables SIMD vectorization
- No garbage collection overhead for numeric data

Reference: [MDN TypedArray](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypedArray)
