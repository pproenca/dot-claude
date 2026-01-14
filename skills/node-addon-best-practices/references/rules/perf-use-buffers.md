---
title: Use Buffers to Bypass V8 Heap
impact: MEDIUM
impactDescription: 5-20x faster data transfer vs string/array marshaling
tags: perf, buffer, v8-heap, zero-copy, memory
---

# Use Buffers to Bypass V8 Heap

Node.js Buffers provide direct memory access without V8 heap involvement. Pass data via Buffer to avoid expensive copying and serialization that occurs with strings and arrays.

## Why This Matters

- Buffers use memory outside V8's managed heap
- `Buffer::Data()` returns a raw pointer - no copying
- Avoids V8's string encoding/decoding overhead
- Enables true zero-copy data sharing with C++

## Incorrect

Passing string data that requires conversion:

```cpp
#include <napi.h>
#include <string>
#include <algorithm>

// BAD: String data requires encoding conversion
Napi::Value ProcessTextData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Expensive: UTF-8 decoding, memory allocation, copying
    std::string input = info[0].As<Napi::String>().Utf8Value();

    // Process the data
    std::string result;
    result.reserve(input.size());

    for (char c : input) {
        if (std::isalnum(static_cast<unsigned char>(c))) {
            result.push_back(std::toupper(static_cast<unsigned char>(c)));
        }
    }

    // Expensive: UTF-8 encoding, memory allocation, copying back
    return Napi::String::New(env, result);
}

// BAD: Array of numbers requires element-by-element marshaling
Napi::Value ProcessNumbers(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    Napi::Array input = info[0].As<Napi::Array>();
    uint32_t length = input.Length();

    // Expensive: Each element access is a separate V8 call
    std::vector<double> data(length);
    for (uint32_t i = 0; i < length; i++) {
        data[i] = input.Get(i).As<Napi::Number>().DoubleValue();
    }

    // Process...
    double sum = 0;
    for (double val : data) {
        sum += val;
    }

    return Napi::Number::New(env, sum);
}
```

## Correct

Using Buffer for direct memory access:

```cpp
#include <napi.h>
#include <cstring>
#include <cctype>

// GOOD: Direct buffer access for binary/text data
Napi::Value ProcessBufferData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Zero-copy: Just get pointer to existing memory
    Napi::Buffer<uint8_t> input = info[0].As<Napi::Buffer<uint8_t>>();
    uint8_t* data = input.Data();
    size_t length = input.Length();

    // Create output buffer
    Napi::Buffer<uint8_t> output = Napi::Buffer<uint8_t>::New(env, length);
    uint8_t* outData = output.Data();

    // Process directly in buffer memory
    size_t outIndex = 0;
    for (size_t i = 0; i < length; i++) {
        if (std::isalnum(data[i])) {
            outData[outIndex++] = std::toupper(data[i]);
        }
    }

    // Return a view of the used portion
    return Napi::Buffer<uint8_t>::Copy(env, outData, outIndex);
}

// GOOD: TypedArray for numeric data
Napi::Value ProcessFloat64Array(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Direct access to Float64Array backing store
    Napi::Float64Array input = info[0].As<Napi::Float64Array>();
    double* data = input.Data();
    size_t length = input.ElementLength();

    // Process in-place or read directly
    double sum = 0.0;
    for (size_t i = 0; i < length; i++) {
        sum += data[i];
    }

    return Napi::Number::New(env, sum);
}

// GOOD: External buffer for large data without copying
Napi::Value CreateExternalBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();
    size_t size = info[0].As<Napi::Number>().Uint32Value();

    // Allocate memory that will be managed by the Buffer
    uint8_t* data = new uint8_t[size];
    std::memset(data, 0, size);

    // Create buffer with custom finalizer
    return Napi::Buffer<uint8_t>::New(
        env,
        data,
        size,
        [](Napi::Env /*env*/, uint8_t* ptr) {
            delete[] ptr;
        }
    );
}
```

## In-Place Modification Pattern

```cpp
#include <napi.h>
#include <cmath>

// GOOD: Modify buffer in-place for maximum efficiency
Napi::Value NormalizeInPlace(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float32Array data = info[0].As<Napi::Float32Array>();
    float* ptr = data.Data();
    size_t length = data.ElementLength();

    // Find min and max
    float minVal = ptr[0];
    float maxVal = ptr[0];
    for (size_t i = 1; i < length; i++) {
        if (ptr[i] < minVal) minVal = ptr[i];
        if (ptr[i] > maxVal) maxVal = ptr[i];
    }

    // Normalize in-place
    float range = maxVal - minVal;
    if (range > 0) {
        for (size_t i = 0; i < length; i++) {
            ptr[i] = (ptr[i] - minVal) / range;
        }
    }

    // Return the same array (modified in-place)
    return info[0];
}
```

## JavaScript Usage

```javascript
const addon = require('./build/Release/addon');

// Pass Buffer instead of string
const textBuffer = Buffer.from('Hello World 123!');
const processed = addon.processBufferData(textBuffer);

// Use Float64Array for numeric data
const numbers = new Float64Array([1.5, 2.5, 3.5, 4.5, 5.5]);
const sum = addon.processFloat64Array(numbers);

// In-place modification
const signal = new Float32Array([0, 50, 100, 150, 200]);
addon.normalizeInPlace(signal);
// signal is now [0, 0.25, 0.5, 0.75, 1]

// Create external buffer for large allocations
const largeBuffer = addon.createExternalBuffer(1024 * 1024);
```

## Buffer vs TypedArray

| Type | Use Case | Memory |
|------|----------|--------|
| `Buffer` | Binary data, I/O | External |
| `Uint8Array` | Byte arrays | ArrayBuffer |
| `Float32Array` | Audio, graphics | ArrayBuffer |
| `Float64Array` | Scientific data | ArrayBuffer |
| `Int32Array` | Integer math | ArrayBuffer |

All provide direct pointer access via `.Data()` method.
