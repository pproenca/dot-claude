# Apply "Guido & Sam" Commenting Rules to Dev Skills

> **For Claude:** REQUIRED SUB-SKILL: Use super:executing-plans to implement this plan task-by-task.

**Goal:** Apply strict Python commenting standards (explain "why" not "what") to code examples in 4 dev plugin skills.

**Architecture:** Edit Python code blocks in SKILL.md and reference files to remove redundant comments, transform labels into explanations, and improve docstrings to explain contracts.

**Tech Stack:** Markdown files with Python code blocks, no dependencies.

---

## The 5 Rules

1. **Comments explain "why", not "what"** - Code shows what; comments explain why
2. **Comments must be up-to-date or deleted** - Stale comments are worse than none
3. **Docstrings for contracts, comments for implementation** - Docstrings define inputs/outputs; comments explain implementation choices
4. **No zombie code** - Use version control, not commented-out code
5. **Keep it brief** - Omit needless words

---

### Task 1: python-testing-patterns/SKILL.md - Remove Redundant Docstrings

**Files:**
- Modify: `plugins/dev/skills/python-testing-patterns/SKILL.md:45-78`

**Step 1: Remove redundant test docstrings**

Find and remove docstrings that just restate the function name:

```python
# BEFORE (lines 45-51):
def test_addition():
    """Test addition."""
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0
    assert calc.add(0, 0) == 0

# AFTER:
def test_addition():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0
    assert calc.add(0, 0) == 0
```

**Step 2: Apply same pattern to test_subtraction, test_multiplication, test_division**

Remove these redundant docstrings:
- Line 54: `"""Test subtraction."""`
- Line 61: `"""Test multiplication."""`
- Line 68: `"""Test division."""`

**Step 3: Keep meaningful docstring**

Keep this one because it explains behavior beyond the function name:
- Line 75: `"""Test division by zero raises error."""` → KEEP

**Step 4: Verify file syntax**

Run: `python -c "import ast; ast.parse(open('plugins/dev/skills/python-testing-patterns/SKILL.md').read().split('```python')[1].split('```')[0])"`

Expected: No syntax errors

**Step 5: Commit**

```bash
git add plugins/dev/skills/python-testing-patterns/SKILL.md
git commit -m "refactor(dev): remove redundant test docstrings in python-testing-patterns"
```

---

### Task 2: python-testing-patterns/SKILL.md - Remove Setup/Teardown Labels

**Files:**
- Modify: `plugins/dev/skills/python-testing-patterns/SKILL.md:110-155`

**Step 1: Remove structural labels from fixture**

```python
# BEFORE (lines 110-121):
@pytest.fixture
def db() -> Generator[Database, None, None]:
    """Fixture that provides connected database."""
    # Setup
    database = Database("sqlite:///:memory:")
    database.connect()

    # Provide to test
    yield database

    # Teardown
    database.disconnect()

# AFTER:
@pytest.fixture
def db() -> Generator[Database, None, None]:
    """Provides connected database, auto-disconnects after test."""
    database = Database("sqlite:///:memory:")
    database.connect()
    yield database
    database.disconnect()
```

**Step 2: Remove labels from api_client fixture**

```python
# BEFORE (lines 141-148):
@pytest.fixture(scope="module")
def api_client(app_config):
    """Module-scoped fixture - created once per test module."""
    # Setup expensive resource
    client = {"config": app_config, "session": "active"}
    yield client
    # Cleanup
    client["session"] = "closed"

# AFTER:
@pytest.fixture(scope="module")
def api_client(app_config):
    """Module-scoped fixture providing API client with active session."""
    client = {"config": app_config, "session": "active"}
    yield client
    client["session"] = "closed"
```

**Step 3: Commit**

```bash
git add plugins/dev/skills/python-testing-patterns/SKILL.md
git commit -m "refactor(dev): remove setup/teardown labels from fixture examples"
```

---

### Task 3: python-testing-patterns/SKILL.md - Clean Remaining Patterns

