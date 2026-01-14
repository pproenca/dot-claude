---
title: Use Base Configurations
impact: LOW-MEDIUM
impactDescription: standardized environment-specific defaults
tags: config, extends, tsconfig, bases
---

## Use Base Configurations

Extend from `@tsconfig/bases` packages for environment-specific defaults. Reduces boilerplate and ensures best practices for your target runtime.

**Incorrect (manual configuration):**

```typescript
// tsconfig.json - manually configuring everything
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
    // Easy to miss options or use wrong values
  }
}
```

**Correct (extend from bases):**

```typescript
// First install the base config
// npm install --save-dev @tsconfig/node20

// tsconfig.json
{
  "extends": "@tsconfig/node20/tsconfig.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
    // Only override what you need
  },
  "include": ["src/**/*"]
}

// For different environments:

// Node.js 18 LTS
{ "extends": "@tsconfig/node18/tsconfig.json" }

// Node.js 20
{ "extends": "@tsconfig/node20/tsconfig.json" }

// Strictest settings
{ "extends": "@tsconfig/strictest/tsconfig.json" }

// React with Vite
{ "extends": "@tsconfig/vite-react/tsconfig.json" }

// Next.js (use their config)
{ "extends": "next/core-js/tsconfig.json" }
```

**Available bases:**
- `@tsconfig/node18`, `@tsconfig/node20` - Node.js versions
- `@tsconfig/strictest` - Maximum strictness
- `@tsconfig/recommended` - General recommendations
- `@tsconfig/vite-react` - Vite + React projects
- Framework-specific: Next.js, Remix, etc. provide their own

Reference: [tsconfig/bases](https://github.com/tsconfig/bases)
