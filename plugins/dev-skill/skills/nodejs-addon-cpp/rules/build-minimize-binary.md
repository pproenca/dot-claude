---
title: Minimize Binary Size
impact: MEDIUM
impactDescription: faster npm install and reduced memory footprint
tags: build, size, strip, optimization
---

## Minimize Binary Size

Strip symbols and disable unnecessary features to reduce binary size.

**Incorrect (bloated binary):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"]
  }]
}
```

**Correct (minimal binary):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"],
    "cflags_cc": ["-fno-rtti", "-fvisibility=hidden"],
    "ldflags": ["-s"],
    "xcode_settings": {
      "GCC_SYMBOLS_PRIVATE_EXTERN": "YES",
      "DEAD_CODE_STRIPPING": "YES"
    }
  }]
}
```

Reference: [Reducing Binary Size](https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html)
