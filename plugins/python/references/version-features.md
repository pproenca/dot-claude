# Python Version Features

Quick reference for version-specific features when adapting code.

## Python 3.13 (October 2024)

### Free-Threaded Mode (Experimental)

```bash
# Install free-threaded Python
uv python install 3.13t
```

```python
# True parallelism for CPU-bound code
import threading

def cpu_bound(n):
    return sum(i**2 for i in range(n))

threads = [threading.Thread(target=cpu_bound, args=(1_000_000,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### Improved Error Messages

```python
# Better suggestions for common mistakes
>>> import asynico
ModuleNotFoundError: No module named 'asynico'. Did you mean: 'asyncio'?
```

### New REPL

- Multiline editing
- Syntax highlighting
- History across sessions

## Python 3.12 (October 2023)

### Type Parameter Syntax

```python
# Old way
from typing import TypeVar, Generic
T = TypeVar('T')

class Stack(Generic[T]):
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...

# New way (3.12+)
class Stack[T]:
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...

# Generic functions
def first[T](items: list[T]) -> T:
    return items[0]
```

### F-String Improvements

```python
# Nested quotes now work
f"Hello {user['name']}"  # Works in 3.12+

# Multiline expressions
f"""
{
    some_long_expression
    + another_expression
}
"""

# Comments in f-strings
f"{
    value  # This is the value
}"
```

### Per-Interpreter GIL (Subinterpreters)

```python
import _interpreters

interp = _interpreters.create()
_interpreters.run_string(interp, "print('Hello from subinterpreter')")
```

## Python 3.11 (October 2022)

### TaskGroup (Structured Concurrency)

```python
async def fetch_all(urls: list[str]) -> list[dict]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(url)) for url in urls]
    return [t.result() for t in tasks]
```

### Exception Groups

```python
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(might_fail_1())
        tg.create_task(might_fail_2())
except* ValueError as eg:
    for exc in eg.exceptions:
        print(f"ValueError: {exc}")
except* TypeError as eg:
    for exc in eg.exceptions:
        print(f"TypeError: {exc}")
```

### Self Type

```python
from typing import Self

class Builder:
    def with_name(self, name: str) -> Self:
        self.name = name
        return self
```

### Fine-Grained Error Locations

```python
# Python 3.11+ shows exact error location
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    x['a']['b']['c']['d'] = 1
    ~~~~~~~~^^^^^
TypeError: 'NoneType' object is not subscriptable
```

### Performance

- 10-60% faster than 3.10
- Faster startup
- Cheaper exceptions

## Python 3.10 (October 2021)

### Structural Pattern Matching

```python
match command:
    case ["quit"]:
        sys.exit(0)
    case ["load", filename]:
        load_file(filename)
    case ["save", filename] if filename.endswith('.json'):
        save_json(filename)
    case _:
        print("Unknown command")

# With classes
match point:
    case Point(x=0, y=0):
        print("Origin")
    case Point(x=0, y=y):
        print(f"On Y axis at {y}")
    case Point(x=x, y=0):
        print(f"On X axis at {x}")
```

### Union Type Operator

```python
# Old way
from typing import Union, Optional
def process(x: Union[int, str]) -> Optional[str]: ...

# New way (3.10+)
def process(x: int | str) -> str | None: ...
```

### Parameter Specification

```python
from typing import ParamSpec, Callable

P = ParamSpec('P')

def decorator(func: Callable[P, int]) -> Callable[P, str]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
        return str(func(*args, **kwargs))
    return wrapper
```

### Parenthesized Context Managers

```python
with (
    open('input.txt') as input_file,
    open('output.txt', 'w') as output_file,
):
    output_file.write(input_file.read())
```

## Python 3.9 (October 2020)

### Generic Built-in Types

```python
# Old way
from typing import List, Dict, Tuple
def process(items: List[str]) -> Dict[str, int]: ...

# New way (3.9+)
def process(items: list[str]) -> dict[str, int]: ...
```

### Dictionary Union

```python
# Merge dictionaries
merged = dict1 | dict2

# Update in place
dict1 |= dict2
```

### String Methods

```python
"hello world".removeprefix("hello ")  # "world"
"hello world".removesuffix(" world")  # "hello"
```

### Type Hinting Generics

```python
# Works without importing from typing
def get_users() -> list[User]: ...
def get_config() -> dict[str, Any]: ...
```

## Migration Checklist

### Upgrading to 3.10+

- [ ] Replace `Union[X, Y]` with `X | Y`
- [ ] Replace `Optional[X]` with `X | None`
- [ ] Consider using `match` for complex conditionals
- [ ] Use `ParamSpec` for decorator type hints

### Upgrading to 3.11+

- [ ] Replace manual task gathering with `TaskGroup`
- [ ] Use `Self` for fluent interfaces
- [ ] Handle `ExceptionGroup` if using TaskGroup

### Upgrading to 3.12+

- [ ] Use new type parameter syntax for generics
- [ ] Leverage improved f-strings
- [ ] Consider subinterpreters for parallelism

### Upgrading to 3.13+

- [ ] Test with free-threaded mode for CPU-bound code
- [ ] Review thread safety of existing code
- [ ] Consider removing multiprocessing for CPU-bound tasks
