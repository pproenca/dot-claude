---
title: Validate String Encoding Conversions
impact: LOW-MEDIUM
impactDescription: Prevents buffer overflows from multi-byte character expansion
tags: security, strings, encoding, utf8, validation
---

# Validate String Encoding Conversions

Respect buffer size parameters in string functions. UTF-8 encoding can expand characters (up to 4 bytes per character), so never assume string length equals byte length.

## Why This Matters

- UTF-8 characters vary from 1-4 bytes
- `string.length` in JavaScript counts code points, not bytes
- Fixed-size buffers can overflow with multi-byte characters
- Truncation in the middle of a multi-byte sequence corrupts data

## Incorrect

Assuming string fits in fixed buffer:

```cpp
#include <napi.h>
#include <cstring>

// BAD: Fixed buffer size without validation
Napi::Value ProcessString(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::String input = info[0].As<Napi::String>();

    // DANGER: Fixed buffer, string might be longer
    char buffer[256];

    // Could overflow buffer with long strings
    std::string str = input.Utf8Value();
    std::strcpy(buffer, str.c_str());  // UNSAFE

    // Process buffer...
    return Napi::String::New(env, buffer);
}

// BAD: Using JS string length for buffer allocation
Napi::Value CopyToBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::String input = info[0].As<Napi::String>();

    // JavaScript length counts code points, not bytes
    size_t jsLength = input.Utf8Value().length();  // Wrong approach

    // This might not be enough for UTF-8 encoding
    // "Hello" = 5 chars = 5 bytes (OK)
    // "日本語" = 3 chars = 9 bytes (WRONG)
    char* buffer = new char[jsLength + 1];

    // Potential overflow
    std::strcpy(buffer, input.Utf8Value().c_str());

    // ...
    delete[] buffer;
    return env.Undefined();
}
```

## Correct

Query byte length first, then allocate:

```cpp
#include <napi.h>
#include <vector>
#include <string>

// GOOD: Get byte length, then allocate appropriately
Napi::Value SafeProcessString(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    if (!info[0].IsString()) {
        Napi::TypeError::New(env, "Expected string argument")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::String input = info[0].As<Napi::String>();

    // Get the actual UTF-8 byte length
    std::string utf8Str = input.Utf8Value();
    size_t byteLength = utf8Str.size();

    // Now allocate with correct size
    std::vector<char> buffer(byteLength + 1);
    std::memcpy(buffer.data(), utf8Str.c_str(), byteLength + 1);

    // Process safely...
    for (size_t i = 0; i < byteLength; i++) {
        if (buffer[i] >= 'a' && buffer[i] <= 'z') {
            buffer[i] = buffer[i] - 'a' + 'A';
        }
    }

    return Napi::String::New(env, buffer.data());
}

// GOOD: Use N-API to get byte length before copying
Napi::Value SafeCopyToBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::String input = info[0].As<Napi::String>();

    // Query the byte length first
    size_t byteLength;
    napi_status status = napi_get_value_string_utf8(
        env,
        input,
        nullptr,    // Pass nullptr to get length only
        0,
        &byteLength
    );

    if (status != napi_ok) {
        Napi::Error::New(env, "Failed to get string length")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Allocate with exact size
    std::vector<char> buffer(byteLength + 1);

    // Now copy with known bounds
    size_t copied;
    status = napi_get_value_string_utf8(
        env,
        input,
        buffer.data(),
        buffer.size(),
        &copied
    );

    if (status != napi_ok || copied != byteLength) {
        Napi::Error::New(env, "Failed to copy string")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Process buffer safely...
    return Napi::Buffer<char>::Copy(env, buffer.data(), byteLength);
}

// GOOD: Validate output buffer size for user-provided buffer
Napi::Value WriteToUserBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::String input = info[0].As<Napi::String>();
    Napi::Buffer<char> outputBuffer = info[1].As<Napi::Buffer<char>>();

    std::string utf8Str = input.Utf8Value();
    size_t byteLength = utf8Str.size();
    size_t bufferSize = outputBuffer.Length();

    // Check if buffer is large enough
    if (bufferSize < byteLength + 1) {
        Napi::RangeError::New(env,
            "Buffer too small: need " + std::to_string(byteLength + 1) +
            " bytes, got " + std::to_string(bufferSize))
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Safe copy
    std::memcpy(outputBuffer.Data(), utf8Str.c_str(), byteLength + 1);

    return Napi::Number::New(env, static_cast<double>(byteLength));
}
```

