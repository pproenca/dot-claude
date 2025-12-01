---
name: python-performance-optimization
description: Use when debugging slow Python code, optimizing bottlenecks, or improving application performance. Covers cProfile, memory profilers, and performance best practices.
allowed-tools: Bash(python:*), Bash(cProfile:*), Read
---

# Python Performance Optimization

Profiling and optimizing Python code for better performance.

## Reference Files

| Topic | When to Load | File |
|-------|--------------|------|
| Query optimization, batch operations, connection pooling | Database performance | `references/database-optimization.md` |
| __slots__, memory leaks, generators, weakref | Memory optimization | `references/memory-optimization.md` |

## Profiling Tools

### Pattern 1: cProfile - CPU Profiling

```python
import cProfile
import pstats
from pstats import SortKey

def slow_function():
    total = 0
    for i in range(1000000):
        total += i
    return total

def another_function():
    return [i**2 for i in range(100000)]

def main():
    result1 = slow_function()
    result2 = another_function()
    return result1, result2

# Profile the code
if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()

    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(10)  # Top 10 functions

    # Save to file for later analysis
    stats.dump_stats("profile_output.prof")
```

**Command-line profiling:**
```bash
# Profile a script
python -m cProfile -o output.prof script.py

# View results
python -m pstats output.prof
# In pstats:
# sort cumtime
# stats 10
```

### Pattern 2: line_profiler - Line-by-Line Profiling

```python
# Install: pip install line-profiler

# Add @profile decorator (line_profiler provides this)
@profile
def process_data(data):
    result = []
    for item in data:
        processed = item * 2
        result.append(processed)
    return result

# Run with:
# kernprof -l -v script.py
```

**Manual line profiling:**
```python
from line_profiler import LineProfiler

def process_data(data):
    result = []
    for item in data:
        processed = item * 2
        result.append(processed)
    return result

if __name__ == "__main__":
    lp = LineProfiler()
    lp.add_function(process_data)

    data = list(range(100000))

    lp_wrapper = lp(process_data)
    lp_wrapper(data)

    lp.print_stats()
```

### Pattern 3: memory_profiler - Memory Usage

```python
# Install: pip install memory-profiler

from memory_profiler import profile

@profile
def memory_intensive():
    big_list = [i for i in range(1000000)]
    big_dict = {i: i**2 for i in range(100000)}
    result = sum(big_list)
    return result

if __name__ == "__main__":
    memory_intensive()

# Run with:
# python -m memory_profiler script.py
```

### Pattern 4: py-spy - Production Profiling

```bash
# Install: pip install py-spy

# Profile a running Python process
py-spy top --pid 12345

# Generate flamegraph
py-spy record -o profile.svg --pid 12345

# Profile a script
py-spy record -o profile.svg -- python script.py

# Dump current call stack
py-spy dump --pid 12345
```

## Optimization Patterns

### Pattern 5: List Comprehensions vs Loops

```python
import timeit

def slow_squares(n):
    """O(n) with repeated list.append() overhead per iteration."""
    result = []
    for i in range(n):
        result.append(i**2)
    return result

def fast_squares(n):
    """Single allocation, no per-iteration append overhead."""
    return [i**2 for i in range(n)]

n = 100000

slow_time = timeit.timeit(lambda: slow_squares(n), number=100)
fast_time = timeit.timeit(lambda: fast_squares(n), number=100)

print(f"Loop: {slow_time:.4f}s")
print(f"Comprehension: {fast_time:.4f}s")
print(f"Speedup: {slow_time/fast_time:.2f}x")

def faster_squares(n):
    """Map avoids Python bytecode per iteration."""
    return list(map(lambda x: x**2, range(n)))
```

### Pattern 6: Generator Expressions for Memory

```python
import sys

list_data = [i for i in range(1000000)]
gen_data = (i for i in range(1000000))

print(f"List size: {sys.getsizeof(list_data)} bytes")
print(f"Generator size: {sys.getsizeof(gen_data)} bytes")
# Generators use constant memory regardless of size
```

### Pattern 7: String Concatenation

```python
# O(n²) - each += creates new string, copies all previous chars
result = ""
for item in items:
    result += str(item)

# O(n) - single allocation, no intermediate copies
result = "".join(str(item) for item in items)
```

### Pattern 8: Dictionary Lookups vs List Searches

```python
# O(n) - must scan entire list
target in items_list

# O(1) - hash table lookup
target in items_dict
target in items_set
```

### Pattern 9: Local Variable Access

```python
# LEGB lookup on each iteration adds overhead
GLOBAL_VALUE = 100

def use_global():
    total = 0
    for i in range(10000):
        total += GLOBAL_VALUE
    return total

def use_local():
    local_value = 100
    total = 0
    for i in range(10000):
        total += local_value
    return total
```

### Pattern 10: Function Call Overhead

```python
# Function call overhead: ~100ns per call adds up in tight loops
for i in range(10000):
    total += helper_function(i)

# Inlined: no call stack overhead
for i in range(10000):
    total += i * 2 + 1
```

## Advanced Optimization

### Pattern 11: NumPy for Numerical Operations

