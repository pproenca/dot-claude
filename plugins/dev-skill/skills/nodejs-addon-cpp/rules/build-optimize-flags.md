---
title: Use Optimal Compiler Flags
impact: MEDIUM
impactDescription: 10-50% performance improvement
tags: build, compiler, optimization, flags
---

## Use Optimal Compiler Flags

Configure gyp to use appropriate optimization flags for release builds.

**Incorrect (debug flags in production):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"]
  }]
}
```

**Correct (optimized release build):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"],
    "cflags_cc": ["-O3", "-fno-exceptions"],
    "xcode_settings": {
      "GCC_OPTIMIZATION_LEVEL": "3",
      "CLANG_CXX_LIBRARY": "libc++"
    },
    "msvs_settings": {
      "VCCLCompilerTool": {
        "Optimization": 2
      }
    }
  }]
}
```

Reference: [node-gyp](https://github.com/nodejs/node-gyp)
