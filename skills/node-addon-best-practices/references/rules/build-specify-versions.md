---
title: Specify Supported Node Versions
impact: MEDIUM
impactDescription: Prevents runtime crashes from N-API version mismatches
tags: build, versions, compatibility, napi, engines
---

# Specify Supported Node Versions

Document the minimum Node.js and N-API versions your addon supports. This prevents users from encountering cryptic runtime errors on unsupported versions.

## Why This Matters

- N-API versions add new functions; using newer APIs breaks older Node.js
- ABI stability depends on correct N-API version targeting
- Users see clear error messages instead of crashes
- npm can warn users before installation

## Incorrect

No version constraints or documentation:

```json
// package.json - No version information
{
    "name": "my-addon",
    "version": "1.0.0"
}
```

```cpp
// Using newer N-API features without version guards
#include <napi.h>

// napi_type_tag_object added in N-API 8
// Will crash on Node.js < 14.17.0
void TypeTagObject(Napi::Env env, Napi::Object obj) {
    napi_type_tag tag = { 0x1234, 0x5678 };
    napi_type_tag_object(env, obj, &tag);
}
```

## Correct

Explicit version constraints in package.json:

```json
// package.json
{
    "name": "my-addon",
    "version": "2.0.0",
    "description": "High-performance native addon",
    "engines": {
        "node": ">=18.0.0"
    },
    "napi": {
        "targets": [
            "napi"
        ]
    },
    "binary": {
        "napi_versions": [8]
    },
    "repository": {
        "type": "git",
        "url": "https://github.com/example/my-addon.git"
    },
    "readme": "README.md"
}
```

```python
# binding.gyp - Specify N-API version
{
    "targets": [{
        "target_name": "addon",
        "sources": ["src/addon.cpp"],
        "include_dirs": [
            "<!@(node -p \"require('node-addon-api').include\")"
        ],
        "defines": [
            "NAPI_VERSION=8"
        ],
        "cflags!": ["-fno-exceptions"],
        "cflags_cc!": ["-fno-exceptions"]
    }]
}
```

```cpp
// src/addon.cpp - Version-guarded features
#include <napi.h>

// Check N-API version at compile time
#if NAPI_VERSION < 8
#error "This addon requires N-API version 8 or higher"
#endif

// Runtime version check
Napi::Value GetVersionInfo(const Napi::CallbackInfo& info) {
    Napi::Env env = info.Env();

    // Get runtime N-API version
    uint32_t napiVersion;
    napi_status status = napi_get_version(env, &napiVersion);

    if (status != napi_ok) {
        Napi::Error::New(env, "Failed to get N-API version")
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }

    Napi::Object result = Napi::Object::New(env);
    result.Set("napiVersion", napiVersion);
    result.Set("compiledVersion", NAPI_VERSION);
    result.Set("nodeVersion", Napi::String::New(env, NODE_VERSION));
    return result;
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    exports.Set("getVersionInfo", Napi::Function::New(env, GetVersionInfo));
    return exports;
}

NODE_API_MODULE(addon, Init)
```

## Version Compatibility Documentation

```markdown
<!-- README.md -->
# my-addon

## Requirements

| Requirement | Minimum Version |
|------------|-----------------|
| Node.js | 18.0.0 |
| N-API | 8 |
| npm | 8.0.0 |

### Node.js Version Support

| Node.js | N-API | Status |
|---------|-------|--------|
| 22.x | 9 | Supported |
| 20.x | 9 | Supported |
| 18.x | 8 | Supported |
| 16.x | 8 | Deprecated |
| 14.x | 7 | Not supported |

### Platform Support

| Platform | Architecture | Status |
|----------|-------------|--------|
| Linux | x64 | Supported |
| Linux | arm64 | Supported |
| macOS | x64 | Supported |
| macOS | arm64 | Supported |
| Windows | x64 | Supported |
```

## JavaScript Version Check

```javascript
// index.js - Runtime version validation
const semver = require('semver');
const packageJson = require('./package.json');

// Check Node.js version
const minNodeVersion = packageJson.engines?.node?.replace('>=', '');
if (minNodeVersion && !semver.gte(process.version, minNodeVersion)) {
    throw new Error(
        `my-addon requires Node.js ${minNodeVersion} or higher. ` +
        `You are running ${process.version}.`
    );
}

// Load the addon
const binding = require('node-gyp-build')(__dirname);

// Verify N-API version
const versionInfo = binding.getVersionInfo();
const requiredNapiVersion = 8;

if (versionInfo.napiVersion < requiredNapiVersion) {
    throw new Error(
        `my-addon requires N-API version ${requiredNapiVersion} or higher. ` +
        `Your Node.js provides N-API version ${versionInfo.napiVersion}.`
    );
}

module.exports = binding;
```

## N-API Version Reference

| N-API Version | Node.js Version | Key Features |
|--------------|-----------------|--------------|
| 9 | 18.17.0+ | Symbol APIs |
| 8 | 12.22.0+ | Type tagging |
| 7 | 10.23.0+ | Detach ArrayBuffer |
| 6 | 10.20.0+ | BigInt support |
| 5 | 10.17.0+ | Date object |
| 4 | 10.16.0+ | Thread-safe functions |

## CI Version Matrix

```yaml
# .github/workflows/test.yml
jobs:
  test:
    strategy:
      matrix:
        node: [18, 20, 22]
        os: [ubuntu-latest, macos-latest, windows-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm ci
      - run: npm test
```
