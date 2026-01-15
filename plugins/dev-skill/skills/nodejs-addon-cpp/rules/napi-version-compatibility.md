---
title: Target Appropriate N-API Version
impact: MEDIUM
impactDescription: ensures compatibility across Node.js versions
tags: napi, version, compatibility, abi
---

## Target Appropriate N-API Version

Set NAPI_VERSION to the lowest version that provides features you need. This maximizes compatibility across Node.js versions.

**Incorrect (implicit latest):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"]
  }]
}
```

**Correct (explicit version):**

```json
{
  "targets": [{
    "target_name": "addon",
    "sources": ["addon.cpp"],
    "defines": ["NAPI_VERSION=8"]
  }]
}
```

**N-API version features:**
- v8: Node 12.22+, ThreadSafeFunction improvements
- v6: Node 10.20+, BigInt support
- v4: Node 10.16+, AsyncWorker improvements
- v3: Node 8.11+, basic async support

Reference: [N-API Version Matrix](https://nodejs.org/api/n-api.html#node-api-version-matrix)