```python
import timeit
import numpy as np

def python_sum(n):
    return sum(range(n))

def numpy_sum(n):
    return np.arange(n).sum()

n = 1000000

python_time = timeit.timeit(lambda: python_sum(n), number=100)
numpy_time = timeit.timeit(lambda: numpy_sum(n), number=100)

print(f"Python: {python_time:.4f}s")
print(f"NumPy: {numpy_time:.4f}s")
print(f"Speedup: {python_time/numpy_time:.2f}x")

def python_multiply():
    a = list(range(100000))
    b = list(range(100000))
    return [x * y for x, y in zip(a, b)]

def numpy_multiply():
    """Vectorized: C loop instead of Python loop."""
    a = np.arange(100000)
    b = np.arange(100000)
    return a * b

py_time = timeit.timeit(python_multiply, number=100)
np_time = timeit.timeit(numpy_multiply, number=100)

print(f"\nPython multiply: {py_time:.4f}s")
print(f"NumPy multiply: {np_time:.4f}s")
print(f"Speedup: {py_time/np_time:.2f}x")
```

### Pattern 12: Caching with functools.lru_cache

```python
from functools import lru_cache
import timeit

def fibonacci_slow(n):
    """O(2^n) - exponential due to repeated subproblems."""
    if n < 2:
        return n
    return fibonacci_slow(n-1) + fibonacci_slow(n-2)

@lru_cache(maxsize=None)
def fibonacci_fast(n):
    """O(n) - each subproblem computed once."""
    if n < 2:
        return n
    return fibonacci_fast(n-1) + fibonacci_fast(n-2)

# Massive speedup for recursive algorithms
n = 30

slow_time = timeit.timeit(lambda: fibonacci_slow(n), number=1)
fast_time = timeit.timeit(lambda: fibonacci_fast(n), number=1000)

print(f"Without cache (1 run): {slow_time:.4f}s")
print(f"With cache (1000 runs): {fast_time:.4f}s")

# Cache info
print(f"Cache info: {fibonacci_fast.cache_info()}")
```

### Pattern 14: Multiprocessing for CPU-Bound Tasks

```python
import multiprocessing as mp
import time

def cpu_intensive_task(n):
    return sum(i**2 for i in range(n))

def sequential_processing():
    start = time.time()
    results = [cpu_intensive_task(1000000) for _ in range(4)]
    elapsed = time.time() - start
    return elapsed, results

def parallel_processing():
    start = time.time()
    with mp.Pool(processes=4) as pool:
        results = pool.map(cpu_intensive_task, [1000000] * 4)
    elapsed = time.time() - start
    return elapsed, results

if __name__ == "__main__":
    seq_time, seq_results = sequential_processing()
    par_time, par_results = parallel_processing()

    print(f"Sequential: {seq_time:.2f}s")
    print(f"Parallel: {par_time:.2f}s")
    print(f"Speedup: {seq_time/par_time:.2f}x")
```

### Pattern 15: Async I/O for I/O-Bound Tasks

```python
import asyncio
import aiohttp
import time
import requests

urls = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
]

def synchronous_requests():
    start = time.time()
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response.status_code)
    elapsed = time.time() - start
    return elapsed, results

async def async_fetch(session, url):
    async with session.get(url) as response:
        return response.status

async def asynchronous_requests():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [async_fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    return elapsed, results

# Async is much faster for I/O-bound work
sync_time, sync_results = synchronous_requests()
async_time, async_results = asyncio.run(asynchronous_requests())

print(f"Synchronous: {sync_time:.2f}s")
print(f"Asynchronous: {async_time:.2f}s")
print(f"Speedup: {sync_time/async_time:.2f}x")
```

## Benchmarking Tools

### Custom Benchmark Decorator

```python
import time
from functools import wraps

def benchmark(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f} seconds")
        return result
    return wrapper
```

### Performance Testing with pytest-benchmark

```python
# Install: pip install pytest-benchmark

def test_list_comprehension(benchmark):
    result = benchmark(lambda: [i**2 for i in range(10000)])
    assert len(result) == 10000

def test_map_function(benchmark):
    result = benchmark(lambda: list(map(lambda x: x**2, range(10000))))
    assert len(result) == 10000

# Run with: pytest test_performance.py --benchmark-compare
```

## Best Practices

1. **Profile before optimizing** - Measure to find real bottlenecks
2. **Focus on hot paths** - Optimize code that runs most frequently
3. **Use appropriate data structures** - Dict for lookups, set for membership
4. **Avoid premature optimization** - Clarity first, then optimize
5. **Use built-in functions** - They're implemented in C
6. **Cache expensive computations** - Use lru_cache
7. **Batch I/O operations** - Reduce system calls
8. **Use generators** for large datasets
9. **Consider NumPy** for numerical operations
10. **Profile production code** - Use py-spy for live systems

## Common Pitfalls

- Optimizing without profiling first
- Using inappropriate data structures
- Creating unnecessary data copies
- Ignoring algorithmic complexity

## Workflow Integration

**Use with `super:systematic-debugging`** for performance issues:
- Profile BEFORE optimizing - find real bottlenecks first
- Don't guess at slow code - measure with cProfile/py-spy
- Follow the 4-phase framework: investigate, analyze, hypothesize, implement

**Use with `super:verification-before-completion`** after optimization:
- Run benchmarks to prove improvement
- Verify no regressions in functionality
- Show before/after metrics

**Use with `python:python-testing-patterns`** for performance tests:
- pytest-benchmark for reliable timing
- Regression tests to catch future slowdowns

## Performance Checklist

- [ ] Profiled code to identify bottlenecks
- [ ] Used appropriate data structures
- [ ] Implemented caching where beneficial
- [ ] Considered multiprocessing/async for CPU/I/O-bound tasks
- [ ] Benchmarked before and after optimization
