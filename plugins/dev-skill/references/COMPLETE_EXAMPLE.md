# Complete Example: React Best Practices Reference

The following is a complete reference showing the expected output structure and quality level. Use this as your template for generating new skills.

## Reference: _sections.md

```markdown
# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Eliminating Waterfalls (async)

**Impact:** CRITICAL
**Description:** Waterfalls are the #1 performance killer. Each sequential await adds full network latency. Eliminating them yields the largest gains.

## 2. Bundle Size Optimization (bundle)

**Impact:** CRITICAL
**Description:** Reducing initial bundle size improves Time to Interactive and Largest Contentful Paint.

## 3. Server-Side Performance (server)

**Impact:** HIGH
**Description:** Optimizing server-side rendering and data fetching eliminates server-side waterfalls and reduces response times.

## 4. Client-Side Data Fetching (client)

**Impact:** MEDIUM-HIGH
**Description:** Automatic deduplication and efficient data fetching patterns reduce redundant network requests.

## 5. Re-render Optimization (rerender)

**Impact:** MEDIUM
**Description:** Reducing unnecessary re-renders minimizes wasted computation and improves UI responsiveness.

## 6. Rendering Performance (rendering)

**Impact:** MEDIUM
**Description:** Optimizing the rendering process reduces the work the browser needs to do.

## 7. JavaScript Performance (js)

**Impact:** LOW-MEDIUM
**Description:** Micro-optimizations for hot paths can add up to meaningful improvements.

## 8. Advanced Patterns (advanced)

**Impact:** LOW
**Description:** Advanced patterns for specific cases that require careful implementation.
```

## Reference: Sample Rules by Category

### Category 1: async- (CRITICAL) - 5 rules

**Rule: async-parallel.md**
```markdown
---
title: Promise.all() for Independent Operations
impact: CRITICAL
impactDescription: 2-10× improvement
tags: async, parallelization, promises, waterfalls
---

## Promise.all() for Independent Operations

When async operations have no interdependencies, execute them concurrently using `Promise.all()`.

**Incorrect (sequential execution, 3 round trips):**

```typescript
const user = await fetchUser()
const posts = await fetchPosts()
const comments = await fetchComments()
```

**Correct (parallel execution, 1 round trip):**

```typescript
const [user, posts, comments] = await Promise.all([
  fetchUser(),
  fetchPosts(),
  fetchComments()
])
```
```

**Rule: async-defer-await.md**
```markdown
---
title: Defer await Until Value Needed
impact: CRITICAL
impactDescription: parallelizes otherwise sequential code
tags: async, defer, promises, waterfalls
---

## Defer await Until Value Needed

Start async operations immediately but defer `await` until the value is actually needed. This allows other code to run while waiting.

**Incorrect (blocks both branches):**

```typescript
async function getData() {
  const user = await fetchUser()
  const shouldLoadPosts = checkPermissions(user)

  if (shouldLoadPosts) {
    const posts = await fetchPosts(user.id)
    return { user, posts }
  }
  return { user }
}
```

**Correct (only blocks when needed):**

```typescript
async function getData() {
  const userPromise = fetchUser()
  const user = await userPromise
  const shouldLoadPosts = checkPermissions(user)

  if (shouldLoadPosts) {
    const posts = await fetchPosts(user.id)
    return { user, posts }
  }
  return { user }
}
```
```

**Rule: async-suspense-boundaries.md**
```markdown
---
title: Strategic Suspense Boundaries
impact: CRITICAL
impactDescription: faster initial paint
tags: async, suspense, streaming, react
---

## Strategic Suspense Boundaries

Wrap slow components in Suspense boundaries to allow faster components to render immediately. Place boundaries strategically to maximize perceived performance.

**Incorrect (all-or-nothing loading):**

```tsx
export default async function Page() {
  const user = await fetchUser()
  const posts = await fetchPosts()
  const analytics = await fetchAnalytics()

  return (
    <div>
      <UserProfile user={user} />
      <PostList posts={posts} />
      <Analytics data={analytics} />
    </div>
  )
}
```

**Correct (progressive streaming):**

```tsx
export default function Page() {
  return (
    <div>
      <Suspense fallback={<UserSkeleton />}>
        <UserProfile />
      </Suspense>
      <Suspense fallback={<PostsSkeleton />}>
        <PostList />
      </Suspense>
      <Suspense fallback={<AnalyticsSkeleton />}>
        <Analytics />
      </Suspense>
    </div>
  )
}
```

The page streams progressively - each component appears as soon as its data is ready.
```

