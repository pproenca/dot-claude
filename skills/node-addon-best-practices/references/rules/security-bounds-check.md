---
title: Bounds-Check Array Access
impact: LOW-MEDIUM
impactDescription: Prevents out-of-bounds access vulnerabilities
tags: security, arrays, bounds-checking, validation, memory-safety
---

# Bounds-Check Array Access

Always verify array indices are within bounds before accessing elements. Check against the actual array length, not assumptions about size.

## Why This Matters

- Out-of-bounds access causes undefined behavior
- Can read/write arbitrary memory locations
- Security vulnerabilities in untrusted input scenarios
- Crashes are the best-case outcome; silent corruption is worse

## Incorrect

Direct array access without bounds verification:

```cpp
#include <napi.h>

// BAD: No bounds checking on array index
Napi::Value GetElement(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Array arr = info[0].As<Napi::Array>();
    uint32_t index = info[1].As<Napi::Number>().Uint32Value();

    // DANGER: No validation that index < arr.Length()
    return arr.Get(index);
}

// BAD: TypedArray access without bounds check
Napi::Value ProcessAtIndex(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float64Array data = info[0].As<Napi::Float64Array>();
    uint32_t index = info[1].As<Napi::Number>().Uint32Value();

    // DANGER: Direct pointer access without bounds check
    double* ptr = data.Data();
    double value = ptr[index];  // Could be out of bounds

    return Napi::Number::New(env, value * 2.0);
}

// BAD: Loop without proper bounds on both arrays
Napi::Value CopyElements(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float64Array source = info[0].As<Napi::Float64Array>();
    Napi::Float64Array dest = info[1].As<Napi::Float64Array>();

    double* srcPtr = source.Data();
    double* destPtr = dest.Data();

    // DANGER: Only checks source length, dest might be smaller
    for (size_t i = 0; i < source.ElementLength(); i++) {
        destPtr[i] = srcPtr[i];
    }

    return env.Undefined();
}
```

## Correct

Validate indices against actual array length:

```cpp
#include <napi.h>
#include <algorithm>

// GOOD: Bounds check before array access
Napi::Value SafeGetElement(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 2 || !info[0].IsArray() || !info[1].IsNumber()) {
        Napi::TypeError::New(env, "Expected (array, index)")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Array arr = info[0].As<Napi::Array>();
    uint32_t index = info[1].As<Napi::Number>().Uint32Value();

    // Get actual array length
    uint32_t length = arr.Length();

    // Bounds check
    if (index >= length) {
        Napi::RangeError::New(env,
            "Index " + std::to_string(index) +
            " out of bounds for array of length " + std::to_string(length))
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    return arr.Get(index);
}

// GOOD: TypedArray with bounds validation
Napi::Value SafeProcessAtIndex(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 2) {
        Napi::TypeError::New(env, "Expected (typedArray, index)")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (!info[0].IsTypedArray()) {
        Napi::TypeError::New(env, "First argument must be a TypedArray")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Float64Array data = info[0].As<Napi::Float64Array>();
    uint32_t index = info[1].As<Napi::Number>().Uint32Value();

    // Get actual element count
    size_t length = data.ElementLength();

    // Bounds check
    if (index >= length) {
        Napi::RangeError::New(env,
            "Index out of bounds")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    double* ptr = data.Data();
    double value = ptr[index];

    return Napi::Number::New(env, value * 2.0);
}

// GOOD: Safe copy with proper bounds on both arrays
Napi::Value SafeCopyElements(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 2) {
        Napi::TypeError::New(env, "Expected (source, dest)")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Float64Array source = info[0].As<Napi::Float64Array>();
    Napi::Float64Array dest = info[1].As<Napi::Float64Array>();

    size_t sourceLen = source.ElementLength();
    size_t destLen = dest.ElementLength();

    // Use minimum of both lengths
    size_t copyLen = std::min(sourceLen, destLen);

    double* srcPtr = source.Data();
    double* destPtr = dest.Data();

    for (size_t i = 0; i < copyLen; i++) {
        destPtr[i] = srcPtr[i];
    }

    // Return actual number of elements copied
    return Napi::Number::New(env, static_cast<double>(copyLen));
}
```

## Range-Based Operations with Validation

```cpp
#include <napi.h>

// GOOD: Validate start and end indices for range operations
Napi::Value SafeSliceSum(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float64Array data = info[0].As<Napi::Float64Array>();
    int64_t start = info[1].As<Napi::Number>().Int64Value();
    int64_t end = info[2].As<Napi::Number>().Int64Value();

    size_t length = data.ElementLength();
    double* ptr = data.Data();

    // Handle negative indices (Python-style)
    if (start < 0) {
        start = static_cast<int64_t>(length) + start;
    }
    if (end < 0) {
        end = static_cast<int64_t>(length) + end;
    }

    // Clamp to valid range
    size_t safeStart = static_cast<size_t>(
        std::max<int64_t>(0, std::min<int64_t>(start, length))
    );
    size_t safeEnd = static_cast<size_t>(
        std::max<int64_t>(0, std::min<int64_t>(end, length))
    );

    // Ensure start <= end
    if (safeStart > safeEnd) {
        return Napi::Number::New(env, 0.0);
    }

    // Safe iteration
    double sum = 0.0;
    for (size_t i = safeStart; i < safeEnd; i++) {
        sum += ptr[i];
    }

    return Napi::Number::New(env, sum);
}

// GOOD: Multi-dimensional array bounds checking
Napi::Value SafeMatrixAccess(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float64Array matrix = info[0].As<Napi::Float64Array>();
    uint32_t rows = info[1].As<Napi::Number>().Uint32Value();
    uint32_t cols = info[2].As<Napi::Number>().Uint32Value();
    uint32_t row = info[3].As<Napi::Number>().Uint32Value();
    uint32_t col = info[4].As<Napi::Number>().Uint32Value();

    // Validate dimensions match array size
    size_t expectedSize = static_cast<size_t>(rows) * cols;
    if (matrix.ElementLength() < expectedSize) {
        Napi::RangeError::New(env, "Matrix dimensions exceed array size")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate indices
    if (row >= rows || col >= cols) {
        Napi::RangeError::New(env,
            "Matrix indices (" + std::to_string(row) + "," +
            std::to_string(col) + ") out of bounds for " +
            std::to_string(rows) + "x" + std::to_string(cols) + " matrix")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Safe access
    size_t index = static_cast<size_t>(row) * cols + col;
    return Napi::Number::New(env, matrix.Data()[index]);
}
```

## JavaScript Test Cases

```javascript
const addon = require('./build/Release/addon');

describe('Array Bounds Checking', () => {
    it('throws for out-of-bounds index', () => {
        const arr = [1, 2, 3];
        expect(() => addon.safeGetElement(arr, 10)).toThrow(/out of bounds/);
    });

    it('handles negative indices correctly', () => {
        const data = new Float64Array([1, 2, 3, 4, 5]);
        const sum = addon.safeSliceSum(data, -3, -1); // [3, 4]
        expect(sum).toBe(7);
    });

    it('throws for invalid matrix access', () => {
        const matrix = new Float64Array(9); // 3x3
        expect(() => addon.safeMatrixAccess(matrix, 3, 3, 5, 0))
            .toThrow(/out of bounds/);
    });
});
```
