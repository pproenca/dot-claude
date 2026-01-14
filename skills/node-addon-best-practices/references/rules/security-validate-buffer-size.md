---
title: Validate Buffer Sizes Before Use
impact: LOW-MEDIUM
impactDescription: Prevents buffer overflow vulnerabilities and crashes
tags: security, buffer, validation, bounds, memory-safety
---

# Validate Buffer Sizes Before Use

Always verify buffer sizes before accessing data. Never trust caller-provided size parameters without validation against the actual allocated buffer size.

## Why This Matters

- Buffer overflows lead to crashes and security vulnerabilities
- Malicious callers can provide incorrect sizes
- Memory corruption can cause data leaks
- Off-by-one errors are common in size calculations

## Incorrect

Trusting caller-provided size without validation:

```cpp
#include <napi.h>
#include <cstring>

// BAD: Trusts the caller-provided size
Napi::Value CopyData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Buffer<uint8_t> source = info[0].As<Napi::Buffer<uint8_t>>();
    Napi::Buffer<uint8_t> dest = info[1].As<Napi::Buffer<uint8_t>>();
    // Caller says how many bytes to copy - NOT VALIDATED
    size_t size = info[2].As<Napi::Number>().Uint32Value();

    // DANGER: Could read beyond source or write beyond dest
    std::memcpy(dest.Data(), source.Data(), size);

    return env.Undefined();
}

// BAD: No validation of offset parameter
Napi::Value ReadAtOffset(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();
    size_t offset = info[1].As<Napi::Number>().Uint32Value();

    // DANGER: Offset could be beyond buffer bounds
    uint32_t value = *reinterpret_cast<uint32_t*>(buffer.Data() + offset);

    return Napi::Number::New(env, value);
}
```

## Correct

Validate all size and offset parameters:

```cpp
#include <napi.h>
#include <cstring>
#include <algorithm>

// GOOD: Validate buffer sizes before operations
Napi::Value SafeCopyData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Validate argument count
    if (info.Length() < 3) {
        Napi::TypeError::New(env, "Expected 3 arguments: source, dest, size")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Validate argument types
    if (!info[0].IsBuffer() || !info[1].IsBuffer() || !info[2].IsNumber()) {
        Napi::TypeError::New(env, "Invalid argument types")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Buffer<uint8_t> source = info[0].As<Napi::Buffer<uint8_t>>();
    Napi::Buffer<uint8_t> dest = info[1].As<Napi::Buffer<uint8_t>>();
    size_t requestedSize = info[2].As<Napi::Number>().Uint32Value();

    // Get actual buffer sizes
    size_t sourceSize = source.Length();
    size_t destSize = dest.Length();

    // Validate requested size against actual sizes
    if (requestedSize > sourceSize) {
        Napi::RangeError::New(env,
            "Requested size exceeds source buffer length")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    if (requestedSize > destSize) {
        Napi::RangeError::New(env,
            "Requested size exceeds destination buffer length")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Safe to copy now
    std::memcpy(dest.Data(), source.Data(), requestedSize);

    return Napi::Number::New(env, static_cast<double>(requestedSize));
}

// GOOD: Validate offset and ensure read stays within bounds
Napi::Value SafeReadAtOffset(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 2 || !info[0].IsBuffer() || !info[1].IsNumber()) {
        Napi::TypeError::New(env, "Expected (buffer, offset)")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();
    size_t offset = info[1].As<Napi::Number>().Uint32Value();
    size_t bufferLength = buffer.Length();

    // Validate: offset + sizeof(uint32_t) must not exceed buffer length
    constexpr size_t valueSize = sizeof(uint32_t);

    if (offset > bufferLength || bufferLength - offset < valueSize) {
        Napi::RangeError::New(env,
            "Offset would read beyond buffer bounds")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    uint32_t value = *reinterpret_cast<uint32_t*>(buffer.Data() + offset);

    return Napi::Number::New(env, value);
}

// GOOD: Safe slice operation with bounds validation
Napi::Value SafeSlice(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (info.Length() < 3) {
        Napi::TypeError::New(env, "Expected (buffer, start, end)")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();
    int64_t start = info[1].As<Napi::Number>().Int64Value();
    int64_t end = info[2].As<Napi::Number>().Int64Value();
    size_t length = buffer.Length();

    // Handle negative indices (like JS slice)
    if (start < 0) {
        start = std::max<int64_t>(0, static_cast<int64_t>(length) + start);
    }
    if (end < 0) {
        end = std::max<int64_t>(0, static_cast<int64_t>(length) + end);
    }

    // Clamp to valid range
    size_t safeStart = std::min(static_cast<size_t>(start), length);
    size_t safeEnd = std::min(static_cast<size_t>(end), length);

    // Ensure start <= end
    if (safeStart > safeEnd) {
        safeEnd = safeStart;
    }

    size_t sliceLength = safeEnd - safeStart;

    return Napi::Buffer<uint8_t>::Copy(
        env,
        buffer.Data() + safeStart,
        sliceLength
    );
}
```

## Helper Functions for Validation

```cpp
#include <napi.h>
#include <stdexcept>

// Utility class for safe buffer operations
class SafeBuffer {
public:
    SafeBuffer(Napi::Buffer<uint8_t>& buffer)
        : data_(buffer.Data()), length_(buffer.Length()) {}

    uint8_t readU8(size_t offset) const {
        validateRead(offset, 1);
        return data_[offset];
    }

    uint32_t readU32LE(size_t offset) const {
        validateRead(offset, 4);
        return *reinterpret_cast<const uint32_t*>(data_ + offset);
    }

    void writeU8(size_t offset, uint8_t value) {
        validateWrite(offset, 1);
        data_[offset] = value;
    }

    void writeU32LE(size_t offset, uint32_t value) {
        validateWrite(offset, 4);
        *reinterpret_cast<uint32_t*>(data_ + offset) = value;
    }

    size_t length() const { return length_; }

private:
    void validateRead(size_t offset, size_t size) const {
        if (offset > length_ || length_ - offset < size) {
            throw std::out_of_range("Buffer read out of bounds");
        }
    }

    void validateWrite(size_t offset, size_t size) {
        if (offset > length_ || length_ - offset < size) {
            throw std::out_of_range("Buffer write out of bounds");
        }
    }

    uint8_t* data_;
    size_t length_;
};

// Usage
Napi::Value UsesSafeBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    try {
        Napi::Buffer<uint8_t> buffer = info[0].As<Napi::Buffer<uint8_t>>();
        SafeBuffer safe(buffer);

        uint32_t header = safe.readU32LE(0);
        uint8_t flags = safe.readU8(4);

        return Napi::Number::New(env, header);
    } catch (const std::out_of_range& e) {
        Napi::RangeError::New(env, e.what())
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }
}
```

## JavaScript Test Cases

```javascript
const addon = require('./build/Release/addon');

// Test buffer validation
describe('Buffer Safety', () => {
    it('rejects size larger than source', () => {
        const source = Buffer.from([1, 2, 3]);
        const dest = Buffer.alloc(10);

        expect(() => addon.safeCopyData(source, dest, 100))
            .toThrow(/source buffer/);
    });

    it('rejects offset beyond bounds', () => {
        const buffer = Buffer.from([1, 2, 3, 4]);

        expect(() => addon.safeReadAtOffset(buffer, 100))
            .toThrow(/bounds/);
    });
});
```