**Files:**
- Modify: `plugins/dev/skills/python-testing-patterns/SKILL.md:124-155, 206-276`

**Step 1: Remove redundant fixture docstrings**

```python
# BEFORE (line 125):
def test_database_query(db):
    """Test database query with fixture."""

# AFTER:
def test_database_query(db):
```

**Step 2: Clean mock test docstrings**

```python
# BEFORE (lines 233-246):
def test_get_user_success():
    """Test successful API call with mock."""
    client = APIClient("https://api.example.com")
    ...

# AFTER - keep this one, it explains the scenario:
def test_get_user_success():
    """Verifies mock response is correctly parsed."""
    client = APIClient("https://api.example.com")
    ...
```

**Step 3: Remove redundant exception test docstrings**

```python
# BEFORE (line 294):
def test_zero_division():
    """Test exception is raised for division by zero."""

# AFTER:
def test_zero_division():
```

**Step 4: Commit**

```bash
git add plugins/dev/skills/python-testing-patterns/SKILL.md
git commit -m "refactor(dev): clean remaining redundant docstrings"
```

---

### Task 4: python-testing-patterns/references/advanced-patterns.md

**Files:**
- Modify: `plugins/dev/skills/python-testing-patterns/references/advanced-patterns.md`

**Step 1: Remove redundant async test docstrings**

```python
# BEFORE (lines 24-28):
@pytest.mark.asyncio
async def test_fetch_data():
    """Test async function."""
    result = await fetch_data("https://api.example.com")

# AFTER:
@pytest.mark.asyncio
async def test_fetch_data():
    result = await fetch_data("https://api.example.com")
```

**Step 2: Clean conftest.py fixture labels**

```python
# BEFORE (lines 171-178):
@pytest.fixture(autouse=True)
def reset_database(database_url):
    """Auto-use fixture that runs before each test."""
    # Setup: Clear database
    print(f"Clearing database: {database_url}")
    yield
    # Teardown: Clean up
    print("Test completed")

# AFTER:
@pytest.fixture(autouse=True)
def reset_database(database_url):
    """Clears database before each test, logs completion after."""
    print(f"Clearing database: {database_url}")
    yield
    print("Test completed")
```

**Step 3: Commit**

```bash
git add plugins/dev/skills/python-testing-patterns/references/advanced-patterns.md
git commit -m "refactor(dev): apply commenting rules to advanced-patterns.md"
```

---

### Task 5: python-testing-patterns/references/database-testing.md

**Files:**
- Modify: `plugins/dev/skills/python-testing-patterns/references/database-testing.md`

**Step 1: Remove redundant test docstrings**

```python
# BEFORE (lines 40-48):
def test_create_user(db_session):
    """Test creating a user."""
    user = User(name="Test User", email="test@example.com")

# AFTER:
def test_create_user(db_session):
    user = User(name="Test User", email="test@example.com")
```

**Step 2: Apply to test_query_user and test_unique_email_constraint**

Remove:
- `"""Test querying users."""`
- `"""Test unique email constraint."""`

**Step 3: Commit**

```bash
git add plugins/dev/skills/python-testing-patterns/references/database-testing.md
git commit -m "refactor(dev): apply commenting rules to database-testing.md"
```

---

### Task 6: python-performance-optimization/SKILL.md - Transform Labels

**Files:**
- Modify: `plugins/dev/skills/python-performance-optimization/SKILL.md:127-197`

**Step 1: Remove obvious comments**

```python
# BEFORE (lines 127-136):
@profile
def memory_intensive():
    """Function that uses lots of memory."""
    # Create large list
    big_list = [i for i in range(1000000)]

    # Create large dict
    big_dict = {i: i**2 for i in range(100000)}

    # Process data
    result = sum(big_list)

# AFTER:
@profile
def memory_intensive():
    """Function that uses lots of memory."""
    big_list = [i for i in range(1000000)]
    big_dict = {i: i**2 for i in range(100000)}
    result = sum(big_list)
```

