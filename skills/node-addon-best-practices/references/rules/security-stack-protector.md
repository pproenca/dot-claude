---
title: Enable Stack Protectors in Build
impact: LOW-MEDIUM
impactDescription: Detects and prevents stack buffer overflow exploits
tags: security, stack-protector, compilation, hardening, overflow
---

# Enable Stack Protectors in Build

Compile with `-fstack-protector-strong` to detect stack buffer overflows at runtime. This adds canary values that are checked before function returns.

## Why This Matters

- Detects stack-based buffer overflows
- Prevents return address overwrites
- Crashes immediately rather than allowing exploitation
- Minimal performance impact (~1-2%)

## Incorrect

Building without stack protection:

```python
# binding.gyp - No security hardening
{
    "targets": [{
        "target_name": "addon",
        "sources": ["src/addon.cpp"],
        "cflags": []  # No protection
    }]
}
```

```cpp
// Vulnerable code without protection
#include <napi.h>
#include <cstring>

Napi::Value VulnerableFunction(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Stack buffer vulnerable to overflow
    char buffer[64];

    std::string input = info[0].As<Napi::String>().Utf8Value();

    // DANGEROUS: Could overflow buffer
    std::strcpy(buffer, input.c_str());

    return Napi::String::New(env, buffer);
}
```

## Correct

Enable stack protector and other security flags:

```python
# binding.gyp - Security-hardened build
{
    "targets": [{
        "target_name": "addon",
        "sources": ["src/addon.cpp"],
        "include_dirs": [
            "<!@(node -p \"require('node-addon-api').include\")"
        ],
        "defines": ["NAPI_VERSION=8"],
        "cflags": [
            "-fstack-protector-strong",
            "-D_FORTIFY_SOURCE=2",
            "-fPIE"
        ],
        "cflags_cc": [
            "-fstack-protector-strong",
            "-D_FORTIFY_SOURCE=2",
            "-fPIE"
        ],
        "ldflags": [
            "-pie",
            "-Wl,-z,relro",
            "-Wl,-z,now"
        ],
        "conditions": [
            ["OS=='linux'", {
                "ldflags": [
                    "-Wl,-z,noexecstack"
                ]
            }],
            ["OS=='mac'", {
                "xcode_settings": {
                    "OTHER_CFLAGS": [
                        "-fstack-protector-strong"
                    ]
                }
            }],
            ["OS=='win'", {
                "msvs_settings": {
                    "VCCLCompilerTool": {
                        "BufferSecurityCheck": "true",
                        "RuntimeLibrary": 2
                    },
                    "VCLinkerTool": {
                        "DataExecutionPrevention": 2,
                        "RandomizedBaseAddress": 2
                    }
                }
            }]
        ]
    }]
}
```

```cpp
// Code with safe practices (stack protector still adds extra safety)
#include <napi.h>
#include <string>
#include <vector>

Napi::Value SafeFunction(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Use std::string instead of fixed buffer
    std::string input = info[0].As<Napi::String>().Utf8Value();

    // Input validation
    if (input.length() > 1024) {
        Napi::RangeError::New(env, "Input too long")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Process safely
    std::string result = input;
    for (char& c : result) {
        c = std::toupper(static_cast<unsigned char>(c));
    }

    return Napi::String::New(env, result);
}

// If you must use fixed buffers, use safe functions
Napi::Value SafeFixedBuffer(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    constexpr size_t BUFFER_SIZE = 64;
    char buffer[BUFFER_SIZE];

    std::string input = info[0].As<Napi::String>().Utf8Value();

    // Check length before copy
    if (input.length() >= BUFFER_SIZE) {
        Napi::RangeError::New(env,
            "Input exceeds buffer size of " + std::to_string(BUFFER_SIZE - 1))
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    // Use safe copy with size limit
    std::strncpy(buffer, input.c_str(), BUFFER_SIZE - 1);
    buffer[BUFFER_SIZE - 1] = '\0';  // Ensure null termination

    return Napi::String::New(env, buffer);
}
```

## CMake Security Configuration

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(addon)

add_library(addon SHARED src/addon.cpp)

# Security hardening flags
if(NOT MSVC)
    target_compile_options(addon PRIVATE
        -fstack-protector-strong
        -fPIE
        -D_FORTIFY_SOURCE=2
    )

    target_link_options(addon PRIVATE
        -pie
        -Wl,-z,relro
        -Wl,-z,now
    )

    if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        target_link_options(addon PRIVATE
            -Wl,-z,noexecstack
        )
    endif()
else()
    # MSVC security flags
    target_compile_options(addon PRIVATE
        /GS           # Buffer security check
        /DYNAMICBASE  # ASLR
        /NXCOMPAT     # DEP
    )
endif()

# Additional hardening for release builds
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    if(NOT MSVC)
        target_compile_options(addon PRIVATE
            -fstack-clash-protection  # GCC 8+
        )
    endif()
endif()
```

## Security Flags Reference

### GCC/Clang Flags

| Flag | Purpose |
|------|---------|
| `-fstack-protector` | Basic stack protection |
| `-fstack-protector-strong` | Stronger protection (recommended) |
| `-fstack-protector-all` | Maximum protection (performance cost) |
| `-D_FORTIFY_SOURCE=2` | Runtime buffer overflow checks |
| `-fPIE` | Position Independent Executable |
| `-fstack-clash-protection` | Prevents stack clash attacks |

### Linker Flags

| Flag | Purpose |
|------|---------|
| `-pie` | Enable ASLR for executable |
| `-Wl,-z,relro` | Partial RELRO (GOT protection) |
| `-Wl,-z,now` | Full RELRO (resolve all symbols at load) |
| `-Wl,-z,noexecstack` | Non-executable stack |

### MSVC Flags

| Flag | Purpose |
|------|---------|
| `/GS` | Buffer security check |
| `/DYNAMICBASE` | Enable ASLR |
| `/NXCOMPAT` | Data Execution Prevention |
| `/GUARD:CF` | Control Flow Guard |

## Verifying Protection

```bash
# Check if stack protector is enabled (Linux)
readelf -s build/Release/addon.node | grep stack_chk

# Check for RELRO (Linux)
readelf -l build/Release/addon.node | grep GNU_RELRO

# Check for NX (Linux)
readelf -W -l build/Release/addon.node | grep GNU_STACK

# macOS: Check for stack canary
otool -Iv build/Release/addon.node | grep stack_chk
```

## Stack Protector Behavior

When a buffer overflow is detected:

```
*** stack smashing detected ***: terminated
Aborted (core dumped)
```

This immediate termination prevents exploitation but note:
- Process crashes (not graceful)
- Should be combined with proper input validation
- Is a last line of defense, not primary protection