## Multi-Byte Character Handling

```cpp
#include <napi.h>
#include <string>
#include <locale>
#include <codecvt>

// GOOD: Proper UTF-8 character counting
Napi::Value CountCharacters(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    std::string utf8Str = info[0].As<Napi::String>().Utf8Value();

    // Count UTF-8 code points (characters), not bytes
    size_t charCount = 0;
    size_t byteCount = utf8Str.size();

    for (size_t i = 0; i < byteCount; ) {
        unsigned char c = utf8Str[i];

        // Determine character byte length from leading byte
        size_t charBytes;
        if ((c & 0x80) == 0) {
            charBytes = 1;  // ASCII
        } else if ((c & 0xE0) == 0xC0) {
            charBytes = 2;  // 2-byte UTF-8
        } else if ((c & 0xF0) == 0xE0) {
            charBytes = 3;  // 3-byte UTF-8
        } else if ((c & 0xF8) == 0xF0) {
            charBytes = 4;  // 4-byte UTF-8
        } else {
            // Invalid UTF-8 sequence
            Napi::Error::New(env, "Invalid UTF-8 sequence")
                .ThrowAsJavaScriptException();
            return env.Undefined();
        }

        // Validate we have enough bytes
        if (i + charBytes > byteCount) {
            Napi::Error::New(env, "Truncated UTF-8 sequence")
                .ThrowAsJavaScriptException();
            return env.Undefined();
        }

        i += charBytes;
        charCount++;
    }

    Napi::Object result = Napi::Object::New(env);
    result.Set("characters", static_cast<double>(charCount));
    result.Set("bytes", static_cast<double>(byteCount));
    return result;
}

// GOOD: Safe truncation at character boundaries
Napi::Value SafeTruncate(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    std::string utf8Str = info[0].As<Napi::String>().Utf8Value();
    size_t maxBytes = info[1].As<Napi::Number>().Uint32Value();

    if (utf8Str.size() <= maxBytes) {
        return Napi::String::New(env, utf8Str);
    }

    // Find a valid truncation point (don't split multi-byte chars)
    size_t truncateAt = maxBytes;
    while (truncateAt > 0) {
        unsigned char c = utf8Str[truncateAt];

        // If this is not a continuation byte, it's a valid boundary
        if ((c & 0xC0) != 0x80) {
            break;
        }
        truncateAt--;
    }

    return Napi::String::New(env, utf8Str.substr(0, truncateAt));
}
```

## JavaScript Test Cases

```javascript
const addon = require('./build/Release/addon');

describe('String Encoding Safety', () => {
    it('handles multi-byte UTF-8 correctly', () => {
        const input = '日本語テスト';  // 6 chars, 18 bytes
        const result = addon.countCharacters(input);

        expect(result.characters).toBe(6);
        expect(result.bytes).toBe(18);
    });

    it('truncates at character boundaries', () => {
        const input = '日本語';  // 9 bytes
        const truncated = addon.safeTruncate(input, 6);

        // Should truncate to '日本' (6 bytes), not corrupt middle of char
        expect(truncated).toBe('日本');
    });

    it('rejects buffer too small', () => {
        const input = '日本語';
        const buffer = Buffer.alloc(5);  // Too small for 9 bytes

        expect(() => addon.writeToUserBuffer(input, buffer))
            .toThrow(/too small/);
    });
});
```
