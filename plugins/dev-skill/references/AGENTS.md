# React and Next.js Performance Best Practices

**Version 0.1.0**
Vercel Engineering
January 2026

> **Note:**
> This document is mainly for agents and LLMs to follow when maintaining,
> generating, or refactoring codebases. Humans may also find it useful,
> but guidance here is optimized for automation and consistency by AI-assisted workflows.

---

## Abstract

Comprehensive performance optimization guide for React and Next.js applications, designed for AI agents and LLMs. Contains 40+ rules across 8 categories, prioritized by impact from critical (eliminating waterfalls, reducing bundle size) to incremental (advanced patterns). Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.

---

## Table of Contents

1. [Eliminating Waterfalls](examples/_sections.md#1-eliminating-waterfalls) — **CRITICAL**
   - 1.1 [Dependency-Based Parallelization](examples/async-dependencies.md) — CRITICAL (2-10× improvement)
   - 1.2 [Promise.all() for Independent Operations](examples/async-parallel.md) — CRITICAL (2-10× improvement)
2. [Bundle Size Optimization](examples/_sections.md#2-bundle-size-optimization) — **CRITICAL**
   - 2.1 [Avoid Barrel File Imports](examples/bundle-barrel-imports.md) — CRITICAL (200-800ms import cost, slow builds)
   - 2.2 [Dynamic Imports for Heavy Components](examples/bundle-dynamic-imports.md) — CRITICAL (directly affects TTI and LCP)
3. [Server-Side Performance](examples/_sections.md#3-server-side-performance) — **HIGH**
   - 3.1 [Parallel Data Fetching with Component Composition](examples/server-parallel-fetching.md) — CRITICAL (eliminates server-side waterfalls)
   - 3.2 [Per-Request Deduplication with React.cache()](examples/server-cache-react.md) — MEDIUM (deduplicates within request)
4. [Client-Side Data Fetching](examples/_sections.md#4-client-side-data-fetching) — **MEDIUM-HIGH**
   - 4.1 [Use SWR for Automatic Deduplication](examples/client-swr-dedup.md) — MEDIUM-HIGH (automatic deduplication)
5. [Re-render Optimization](examples/_sections.md#5-re-render-optimization) — **MEDIUM**
   - 5.1 [Extract to Memoized Components](examples/rerender-memo.md) — MEDIUM (enables early returns)
6. [Rendering Performance](examples/_sections.md#6-rendering-performance) — **MEDIUM**
   - 6.1 [CSS content-visibility for Long Lists](examples/rendering-content-visibility.md) — HIGH (faster initial render)
7. [JavaScript Performance](examples/_sections.md#7-javascript-performance) — **LOW-MEDIUM**
   - 7.1 [Use Set/Map for O(1) Lookups](examples/js-set-map-lookups.md) — LOW-MEDIUM (O(n) to O(1))
   - 7.2 [Use toSorted() Instead of sort() for Immutability](examples/js-tosorted-immutable.md) — MEDIUM-HIGH (prevents mutation bugs in React state)
8. [Advanced Patterns](examples/_sections.md#8-advanced-patterns) — **LOW**
   - 8.1 [useLatest for Stable Callback Refs](examples/advanced-use-latest.md) — LOW (prevents effect re-runs)

---

## References

1. [https://react.dev](https://react.dev)
2. [https://nextjs.org](https://nextjs.org)
3. [https://swr.vercel.app](https://swr.vercel.app)
4. [https://github.com/shuding/better-all](https://github.com/shuding/better-all)
5. [https://github.com/isaacs/node-lru-cache](https://github.com/isaacs/node-lru-cache)
6. [https://vercel.com/blog/how-we-optimized-package-imports-in-next-js](https://vercel.com/blog/how-we-optimized-package-imports-in-next-js)
7. [https://vercel.com/blog/how-we-made-the-vercel-dashboard-twice-as-fast](https://vercel.com/blog/how-we-made-the-vercel-dashboard-twice-as-fast)

---

## Source Files

This document was compiled from individual reference files. For detailed editing or extension:

| File | Description |
|------|-------------|
| [examples/_sections.md](examples/_sections.md) | Category definitions and impact ordering |
| [SKILL.md](SKILL.md) | Quick reference entry point |
| [metadata.json](metadata.json) | Version and reference URLs |
