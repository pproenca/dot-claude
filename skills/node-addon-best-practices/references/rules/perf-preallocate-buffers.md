---
title: Preallocate Result Buffers
impact: MEDIUM
impactDescription: Eliminates allocation overhead, enables buffer pooling patterns
tags: perf, allocation, buffers, memory-reuse, zero-copy
---

# Preallocate Result Buffers

Accept pre-allocated Buffers from JavaScript and write results directly into them. This eliminates allocation overhead in C++ and enables buffer pooling on the JavaScript side.

## Why This Matters

- Allocation is expensive, especially for large buffers
- JavaScript can pool and reuse buffers across multiple calls
- Eliminates garbage collection pressure
- Enables true zero-copy data flows

## Incorrect

Allocating new buffers in C++ for each call:

```cpp
#include <napi.h>
#include <cstring>
#include <cmath>

// BAD: Allocates new buffer every call
Napi::Value GenerateSignal(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    uint32_t sampleCount = info[0].As<Napi::Number>().Uint32Value();
    double frequency = info[1].As<Napi::Number>().DoubleValue();
    double sampleRate = info[2].As<Napi::Number>().DoubleValue();

    // Allocation happens every call - expensive!
    Napi::Float32Array output = Napi::Float32Array::New(env, sampleCount);
    float* data = output.Data();

    double phase = 0.0;
    double phaseIncrement = 2.0 * M_PI * frequency / sampleRate;

    for (uint32_t i = 0; i < sampleCount; i++) {
        data[i] = static_cast<float>(std::sin(phase));
        phase += phaseIncrement;
    }

    return output;
}

// BAD: Returns new buffer for transformed data
Napi::Value ApplyGain(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float32Array input = info[0].As<Napi::Float32Array>();
    float gain = info[1].As<Napi::Number>().FloatValue();
    size_t length = input.ElementLength();

    // New allocation for output
    Napi::Float32Array output = Napi::Float32Array::New(env, length);

    float* inData = input.Data();
    float* outData = output.Data();

    for (size_t i = 0; i < length; i++) {
        outData[i] = inData[i] * gain;
    }

    return output;
}
```

## Correct

Accept pre-allocated buffer from JavaScript:

```cpp
#include <napi.h>
#include <cmath>

// GOOD: Write into caller-provided buffer
Napi::Value GenerateSignalInPlace(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Caller provides the output buffer
    Napi::Float32Array output = info[0].As<Napi::Float32Array>();
    double frequency = info[1].As<Napi::Number>().DoubleValue();
    double sampleRate = info[2].As<Napi::Number>().DoubleValue();

    float* data = output.Data();
    size_t sampleCount = output.ElementLength();

    double phase = 0.0;
    double phaseIncrement = 2.0 * M_PI * frequency / sampleRate;

    for (size_t i = 0; i < sampleCount; i++) {
        data[i] = static_cast<float>(std::sin(phase));
        phase += phaseIncrement;
    }

    // Return bytes written (useful if output size varies)
    return Napi::Number::New(env, static_cast<double>(sampleCount));
}

// GOOD: Transform in-place or into provided buffer
Napi::Value ApplyGainInPlace(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float32Array buffer = info[0].As<Napi::Float32Array>();
    float gain = info[1].As<Napi::Number>().FloatValue();

    float* data = buffer.Data();
    size_t length = buffer.ElementLength();

    // Modify in-place - zero allocations
    for (size_t i = 0; i < length; i++) {
        data[i] *= gain;
    }

    return env.Undefined();
}

// GOOD: Separate input and output buffers, both provided by caller
Napi::Value ConvolveIntoBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Float32Array input = info[0].As<Napi::Float32Array>();
    Napi::Float32Array kernel = info[1].As<Napi::Float32Array>();
    Napi::Float32Array output = info[2].As<Napi::Float32Array>();

    float* inData = input.Data();
    float* kernelData = kernel.Data();
    float* outData = output.Data();

    size_t inputLen = input.ElementLength();
    size_t kernelLen = kernel.ElementLength();
    size_t outputLen = output.ElementLength();

    // Verify output buffer is large enough
    size_t requiredLen = inputLen + kernelLen - 1;
    if (outputLen < requiredLen) {
        Napi::TypeError::New(env, "Output buffer too small").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Clear output buffer
    std::memset(outData, 0, outputLen * sizeof(float));

    // Convolution
    for (size_t i = 0; i < inputLen; i++) {
        for (size_t j = 0; j < kernelLen; j++) {
            outData[i + j] += inData[i] * kernelData[j];
        }
    }

    return Napi::Number::New(env, static_cast<double>(requiredLen));
}
```

## Buffer Pool Pattern in JavaScript

```javascript
const addon = require('./build/Release/addon');

class BufferPool {
    constructor(bufferSize, poolSize = 4) {
        this.buffers = [];
        this.available = [];

        for (let i = 0; i < poolSize; i++) {
            const buffer = new Float32Array(bufferSize);
            this.buffers.push(buffer);
            this.available.push(i);
        }
    }

    acquire() {
        if (this.available.length === 0) {
            // Pool exhausted - create temporary buffer
            return { buffer: new Float32Array(this.buffers[0].length), pooled: false };
        }
        const idx = this.available.pop();
        return { buffer: this.buffers[idx], pooled: true, idx };
    }

    release(handle) {
        if (handle.pooled) {
            this.available.push(handle.idx);
        }
    }
}

// Usage with buffer pool
const pool = new BufferPool(4096, 8);

function generateTone(frequency, sampleRate) {
    const handle = pool.acquire();
    try {
        addon.generateSignalInPlace(handle.buffer, frequency, sampleRate);
        // Process the buffer...
        return handle.buffer.slice(); // Copy if needed beyond this scope
    } finally {
        pool.release(handle);
    }
}

// Ring buffer pattern for streaming
class RingBuffer {
    constructor(size) {
        this.buffer = new Float32Array(size);
        this.writePos = 0;
        this.readPos = 0;
    }

    getWriteBuffer(samples) {
        // Return view into ring buffer for direct writes
        return new Float32Array(
            this.buffer.buffer,
            this.writePos * 4,
            samples
        );
    }

    commitWrite(samples) {
        this.writePos = (this.writePos + samples) % this.buffer.length;
    }
}

const ringBuffer = new RingBuffer(16384);
const writeView = ringBuffer.getWriteBuffer(1024);
addon.generateSignalInPlace(writeView, 440, 44100);
ringBuffer.commitWrite(1024);
```

## Variable-Length Output Pattern

```cpp
#include <napi.h>

// GOOD: Return actual bytes written when output size varies
Napi::Value CompressData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Buffer<uint8_t> input = info[0].As<Napi::Buffer<uint8_t>>();
    Napi::Buffer<uint8_t> output = info[1].As<Napi::Buffer<uint8_t>>();

    uint8_t* inData = input.Data();
    size_t inLen = input.Length();
    uint8_t* outData = output.Data();
    size_t outCapacity = output.Length();

    // Simulate compression (actual implementation would use zlib, etc.)
    size_t bytesWritten = 0;
    // ... compression logic ...

    // Return actual bytes written
    return Napi::Number::New(env, static_cast<double>(bytesWritten));
}
```

## Performance Benefits

| Pattern | Allocation | GC Pressure | Reusability |
|---------|-----------|-------------|-------------|
| New buffer per call | Every call | High | None |
| Caller-provided | None | None | Full |
| Buffer pool | Initial only | Minimal | Full |
