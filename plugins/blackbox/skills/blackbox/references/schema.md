# Blackbox Data Schema

## Directory Structure

```
data/
├── buffer.jsonl     # Event log (append-only)
└── objects/         # Content-Addressable Storage (CAS)
    └── <ab>/        # First 2 chars of SHA1
        └── <rest>   # Remaining 38 chars (immutable, 0o444)
```

## buffer.jsonl Format

Each line is a JSON object:

```json
{
  "t": 1700000000.123,      // Unix timestamp (float)
  "e": "PreToolUse",        // Event type
  "h": "abc123...",         // SHA1 hash of file (40 chars) or null
  "skipped": "binary_or_oversize",  // Optional: why file was skipped
  "d": { ... }              // Full event data from Claude Code
}
```

### Event Types

| Event | Description | Has Hash |
|-------|-------------|----------|
| `SessionStart` | New session began | No |
| `UserPromptSubmit` | User submitted prompt | No |
| `PreToolUse` | Before Write/Edit/MultiEdit | Yes (if file exists) |

### Event Data (`d` field)

For `PreToolUse` events:
```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.py",
    "content": "..."  // For Write tool
  }
}
```

## CAS Objects

- Path: `objects/<hash[0:2]>/<hash[2:]>`
- Permissions: `0o444` (read-only)
- Content: Exact file bytes at snapshot time

### Limitations

- Max file size: 2MB
- Binary files: Skipped (null bytes in first 512 bytes)
- Empty files: Hash `da39a3ee5e6b4b0d3255bfef95601890afd80709`
