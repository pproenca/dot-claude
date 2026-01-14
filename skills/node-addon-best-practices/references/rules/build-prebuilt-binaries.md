---
title: Provide Prebuilt Binaries
impact: MEDIUM
impactDescription: Eliminates build-time compilation for end users
tags: build, prebuild, prebuildify, binaries, distribution
---

# Provide Prebuilt Binaries

Ship precompiled binaries for common platforms to eliminate compilation requirements for users. Use prebuild or prebuildify to automate multi-platform binary generation and distribution.

## Why This Matters

- Users without build tools can install your addon
- Faster npm install (no compilation step)
- Consistent binaries across user environments
- Required for many CI/CD environments

## Incorrect

Requiring all users to compile from source:

```json
{
  "name": "my-addon",
  "scripts": {
    "install": "node-gyp rebuild"
  }
}
```

Problems with source-only distribution:
- Requires Python, C++ compiler, make/MSBuild
- Windows users need Visual Studio Build Tools
- macOS users need Xcode Command Line Tools
- Build failures due to environment differences
- Slow installation (minutes vs seconds)

## Correct

Use prebuildify for inline prebuilt binaries:

```json
{
  "name": "my-addon",
  "version": "1.0.0",
  "main": "lib/index.js",
  "scripts": {
    "install": "prebuild-install || node-gyp rebuild",
    "build": "node-gyp build",
    "prebuild": "prebuildify --napi --strip",
    "prebuild:all": "npm run prebuild:linux && npm run prebuild:macos && npm run prebuild:windows",
    "prebuild:linux": "prebuildify --napi --strip --platform=linux --arch=x64",
    "prebuild:macos": "prebuildify --napi --strip --platform=darwin --arch=x64,arm64",
    "prebuild:windows": "prebuildify --napi --strip --platform=win32 --arch=x64"
  },
  "dependencies": {
    "node-addon-api": "^7.0.0",
    "prebuild-install": "^7.0.0"
  },
  "devDependencies": {
    "prebuildify": "^6.0.0"
  }
}
```

## Loading Prebuilt Binaries

```javascript
// lib/index.js
const path = require('path');

let addon;

try {
  // Try to load prebuildify binary first
  addon = require('../prebuilds/' +
    process.platform + '-' + process.arch +
    '/node.napi.node');
} catch {
  try {
    // Fall back to compiled binary
    addon = require('../build/Release/addon.node');
  } catch {
    addon = require('../build/Debug/addon.node');
  }
}

module.exports = addon;
```

## Using node-pre-gyp Alternative

```json
{
  "name": "my-addon",
  "version": "1.0.0",
  "main": "lib/index.js",
  "binary": {
    "module_name": "addon",
    "module_path": "./lib/binding/{platform}-{arch}",
    "remote_path": "./{module_name}/v{version}",
    "host": "https://github.com/myorg/myrepo/releases/download"
  },
  "scripts": {
    "install": "node-pre-gyp install --fallback-to-build",
    "build": "node-pre-gyp build",
    "package": "node-pre-gyp package",
    "publish": "node-pre-gyp publish"
  },
  "dependencies": {
    "@mapbox/node-pre-gyp": "^1.0.0",
    "node-addon-api": "^7.0.0"
  }
}
```

## GitHub Actions for Multi-Platform Builds

```yaml
# .github/workflows/prebuild.yml
name: Prebuild Binaries

on:
  release:
    types: [created]
  workflow_dispatch:

jobs:
  prebuild:
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            arch: x64
          - os: macos-latest
            arch: x64
          - os: macos-latest
            arch: arm64
          - os: windows-latest
            arch: x64

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Prebuild
        run: npx prebuildify --napi --strip --arch=${{ matrix.arch }}

      - name: Upload prebuilds
        uses: actions/upload-artifact@v4
        with:
          name: prebuild-${{ matrix.os }}-${{ matrix.arch }}
          path: prebuilds/

  package:
    needs: prebuild
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download all prebuilds
        uses: actions/download-artifact@v4
        with:
          path: prebuilds/
          merge-multiple: true

      - name: Publish to npm
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Cross-Compilation with Docker

```dockerfile
# Dockerfile.linux-arm64
FROM node:20-bullseye

RUN apt-get update && apt-get install -y \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

ENV CC=aarch64-linux-gnu-gcc
ENV CXX=aarch64-linux-gnu-g++

RUN npm ci
RUN npx prebuildify --napi --strip --arch=arm64
```

```bash
# Build script
docker build -f Dockerfile.linux-arm64 -t addon-arm64 .
docker run --rm -v $(pwd)/prebuilds:/app/prebuilds addon-arm64
```

## Verifying Prebuilt Binaries

```javascript
// scripts/verify-prebuilds.js
const fs = require('fs');
const path = require('path');

const expected = [
  'linux-x64/node.napi.node',
  'darwin-x64/node.napi.node',
  'darwin-arm64/node.napi.node',
  'win32-x64/node.napi.node'
];

const prebuildsDir = path.join(__dirname, '..', 'prebuilds');
const missing = [];

for (const file of expected) {
  const fullPath = path.join(prebuildsDir, file);
  if (!fs.existsSync(fullPath)) {
    missing.push(file);
  } else {
    const stats = fs.statSync(fullPath);
    console.log(`✓ ${file} (${(stats.size / 1024).toFixed(1)} KB)`);
  }
}

if (missing.length > 0) {
  console.error('\nMissing prebuilds:');
  missing.forEach(f => console.error(`  ✗ ${f}`));
  process.exit(1);
}

console.log('\nAll prebuilds present!');
```

## Best Practices

| Practice | Description |
|----------|-------------|
| Use N-API | Ensures binary compatibility across Node versions |
| Strip symbols | Reduces binary size significantly |
| Test on CI | Verify prebuilds work before publishing |
| Include source | Allow fallback compilation |
| Document requirements | List build prerequisites for fallback |

Reference: [prebuildify Documentation](https://github.com/prebuild/prebuildify)
