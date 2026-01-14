---
title: Consider cmake-js for CMake Projects
impact: MEDIUM
impactDescription: Enables unified build system when C++ dependencies use CMake
tags: build, cmake, cmake-js, integration, cross-platform
---

# Consider cmake-js for CMake Projects

When your C++ dependencies already use CMake, use cmake-js instead of node-gyp. This avoids duplicating build configuration and leverages CMake's superior dependency management.

## Why This Matters

- Single build system for all C++ code
- Better IDE integration (CLion, VS Code CMake Tools)
- Superior dependency management with find_package
- Modern CMake target-based approach
- FetchContent for automatic dependency downloads

## Incorrect

Duplicating build configuration in both systems:

```python
# binding.gyp - Duplicates what CMakeLists.txt already defines
{
    "targets": [{
        "target_name": "addon",
        "sources": ["src/addon.cpp"],
        "include_dirs": [
            "/usr/local/include/mylib",
            "deps/otherlib/include"
        ],
        "libraries": [
            "-L/usr/local/lib",
            "-lmylib",
            "-lotherlib"
        ],
        "conditions": [
            # Platform-specific paths duplicated from CMakeLists.txt
        ]
    }]
}
```

```cmake
# CMakeLists.txt - Already has all this information
find_package(MyLib REQUIRED)
find_package(OtherLib REQUIRED)
# ...configuration duplicated in binding.gyp
```

## Correct

Use cmake-js with CMakeLists.txt:

```json
// package.json
{
    "name": "my-cmake-addon",
    "version": "1.0.0",
    "main": "lib/index.js",
    "scripts": {
        "install": "cmake-js compile",
        "build": "cmake-js build",
        "rebuild": "cmake-js rebuild",
        "clean": "cmake-js clean",
        "build:debug": "cmake-js build --debug"
    },
    "dependencies": {
        "node-addon-api": "^7.0.0"
    },
    "devDependencies": {
        "cmake-js": "^7.0.0"
    },
    "cmake-js": {
        "runtime": "node",
        "runtimeVersion": "20.0.0",
        "arch": "x64"
    }
}
```

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(my_addon)

# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include cmake-js helpers
include_directories(${CMAKE_JS_INC})

# Find node-addon-api
execute_process(
    COMMAND node -p "require('node-addon-api').include"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    OUTPUT_VARIABLE NODE_ADDON_API_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
string(REGEX REPLACE "[\"\n]" "" NODE_ADDON_API_DIR ${NODE_ADDON_API_DIR})

# Add your dependencies using standard CMake
find_package(OpenSSL REQUIRED)
find_package(ZLIB REQUIRED)

# Or use FetchContent for header-only libraries
include(FetchContent)
FetchContent_Declare(
    json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.2
)
FetchContent_MakeAvailable(json)

# Define the addon target
add_library(${PROJECT_NAME} SHARED
    src/addon.cpp
    src/crypto_wrapper.cpp
    src/compression.cpp
)

# Set the output name and extension
set_target_properties(${PROJECT_NAME} PROPERTIES
    PREFIX ""
    SUFFIX ".node"
    OUTPUT_NAME "addon"
)

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE
    ${NODE_ADDON_API_DIR}
    ${CMAKE_JS_INC}
)

# Link libraries
target_link_libraries(${PROJECT_NAME} PRIVATE
    ${CMAKE_JS_LIB}
    OpenSSL::SSL
    OpenSSL::Crypto
    ZLIB::ZLIB
    nlohmann_json::nlohmann_json
)

# N-API version
target_compile_definitions(${PROJECT_NAME} PRIVATE
    NAPI_VERSION=8
)

# Platform-specific settings
if(MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE /W4)
else()
    target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra)
endif()
```

```cpp
// src/addon.cpp
#include <napi.h>
#include <openssl/sha.h>
#include <zlib.h>
#include <nlohmann/json.hpp>

Napi::Value ComputeSHA256(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Buffer<uint8_t> input = info[0].As<Napi::Buffer<uint8_t>>();

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(input.Data(), input.Length(), hash);

    return Napi::Buffer<uint8_t>::Copy(env, hash, SHA256_DIGEST_LENGTH);
}

Napi::Value CompressData(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    Napi::Buffer<uint8_t> input = info[0].As<Napi::Buffer<uint8_t>>();

    uLongf destLen = compressBound(input.Length());
    std::vector<uint8_t> compressed(destLen);

    int result = compress(
        compressed.data(), &destLen,
        input.Data(), input.Length()
    );

    if (result != Z_OK) {
        Napi::Error::New(env, "Compression failed").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    return Napi::Buffer<uint8_t>::Copy(env, compressed.data(), destLen);
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    exports.Set("sha256", Napi::Function::New(env, ComputeSHA256));
    exports.Set("compress", Napi::Function::New(env, CompressData));
    return exports;
}

NODE_API_MODULE(addon, Init)
```

## Project Structure with CMake

```
my-cmake-addon/
├── CMakeLists.txt
├── package.json
├── lib/
│   └── index.js
├── src/
│   ├── addon.cpp
│   ├── crypto_wrapper.cpp
│   └── compression.cpp
├── include/
│   └── addon.h
├── build/                    # CMake build directory
│   └── Release/
│       └── addon.node
└── test/
    └── test.js
```

## Build Commands

```bash
# Standard build
npm install

# Rebuild with verbose output
cmake-js rebuild --log-level verbose

# Debug build
npm run build:debug

# Specify generator
cmake-js build --generator "Ninja"

# Pass CMake options
cmake-js build --CDMY_OPTION=ON

# Build for specific architecture
cmake-js build --arch x64
```

## When to Use cmake-js vs node-gyp

| Scenario | Recommended |
|----------|-------------|
| Simple addon, no deps | node-gyp |
| C++ deps already use CMake | cmake-js |
| Need FetchContent | cmake-js |
| Complex find_package needs | cmake-js |
| Maximum compatibility | node-gyp |
| IDE integration priority | cmake-js |
