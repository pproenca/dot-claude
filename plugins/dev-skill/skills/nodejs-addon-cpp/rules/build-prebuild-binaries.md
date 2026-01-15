---
title: Distribute Prebuilt Binaries
impact: MEDIUM
impactDescription: eliminates build time for users
tags: build, prebuild, distribution, npm
---

## Distribute Prebuilt Binaries

Use prebuild/prebuildify to distribute precompiled binaries instead of requiring users to compile.

**Incorrect (compile on install):**

```json
{
  "scripts": {
    "install": "node-gyp rebuild"
  }
}
```

**Correct (prebuilt binaries):**

```json
{
  "scripts": {
    "install": "prebuild-install || node-gyp rebuild",
    "prebuild": "prebuildify --napi --strip"
  },
  "devDependencies": {
    "prebuildify": "^5.0.0"
  },
  "dependencies": {
    "prebuild-install": "^7.0.0"
  }
}
```

Reference: [prebuildify](https://github.com/prebuild/prebuildify)