**Step 2: Transform # Slow: / # Fast: labels**

```python
# BEFORE (lines 170-181):
# Slow: Traditional loop
def slow_squares(n):
    """Create list of squares using loop."""
    result = []
    for i in range(n):
        result.append(i**2)
    return result

# Fast: List comprehension
def fast_squares(n):
    """Create list of squares using comprehension."""
    return [i**2 for i in range(n)]

# AFTER:
def slow_squares(n):
    """O(n) with repeated list.append() overhead per iteration."""
    result = []
    for i in range(n):
        result.append(i**2)
    return result

def fast_squares(n):
    """Single allocation, no per-iteration append overhead."""
    return [i**2 for i in range(n)]
```

**Step 3: Remove # Benchmark label**

```python
# BEFORE (line 183):
# Benchmark
n = 100000

# AFTER:
n = 100000
```

**Step 4: Commit**

```bash
git add plugins/dev/skills/python-performance-optimization/SKILL.md
git commit -m "refactor(dev): transform performance labels to explain complexity"
```

---

### Task 7: python-performance-optimization/SKILL.md - Continue Transformations

**Files:**
- Modify: `plugins/dev/skills/python-performance-optimization/SKILL.md:199-269`

**Step 1: Remove # Memory comparison label**

```python
# BEFORE (lines 204-210):
# Memory comparison
list_data = [i for i in range(1000000)]
gen_data = (i for i in range(1000000))

# AFTER:
list_data = [i for i in range(1000000)]
gen_data = (i for i in range(1000000)]
```

Keep the explanation comment on line 210: `# Generators use constant memory regardless of size`

**Step 2: Transform string concatenation comments**

```python
# BEFORE (lines 216-222):
# Slow: string += in loop (O(n²) for n concatenations)
result = ""
for item in items:
    result += str(item)

# Fast: use join (O(n))
result = "".join(str(item) for item in items)

# AFTER - KEEP AS IS - these explain WHY (complexity):
# O(n²) - each += creates new string, copies all previous chars
result = ""
for item in items:
    result += str(item)

# O(n) - single allocation, no intermediate copies
result = "".join(str(item) for item in items)
```

**Step 3: Transform dict/list lookup comments**

```python
# BEFORE (lines 228-236):
# O(n) search in list - slow for large collections
target in items_list

# O(1) search in dict/set - fast regardless of size
target in items_dict
target in items_set

# Use set for membership testing, dict for key-value lookups

# AFTER - KEEP complexity explanations, remove obvious:
# O(n) - must scan entire list
target in items_list

# O(1) - hash table lookup
target in items_dict
target in items_set
```

**Step 4: Commit**

```bash
git add plugins/dev/skills/python-performance-optimization/SKILL.md
git commit -m "refactor(dev): improve performance comments to explain complexity"
```

---

### Task 8: python-performance-optimization/SKILL.md - Final Cleanup

**Files:**
- Modify: `plugins/dev/skills/python-performance-optimization/SKILL.md:240-350`

**Step 1: Transform local variable comments**

```python
# BEFORE (lines 241-256):
# Global variable access is slower - LEGB lookup each time
GLOBAL_VALUE = 100

def use_global():
    total = 0
    for i in range(10000):
        total += GLOBAL_VALUE  # Slow: global lookup
    return total

def use_local():
    local_value = 100
    total = 0  # Fast: local lookup
    for i in range(10000):
        total += local_value
    return total

# AFTER:
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

**Step 2: Transform function call overhead comments**

```python
# BEFORE (lines 261-268):
# In hot loops, inline calculations instead of function calls
# Slow: function call overhead
for i in range(10000):
    total += helper_function(i)

# Fast: inline the calculation
for i in range(10000):
    total += i * 2 + 1

# AFTER:
# Function call overhead: ~100ns per call adds up in tight loops
for i in range(10000):
    total += helper_function(i)

# Inlined: no call stack overhead
for i in range(10000):
    total += i * 2 + 1
