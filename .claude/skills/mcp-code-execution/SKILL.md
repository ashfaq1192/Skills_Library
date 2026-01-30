---
name: mcp-code-execution
description: MCP Code Execution pattern reference implementation
version: 1.0.0
---

# MCP Code Execution Pattern

## When to Use
- Creating new token-efficient skills
- Wrapping MCP operations in scripts
- Reducing context window consumption

## Pattern
1. **SKILL.md** (~100 tokens) - Instructions only
2. **scripts/** (0 tokens) - Executable logic
3. **Result** (<50 tokens) - Filtered output

## Key Rule
Scripts filter data BEFORE returning to context. Never return full datasets.

```python
# scripts/operation.py (0 tokens loaded)
result = subprocess.run(["kubectl", "get", "pods", "-o", "json"], ...)
pods = json.loads(result.stdout)["items"]
running = sum(1 for p in pods if p["status"]["phase"] == "Running")
print(f"✓ {running}/{len(pods)} pods running")  # Only this enters context
```

## Validation
- [ ] SKILL.md under 150 tokens
- [ ] Scripts filter data before returning
- [ ] Output is status + minimal data only

See [REFERENCE.md](./REFERENCE.md) for examples, anti-patterns, and implementation guide.
