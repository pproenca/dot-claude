---
title: Provide Prebuilt Binaries
impact: MEDIUM
impactDescription: Eliminates build failures for 95%+ of users without build tools
tags: build, prebuild, distribution, binary, npm-install
---

# Provide Prebuilt Binaries

Use prebuild or prebuildify to distribute precompiled binaries. Most users don't have C++ build tools installed; prebuilt binaries enable seamless `npm install`.

## Why This Matters

- Users avoid installing Python, C++ compilers, node-gyp
- Faster installation (seconds vs minutes)
- Eliminates platform-specific build failures
- CI/CD pipelines run without build toolchains
- Better user experience for non-C++ developers

## Incorrect

Requiring users to compile from source:

```json
// package.json - Forces compilation on every install
{
    "name": "my-addon",
    "scripts": {
        "install": "node-gyp rebuild"
    }
}
```

```
// User experience:
$ npm install my-addon
npm ERR! gyp ERR! find Python
npm ERR! gyp ERR! build error
npm ERR! node-gyp failed
```

## Correct

Use prebuildify for prebuilt binaries:

```json
// package.json
{
    "name": "my-addon",
    "version": "2.0.0",
    "main": "index.js",
    "scripts": {
        "install": "node-gyp-build",
        "prebuild": "prebuildify --napi --strip",
        "prebuild:all": "prebuildify --napi --strip --target 18.0.0 --target 20.0.0 --target 22.0.0",
        "prebuild:linux": "prebuildify --napi --strip --arch x64 --arch arm64",
        "prebuild:darwin": "prebuildify --napi --strip --arch x64 --arch arm64",
        "prebuild:win32": "prebuildify --napi --strip --arch x64",
        "test": "node test.js"
    },
    "dependencies": {
        "node-gyp-build": "^4.6.0"
    },
    "devDependencies": {
        "node-addon-api": "^7.0.0",
        "node-gyp": "^10.0.0",
        "prebuildify": "^6.0.0"
    },
    "files": [
        "index.js",
        "prebuilds",
        "src",
        "binding.gyp"
    ],
    "gypfile": true
}
```

```javascript
// index.js - Uses node-gyp-build for automatic binary loading
const binding = require('node-gyp-build')(__dirname);

module.exports = binding;
```

```python
# binding.gyp
{
    "targets": [{
        "target_name": "addon",
        "sources": ["src/addon.cpp"],
        "include_dirs": [
            "<!@(node -p \"require('node-addon-api').include\")"
        ],
        "defines": ["NAPI_VERSION=8"]
    }]
}
```

## GitHub Actions for Cross-Platform Prebuilds

```yaml
# .github/workflows/prebuild.yml
name: Prebuild

on:
  push:
    tags:
      - 'v*'

jobs:
  prebuild:
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            arch: x64
          - os: ubuntu-latest
            arch: arm64
          - os: macos-latest
            arch: x64
          - os: macos-latest
            arch: arm64
          - os: windows-latest
            arch: x64

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Build prebuilds
        run: npm run prebuild -- --arch ${{ matrix.arch }}

      - name: Upload prebuilds
        uses: actions/upload-artifact@v4
        with:
          name: prebuild-${{ matrix.os }}-${{ matrix.arch }}
          path: prebuilds/

  publish:
    needs: prebuild
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          registry-url: 'https://registry.npmjs.org'

      - name: Download all prebuilds
        uses: actions/download-artifact@v4
        with:
          path: prebuilds/
          pattern: prebuild-*
          merge-multiple: true

      - name: Publish to npm
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Directory Structure with Prebuilds

```
my-addon/
├── package.json
├── index.js
├── binding.gyp
├── src/
│   └── addon.cpp
├── prebuilds/           # Included in npm package
│   ├── darwin-arm64/
│   │   └── node.napi.node
│   ├── darwin-x64/
│   │   └── node.napi.node
│   ├── linux-arm64/
│   │   └── node.napi.node
│   ├── linux-x64/
│   │   └── node.napi.node
│   └── win32-x64/
│       └── node.napi.node
└── build/               # NOT included (gitignored)
    └── Release/
        └── addon.node
```

## Fallback to Compilation

```javascript
// index.js - Graceful fallback
let binding;

try {
    // Try prebuilt binary first
    binding = require('node-gyp-build')(__dirname);
} catch (e) {
    console.warn('Prebuilt binary not found, falling back to compilation');
    console.warn('This may take a few minutes...');

    // Trigger rebuild
    const { execSync } = require('child_process');
    execSync('npm run rebuild', { stdio: 'inherit', cwd: __dirname });

    // Load compiled binary
    binding = require('node-gyp-build')(__dirname);
}

module.exports = binding;
```

## Alternative: prebuild with GitHub Releases

```json
// package.json using prebuild (downloads from GitHub Releases)
{
    "scripts": {
        "install": "prebuild-install || node-gyp rebuild",
        "prebuild": "prebuild --all --strip"
    },
    "dependencies": {
        "prebuild-install": "^7.0.0"
    },
    "devDependencies": {
        "prebuild": "^13.0.0"
    }
}
```

## Platform Matrix

| Platform | Architectures | Node Versions |
|----------|--------------|---------------|
| linux | x64, arm64 | 18, 20, 22 |
| darwin | x64, arm64 | 18, 20, 22 |
| win32 | x64 | 18, 20, 22 |

N-API versioning means one binary works across Node.js versions with the same N-API version.