```

**Step 3: Clean numpy section comments**

```python
# BEFORE (line 296):
# Vectorized operations

# AFTER: Remove - section header is sufficient
```

**Step 4: Commit**

```bash
git add plugins/dev/skills/python-performance-optimization/SKILL.md
git commit -m "refactor(dev): finalize performance optimization comment cleanup"
```

---

### Task 9: python-performance-optimization/references/database-optimization.md

**Files:**
- Modify: `plugins/dev/skills/python-performance-optimization/references/database-optimization.md`

**Step 1: Remove redundant docstrings**

```python
# BEFORE (lines 13-17):
def create_db():
    """Create test database."""
    conn = sqlite3.connect(":memory:")

# AFTER:
def create_db():
    conn = sqlite3.connect(":memory:")
```

**Step 2: Transform slow/fast insert comments**

```python
# BEFORE (lines 19-27):
def slow_inserts(conn, count):
    """Insert records one at a time."""
    start = time.time()
    cursor = conn.cursor()
    for i in range(count):
        cursor.execute("INSERT INTO users (name) VALUES (?)", (f"User {i}",))
        conn.commit()  # Commit each insert

# AFTER:
def slow_inserts(conn, count):
    """N commits = N disk syncs, O(n) I/O operations."""
    start = time.time()
    cursor = conn.cursor()
    for i in range(count):
        cursor.execute("INSERT INTO users (name) VALUES (?)", (f"User {i}",))
        conn.commit()
```

**Step 3: Transform batch insert docstring**

```python
# BEFORE (lines 29-37):
def fast_inserts(conn, count):
    """Batch insert with single commit."""
    ...
    conn.commit()  # Single commit

# AFTER:
def fast_inserts(conn, count):
    """Single commit = single disk sync, O(1) I/O operations."""
    ...
    conn.commit()
```

**Step 4: Commit**

```bash
git add plugins/dev/skills/python-performance-optimization/references/database-optimization.md
git commit -m "refactor(dev): apply commenting rules to database-optimization.md"
```

---

### Task 10: python-performance-optimization/references/memory-optimization.md

**Files:**
- Modify: `plugins/dev/skills/python-performance-optimization/references/memory-optimization.md`

**Step 1: Remove redundant class docstrings**

```python
# BEFORE (lines 14-19):
class RegularClass:
    """Regular class with __dict__."""
    def __init__(self, x, y, z):

class SlottedClass:
    """Class with __slots__ for memory efficiency."""
    __slots__ = ['x', 'y', 'z']

# AFTER:
class RegularClass:
    """Each instance has __dict__ (56+ bytes overhead)."""
    def __init__(self, x, y, z):

class SlottedClass:
    """No __dict__, attributes stored in fixed-size array."""
    __slots__ = ['x', 'y', 'z']
```

**Step 2: Remove memory leak example docstrings**

```python
# BEFORE (lines 51-60):
def memory_leak_example():
    """Example that leaks memory."""
    leaked_objects = []
    ...

def track_memory_usage():
    """Track memory allocations."""

# AFTER:
def memory_leak_example():
    leaked_objects = []
    ...

def track_memory_usage():
```

**Step 3: Clean iterator vs list comments**

```python
# BEFORE (lines 95-108):
def process_file_list(filename):
    """Load entire file into memory."""
    with open(filename) as f:
        lines = f.readlines()  # Loads all lines

def process_file_iterator(filename):
    """Process file line by line."""
    with open(filename) as f:
        return sum(1 for line in f if line.strip())

# Iterator uses constant memory
# List loads entire file into memory

# AFTER:
def process_file_list(filename):
    """O(n) memory - entire file in RAM."""
    with open(filename) as f:
        lines = f.readlines()

def process_file_iterator(filename):
    """O(1) memory - one line at a time."""
    with open(filename) as f:
        return sum(1 for line in f if line.strip())