### Category 2: bundle- (CRITICAL) - 5 rules

**Rule: bundle-barrel-imports.md**
```markdown
---
title: Avoid Barrel File Imports
impact: CRITICAL
impactDescription: 200-800ms import cost, slow builds
tags: bundle, imports, tree-shaking, barrel-files, performance
---

## Avoid Barrel File Imports

Import directly from source files instead of barrel files to avoid loading thousands of unused modules.

**Incorrect (imports entire library):**

```tsx
import { Check, X, Menu } from 'lucide-react'
// Loads 1,583 modules, takes ~2.8s extra in dev
```

**Correct (imports only what you need):**

```tsx
import Check from 'lucide-react/dist/esm/icons/check'
import X from 'lucide-react/dist/esm/icons/x'
import Menu from 'lucide-react/dist/esm/icons/menu'
// Loads only 3 modules (~2KB vs ~1MB)
```

**Alternative (Next.js 13.5+):**

```js
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: ['lucide-react', '@mui/material']
  }
}
```

Reference: [How we optimized package imports in Next.js](https://vercel.com/blog/how-we-optimized-package-imports-in-next-js)
```

**Rule: bundle-dynamic-imports.md**
```markdown
---
title: Use Dynamic Imports for Large Components
impact: CRITICAL
impactDescription: reduces initial bundle by 30-70%
tags: bundle, dynamic-import, code-splitting, lazy-loading
---

## Use Dynamic Imports for Large Components

Use `next/dynamic` or React.lazy() to load heavy components only when needed.

**Incorrect (always loaded):**

```tsx
import HeavyChart from '@/components/HeavyChart'
import CodeEditor from '@/components/CodeEditor'

export default function Dashboard() {
  const [showChart, setShowChart] = useState(false)
  return (
    <div>
      {showChart && <HeavyChart />}
      <CodeEditor />
    </div>
  )
}
// Both components in initial bundle even if never used
```

**Correct (loaded on demand):**

```tsx
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <ChartSkeleton />
})
const CodeEditor = dynamic(() => import('@/components/CodeEditor'), {
  ssr: false
})

export default function Dashboard() {
  const [showChart, setShowChart] = useState(false)
  return (
    <div>
      {showChart && <HeavyChart />}
      <CodeEditor />
    </div>
  )
}
// Components loaded only when rendered
```
```

### Category 3: server- (HIGH) - 5 rules

**Rule: server-parallel-fetching.md**
```markdown
---
title: Parallel Data Fetching in Server Components
impact: HIGH
impactDescription: eliminates server-side waterfalls
tags: server, rsc, parallel, data-fetching
---

## Parallel Data Fetching in Server Components

Initiate all data fetches at once, then await them together.

**Incorrect (sequential fetches):**

```tsx
export default async function Page() {
  const user = await fetchUser()
  const posts = await fetchPosts(user.id)
  const comments = await fetchComments(posts[0].id)
  // Total time: user + posts + comments
}
```

**Correct (parallel fetches):**

```tsx
export default async function Page() {
  const userPromise = fetchUser()
  const postsPromise = fetchPosts()

  const [user, posts] = await Promise.all([userPromise, postsPromise])
  // Total time: max(user, posts)
}
```
```

**Rule: server-cache-react.md**
```markdown
---
title: Use React cache() for Request Deduplication
impact: HIGH
impactDescription: eliminates duplicate fetches per request
tags: server, cache, deduplication, react
---

## Use React cache() for Request Deduplication

Wrap data fetching functions with `cache()` to deduplicate identical calls within a single request.

**Incorrect (duplicate fetches):**

```tsx
// lib/data.ts
export async function getUser(id: string) {
  return fetch(`/api/users/${id}`).then(r => r.json())
}

// components/Header.tsx
const user = await getUser(userId)

// components/Sidebar.tsx
const user = await getUser(userId) // Fetches again!
```

**Correct (deduplicated):**

```tsx
// lib/data.ts
import { cache } from 'react'

export const getUser = cache(async (id: string) => {
  return fetch(`/api/users/${id}`).then(r => r.json())
})

// Both components get the same cached result
```
```

### Category 5: rerender- (MEDIUM) - 7 rules

