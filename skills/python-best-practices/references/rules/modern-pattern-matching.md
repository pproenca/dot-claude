---
title: Use Structural Pattern Matching
impact: MEDIUM-HIGH
impactDescription: Cleaner conditional logic
tags: modern, match, case, pattern-matching, python310
---

## Use Structural Pattern Matching

Use `match`/`case` statements for complex conditional logic instead of if/elif chains.

**Incorrect (long if/elif chains):**

```python
def handle_command(command: dict) -> str:
    if command.get("type") == "move":
        direction = command.get("direction")
        if direction == "north":
            return move_north()
        elif direction == "south":
            return move_south()
    elif command.get("type") == "attack":
        target = command.get("target")
        if target is not None:
            return attack(target)
    elif command.get("type") == "quit":
        return quit_game()
    return "Unknown command"
```

**Correct (using pattern matching):**

```python
def handle_command(command: dict) -> str:
    match command:
        case {"type": "move", "direction": "north"}:
            return move_north()
        case {"type": "move", "direction": "south"}:
            return move_south()
        case {"type": "attack", "target": target} if target:
            return attack(target)
        case {"type": "quit"}:
            return quit_game()
        case _:
            return "Unknown command"
```

Reference: [PEP 636 - Structural Pattern Matching Tutorial](https://peps.python.org/pep-0636/)