```

**Step 4: Commit**

```bash
git add plugins/dev/skills/python-performance-optimization/references/memory-optimization.md
git commit -m "refactor(dev): apply commenting rules to memory-optimization.md"
```

---

### Task 11: async-python-patterns/SKILL.md

**Files:**
- Modify: `plugins/dev/skills/async-python-patterns/SKILL.md`

**Step 1: Clean function docstrings**

```python
# BEFORE (lines 25-28):
async def fetch_data(url: str) -> dict:
    """Fetch data from URL asynchronously."""
    await asyncio.sleep(1)  # Simulate I/O

# AFTER:
async def fetch_data(url: str) -> dict:
    """Returns dict with url and data keys."""
    await asyncio.sleep(1)
```

**Step 2: Clean gather example**

```python
# BEFORE (lines 43-52):
async def fetch_user(user_id: int) -> dict:
    """Fetch user data."""
    await asyncio.sleep(0.5)

async def fetch_all_users(user_ids: List[int]) -> List[dict]:
    """Fetch multiple users concurrently."""

# AFTER:
async def fetch_user(user_id: int) -> dict:
    await asyncio.sleep(0.5)
    return {"id": user_id, "name": f"User {user_id}"}

async def fetch_all_users(user_ids: List[int]) -> List[dict]:
    """Runs all fetches concurrently, returns when all complete."""
```

**Step 3: Remove obvious task comments**

```python
# BEFORE (lines 75-77):
    # Create tasks
    task1 = asyncio.create_task(background_task("Task 1", 2))
    task2 = asyncio.create_task(background_task("Task 2", 1))

    # Do other work
    print("Main: doing other work")

    # Wait for tasks
    result1 = await task1

# AFTER:
    task1 = asyncio.create_task(background_task("Task 1", 2))
    task2 = asyncio.create_task(background_task("Task 2", 1))

    print("Main: doing other work")
    await asyncio.sleep(0.5)

    result1 = await task1
```

**Step 4: Keep meaningful pitfall comments**

The "Common Pitfalls" section comments explain WHY - keep them:
- `# Wrong - returns coroutine object, doesn't execute`
- `# Blocks!`
- `# Non-blocking`

**Step 5: Commit**

```bash
git add plugins/dev/skills/async-python-patterns/SKILL.md
git commit -m "refactor(dev): apply commenting rules to async-python-patterns"
```

---

### Task 12: async-python-patterns/references/advanced-patterns.md

**Files:**
- Modify: `plugins/dev/skills/async-python-patterns/references/advanced-patterns.md`

**Step 1: Clean context manager docstrings**

```python
# BEFORE (lines 17-27):
class AsyncDatabaseConnection:
    """Async database connection context manager."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.connection: Optional[object] = None

    async def __aenter__(self):
        print("Opening connection")
        await asyncio.sleep(0.1)  # Simulate connection

# AFTER:
class AsyncDatabaseConnection:
    """Manages connection lifecycle via async with."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.connection: Optional[object] = None

    async def __aenter__(self):
        print("Opening connection")
        await asyncio.sleep(0.1)
```

**Step 2: Clean producer-consumer comments**

```python
# BEFORE (lines 85-92):
async def producer(queue: Queue, producer_id: int, num_items: int):
    """Produce items and put them in queue."""
    for i in range(num_items):
        item = f"Item-{producer_id}-{i}"
        await queue.put(item)
        print(f"Producer {producer_id} produced: {item}")
        await asyncio.sleep(0.1)
    await queue.put(None)  # Signal completion

# AFTER:
async def producer(queue: Queue, producer_id: int, num_items: int):
    for i in range(num_items):
        item = f"Item-{producer_id}-{i}"
        await queue.put(item)
        print(f"Producer {producer_id} produced: {item}")
        await asyncio.sleep(0.1)
    await queue.put(None)  # Sentinel signals consumer to stop
```

**Step 3: Commit**

```bash
git add plugins/dev/skills/async-python-patterns/references/advanced-patterns.md
git commit -m "refactor(dev): apply commenting rules to async advanced-patterns.md"
```

---

### Task 13: async-python-patterns/references/real-world-examples.md