**Rule: rerender-memo.md**
```markdown
---
title: Memoize Expensive Child Components
impact: MEDIUM
impactDescription: prevents cascading re-renders
tags: rerender, memo, optimization, react
---

## Memoize Expensive Child Components

Use `React.memo()` to prevent re-renders when props haven't changed.

**Incorrect (re-renders on every parent render):**

```tsx
function ExpensiveList({ items, onSelect }) {
  return items.map(item => (
    <ExpensiveItem key={item.id} item={item} onSelect={onSelect} />
  ))
}
```

**Correct (only re-renders when props change):**

```tsx
const ExpensiveList = memo(function ExpensiveList({ items, onSelect }) {
  return items.map(item => (
    <ExpensiveItem key={item.id} item={item} onSelect={onSelect} />
  ))
})
```

**Important:** Ensure callbacks are stable (use useCallback) or memo won't help.
```

**Rule: rerender-functional-setstate.md**
```markdown
---
title: Use Functional setState Updates
impact: MEDIUM
impactDescription: prevents stale closures and unnecessary callback recreations
tags: rerender, hooks, useState, callbacks, closures
---

## Use Functional setState Updates

When updating state based on current value, use functional form to avoid stale closures.

**Incorrect (requires state as dependency):**

```tsx
function Counter() {
  const [count, setCount] = useState(0)

  const increment = useCallback(() => {
    setCount(count + 1)
  }, [count])  // Recreated on every count change
}
```

**Correct (stable callback):**

```tsx
function Counter() {
  const [count, setCount] = useState(0)

  const increment = useCallback(() => {
    setCount(c => c + 1)
  }, [])  // Never recreated
}
```
```

### Category 7: js- (LOW-MEDIUM) - 12 rules

**Rule: js-set-map-lookups.md**
```markdown
---
title: Use Set/Map for O(1) Lookups
impact: MEDIUM
impactDescription: O(n) to O(1)
tags: js, set, map, performance, lookup
---

## Use Set/Map for O(1) Lookups

Replace array `.includes()` or `.find()` with Set/Map for frequent lookups.

**Incorrect (O(n) per lookup):**

```typescript
const allowedIds = ['a', 'b', 'c', 'd', 'e']

function isAllowed(id: string) {
  return allowedIds.includes(id)  // O(n) every time
}
```

**Correct (O(1) per lookup):**

```typescript
const allowedIds = new Set(['a', 'b', 'c', 'd', 'e'])

function isAllowed(id: string) {
  return allowedIds.has(id)  // O(1) every time
}
```
```

**Rule: js-cache-property-access.md**
```markdown
---
title: Cache Property Access in Loops
impact: LOW-MEDIUM
impactDescription: reduces property lookups by N×
tags: js, loops, optimization, property-access
---

## Cache Property Access in Loops

Cache frequently accessed properties outside loops.

**Incorrect (repeated property access):**

```typescript
for (let i = 0; i < items.length; i++) {
  process(items[i], config.settings.threshold)
}
```

**Correct (cached access):**

```typescript
const { length } = items
const { threshold } = config.settings

for (let i = 0; i < length; i++) {
  process(items[i], threshold)
}
```
```

## Reference: Complete metadata.json

```json
{
  "version": "0.1.0",
  "organization": "Vercel Engineering",
  "date": "January 2026",
  "abstract": "Comprehensive performance optimization guide for React and Next.js applications, designed for AI agents and LLMs. Contains 45+ rules across 8 categories, prioritized by impact from critical (eliminating waterfalls, reducing bundle size) to incremental (advanced patterns). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.",
  "references": [
    "https://react.dev",
    "https://nextjs.org",
    "https://swr.vercel.app",
    "https://vercel.com/blog/how-we-optimized-package-imports-in-next-js"
  ]
}
```

## Reference: Rule Count per Category

| Category | Prefix | Impact | Target Rules |
|----------|--------|--------|--------------|
| Eliminating Waterfalls | async- | CRITICAL | 5 |
| Bundle Size Optimization | bundle- | CRITICAL | 5 |
| Server-Side Performance | server- | HIGH | 5 |
| Client-Side Data Fetching | client- | MEDIUM-HIGH | 2 |
| Re-render Optimization | rerender- | MEDIUM | 7 |
| Rendering Performance | rendering- | MEDIUM | 7 |
| JavaScript Performance | js- | LOW-MEDIUM | 12 |
| Advanced Patterns | advanced- | LOW | 2 |
| **Total** | | | **45** |
