---
title: Use node-gyp for Standard Setup
impact: MEDIUM
impactDescription: Cross-platform builds with consistent configuration
tags: build, node-gyp, binding-gyp, compilation
---

# Use node-gyp for Standard Setup

node-gyp is the standard build tool for Node.js native addons. Use binding.gyp for portable, maintainable build configuration that works across all platforms and Node.js versions.

## Why This Matters

- Official Node.js build system with wide community support
- Handles platform-specific compiler flags automatically
- Integrates with npm lifecycle scripts for seamless installs
- Manages Node.js header downloads and ABI compatibility

## Incorrect

Manual Makefile without proper cross-platform handling:

```makefile
# BAD: Platform-specific, no Node.js integration
addon.node: addon.cpp
    g++ -shared -fPIC -o addon.node addon.cpp \
        -I/usr/local/include/node \
        -lnode

# Problems:
# - Hardcoded paths don't work on Windows
# - No automatic Node.js header management
# - Missing required compiler flags
# - No ABI versioning
```

## Correct

Proper binding.gyp with node-gyp:

```python
# binding.gyp
{
  "targets": [
    {
      "target_name": "addon",
      "sources": ["src/addon.cpp"],
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")"
      ],
      "dependencies": [
        "<!(node -p \"require('node-addon-api').gyp\")"
      ],
      "cflags!": ["-fno-exceptions"],
      "cflags_cc!": ["-fno-exceptions"],
      "xcode_settings": {
        "GCC_ENABLE_CPP_EXCEPTIONS": "YES",
        "CLANG_CXX_LIBRARY": "libc++",
        "MACOSX_DEPLOYMENT_TARGET": "10.15"
      },
      "msvs_settings": {
        "VCCLCompilerTool": {
          "ExceptionHandling": 1
        }
      },
      "defines": ["NAPI_VERSION=8"]
    }
  ]
}
```

## Package.json Integration

```json
{
  "name": "my-addon",
  "version": "1.0.0",
  "main": "lib/index.js",
  "scripts": {
    "install": "node-gyp rebuild",
    "build": "node-gyp build",
    "rebuild": "node-gyp rebuild",
    "clean": "node-gyp clean"
  },
  "dependencies": {
    "node-addon-api": "^7.0.0"
  },
  "devDependencies": {
    "node-gyp": "^10.0.0"
  },
  "gypfile": true
}
```

## Multi-Target Configuration

```python
# binding.gyp with multiple targets
{
  "targets": [
    {
      "target_name": "core",
      "type": "static_library",
      "sources": [
        "src/core/engine.cpp",
        "src/core/utils.cpp"
      ],
      "include_dirs": ["src/core"],
      "direct_dependent_settings": {
        "include_dirs": ["src/core"]
      }
    },
    {
      "target_name": "addon",
      "sources": ["src/addon.cpp"],
      "dependencies": ["core"],
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")"
      ],
      "defines": ["NAPI_VERSION=8"]
    }
  ]
}
```

## Conditional Configuration

```python
# binding.gyp with platform conditions
{
  "targets": [
    {
      "target_name": "addon",
      "sources": ["src/addon.cpp"],
      "conditions": [
        ["OS=='win'", {
          "defines": ["NOMINMAX", "WIN32_LEAN_AND_MEAN"],
          "libraries": ["-lws2_32"]
        }],
        ["OS=='mac'", {
          "xcode_settings": {
            "OTHER_CPLUSPLUSFLAGS": ["-stdlib=libc++"]
          },
          "libraries": ["-framework CoreFoundation"]
        }],
        ["OS=='linux'", {
          "cflags": ["-fvisibility=hidden"],
          "libraries": ["-lpthread"]
        }]
      ],
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")"
      ],
      "defines": ["NAPI_VERSION=8"]
    }
  ]
}
```

## Debug Build Configuration

```python
# binding.gyp with debug support
{
  "targets": [
    {
      "target_name": "addon",
      "sources": ["src/addon.cpp"],
      "configurations": {
        "Debug": {
          "defines": ["DEBUG", "_DEBUG"],
          "cflags": ["-g", "-O0"],
          "xcode_settings": {
            "GCC_OPTIMIZATION_LEVEL": "0",
            "GCC_GENERATE_DEBUGGING_SYMBOLS": "YES"
          },
          "msvs_settings": {
            "VCCLCompilerTool": {
              "Optimization": 0,
              "DebugInformationFormat": 3
            }
          }
        },
        "Release": {
          "defines": ["NDEBUG"],
          "cflags": ["-O3"],
          "xcode_settings": {
            "GCC_OPTIMIZATION_LEVEL": "3"
          },
          "msvs_settings": {
            "VCCLCompilerTool": {
              "Optimization": 2
            }
          }
        }
      },
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")"
      ],
      "defines": ["NAPI_VERSION=8"]
    }
  ]
}
```

## Build Commands

```bash
# Standard build
node-gyp rebuild

# Debug build
node-gyp rebuild --debug

# Verbose output
node-gyp rebuild --verbose

# Specific Node.js version
node-gyp rebuild --target=18.0.0

# Clean and rebuild
node-gyp clean && node-gyp configure && node-gyp build
```

Reference: [node-gyp Documentation](https://github.com/nodejs/node-gyp)