**Files:**
- Modify: `plugins/dev/skills/async-python-patterns/references/real-world-examples.md`

**Step 1: Clean web scraping docstrings**

```python
# BEFORE (lines 16-27):
async def fetch_url(session: aiohttp.ClientSession, url: str) -> Dict:
    """Fetch single URL."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:

async def scrape_urls(urls: List[str]) -> List[Dict]:
    """Scrape multiple URLs concurrently."""

# AFTER:
async def fetch_url(session: aiohttp.ClientSession, url: str) -> Dict:
    """Returns dict with url, status, length or error key."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:

async def scrape_urls(urls: List[str]) -> List[Dict]:
    """All URLs fetched concurrently, reuses single session."""
```

**Step 2: Clean database operation docstrings**

```python
# BEFORE (lines 60-68):
async def execute(self, query: str) -> List[dict]:
    """Execute query."""

async def fetch_one(self, query: str) -> Optional[dict]:
    """Fetch single row."""

# AFTER:
async def execute(self, query: str) -> List[dict]:

async def fetch_one(self, query: str) -> Optional[dict]:
```

**Step 3: Clean WebSocket docstrings**

```python
# BEFORE (lines 105-108):
async def send(self, message: str):
    """Send message."""

async def recv(self) -> str:
    """Receive message."""

# AFTER:
async def send(self, message: str):

async def recv(self) -> str:
```

**Step 4: Commit**

```bash
git add plugins/dev/skills/async-python-patterns/references/real-world-examples.md
git commit -m "refactor(dev): apply commenting rules to async real-world-examples.md"
```

---

### Task 14: python-packaging/SKILL.md

**Files:**
- Modify: `plugins/dev/skills/python-packaging/SKILL.md`

**Step 1: Review Python code blocks**

Most of this file is TOML configuration. Only CLI examples need review.

**Step 2: Clean CLI docstrings**

```python
# BEFORE (lines 249-258):
@click.group()
@click.version_option()
def cli():
    """My awesome CLI tool."""
    pass

@cli.command()
@click.argument("name")
@click.option("--greeting", default="Hello", help="Greeting to use")
def greet(name: str, greeting: str):
    """Greet someone."""
    click.echo(f"{greeting}, {name}!")

# AFTER - Keep CLI docstrings, they become --help text:
@click.group()
@click.version_option()
def cli():
    """My awesome CLI tool."""
    pass

@cli.command()
@click.argument("name")
@click.option("--greeting", default="Hello", help="Greeting to use")
def greet(name: str, greeting: str):
    """Greet someone."""  # This is intentional - becomes help text
    click.echo(f"{greeting}, {name}!")
```

**Step 3: Clean argparse example**

```python
# BEFORE (lines 296-331):
def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(...)

# AFTER:
def main():
    parser = argparse.ArgumentParser(...)
```

**Step 4: Commit**

```bash
git add plugins/dev/skills/python-packaging/SKILL.md
git commit -m "refactor(dev): apply commenting rules to python-packaging CLI examples"
```

---

### Task 15: python-packaging/references/advanced-patterns.md

**Files:**
- Modify: `plugins/dev/skills/python-packaging/references/advanced-patterns.md`

**Step 1: Review and clean Python code blocks**

Scan for redundant docstrings and apply rules.

**Step 2: Commit**

```bash
git add plugins/dev/skills/python-packaging/references/advanced-patterns.md
git commit -m "refactor(dev): apply commenting rules to packaging advanced-patterns.md"
```

---

### Task 16: Validation

**Files:**
- All modified files

**Step 1: Run plugin validation**

Run: `./scripts/validate-plugins.sh`

Expected: All validations passed

**Step 2: Check line counts**

```bash
wc -l plugins/dev/skills/*/SKILL.md
```

Expected: All under 500 lines

**Step 3: Final commit if needed**

```bash
git status
# If any uncommitted changes:
git add -A
git commit -m "refactor(dev): final cleanup after commenting rules applied"
```
