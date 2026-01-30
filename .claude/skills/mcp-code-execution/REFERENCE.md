# MCP Code Execution Pattern - Reference Documentation

**Version**: 1.0.0
**Created**: 2026-01-27
**Purpose**: Reference implementation and guide for the MCP Code Execution pattern

## Overview

The MCP Code Execution pattern is the core innovation of Hackathon III. Instead of loading MCP (Model Context Protocol) tools directly into an AI agent's context window, operations are wrapped in Skills that execute scripts. This achieves 78-98% token reduction while maintaining full capability.

### The Problem

Direct MCP integration consumes context aggressively:

| Approach | Startup Cost | Per-Operation | 5 Operations |
|----------|-------------|---------------|-------------|
| Direct MCP (5 servers) | 50,000 tokens | 500-25,000 tokens | 75,000+ tokens |
| Code Execution | 0 tokens | 100-150 tokens | 550 tokens |
| **Savings** | **100%** | **78-99%** | **99.3%** |

### The Solution

```
Direct MCP (BAD):
  Agent loads 15,000+ tokens of tool definitions at startup
  Every operation returns full dataset into context

Code Execution (GOOD):
  SKILL.md (~100 tokens) tells agent WHAT to do
  scripts/*.py does the work (0 tokens loaded)
  Only final result enters context ("✓ Done" + minimal data)
```

## Pattern Architecture

```
┌──────────────────────────────────────────────┐
│ Agent Context Window                          │
│                                               │
│  ┌──────────────┐    ┌────────────────────┐  │
│  │ SKILL.md     │    │ Script Result      │  │
│  │ ~100 tokens  │    │ "✓ 5/5 pods ready" │  │
│  │              │    │ ~10 tokens         │  │
│  └──────┬───────┘    └────────▲───────────┘  │
│         │                     │              │
└─────────┼─────────────────────┼──────────────┘
          │                     │
          ▼                     │
┌─────────────────────┐        │
│ Script Execution    │        │
│ (Outside Context)   │────────┘
│                     │
│ - kubectl get pods  │  ← 10,000 tokens of data
│ - Filter to 5 pods  │  ← Processed in script
│ - Return summary    │  ← Only 10 tokens returned
└─────────────────────┘
```

## Implementation Guide

### Step 1: Create Skill Structure

```
.claude/skills/<skill-name>/
├── SKILL.md              # ~100 tokens (instructions only)
├── REFERENCE.md          # Deep docs (loaded on-demand)
└── scripts/
    ├── operation.py      # Main operation script
    ├── verify.py         # Validation script
    └── templates/        # Configuration templates (optional)
```

### Step 2: Write SKILL.md (~100 Tokens)

```markdown
---
name: example-skill
description: Brief description of what this skill does
version: 1.0.0
---

# Skill Name

## When to Use
- Use case 1

## Instructions
1. Run: `python scripts/operation.py --param value`
2. Verify: `python scripts/verify.py`

## Validation
- [ ] Expected outcome 1
- [ ] Expected outcome 2
```

**Rules:**
- YAML frontmatter: name, description, version
- Keep under 150 tokens (aim for ~100)
- Instructions reference scripts, not inline logic
- Include validation checklist

### Step 3: Write Scripts (0 Tokens Loaded)

```python
#!/usr/bin/env python3
"""Script that executes operations and returns minimal output."""
import subprocess
import sys
import json

def main():
    # 1. Execute the operation
    result = subprocess.run(
        ["kubectl", "get", "pods", "-o", "json"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}")
        sys.exit(1)

    # 2. FILTER data in the script (critical!)
    pods = json.loads(result.stdout)["items"]
    running = [p for p in pods if p["status"]["phase"] == "Running"]

    # 3. Return ONLY minimal summary to context
    print(f"✓ {len(running)}/{len(pods)} pods running")
    sys.exit(0)

if __name__ == "__main__":
    main()
```

**Rules:**
- Filter/process data IN the script before returning
- Return status + minimal essential data only
- Use exit codes: 0 = success, 1 = failure
- Include actionable error messages
- No external dependencies when possible (use stdlib)

### Step 4: Verify Token Efficiency

```bash
# Count SKILL.md tokens (approximate: words * 1.3)
wc -w .claude/skills/*/SKILL.md

# Target: under 150 words per SKILL.md
```

## Pattern Examples

### Example 1: Kubernetes Operations

**Bad (Direct MCP):**
```
TOOL CALL: kubectl.getPods(namespace: "learnflow")
→ Returns 200+ lines of pod details into context (5,000 tokens)
```

**Good (Code Execution):**
```python
# scripts/get_pods.py
result = subprocess.run(["kubectl", "get", "pods", "-n", "learnflow", "-o", "json"], ...)
pods = json.loads(result.stdout)["items"]
running = sum(1 for p in pods if p["status"]["phase"] == "Running")
print(f"✓ {running}/{len(pods)} pods running in learnflow")
# Context receives: "✓ 5/5 pods running in learnflow" (10 tokens)
```

### Example 2: Database Operations

**Bad (Direct MCP):**
```
TOOL CALL: postgres.query("SELECT * FROM users")
→ Returns 10,000 rows into context (50,000 tokens)
```

**Good (Code Execution):**
```python
# scripts/count_users.py
import psycopg2
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM users")
count = cur.fetchone()[0]
print(f"✓ {count} users in database")
# Context receives: "✓ 1,234 users in database" (8 tokens)
```

### Example 3: API Calls

**Bad (Direct MCP):**
```
TOOL CALL: http.get("https://api.example.com/data")
→ Returns full JSON response (15,000 tokens)
```

**Good (Code Execution):**
```python
# scripts/check_api.py
import urllib.request, json
response = urllib.request.urlopen("https://api.example.com/health")
data = json.loads(response.read())
print(f"✓ API healthy: {data['status']}, version {data['version']}")
# Context receives: "✓ API healthy: ok, version 2.1.0" (12 tokens)
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|-------------|---------|----------|
| MCP tools at startup | 15,000+ tokens consumed | Use Code Execution pattern |
| Full dataset return | Floods context | Filter in script, return summary |
| Logic in SKILL.md | Inflates token count | Move to scripts/ |
| No error handling | Cryptic failures | Return actionable messages |
| Hard-coded values | Not reusable | Use CLI arguments |
| Large REFERENCE.md in context | Wastes tokens | Load on-demand only |

## Token Budget Guidelines

| Component | Target | Maximum |
|-----------|--------|---------|
| SKILL.md | ~100 tokens | 150 tokens |
| Script output (success) | ~10 tokens | 50 tokens |
| Script output (error) | ~30 tokens | 100 tokens |
| REFERENCE.md | 0 tokens (on-demand) | N/A |
| **Total per skill use** | **~110 tokens** | **200 tokens** |

## Cross-Agent Compatibility

Both Claude Code and Goose can execute skills from `.claude/skills/`:

### Claude Code
- Reads SKILL.md from `.claude/skills/<name>/SKILL.md`
- Recognizes YAML frontmatter
- Executes scripts via Python/Bash

### Goose
- Same directory structure works
- Same script execution model
- Same output parsing

### Compatibility Checklist
- [ ] Scripts use standard Python (3.9+)
- [ ] No agent-specific paths or APIs
- [ ] Scripts are executable (`chmod +x scripts/*.sh`)
- [ ] Output is plain text (no ANSI colors that one agent might not parse)
- [ ] Exit codes are standard (0 = success, 1 = failure)

## Testing Your Pattern

### Verify Token Count
```bash
# Approximate token count (words * 1.3)
wc -w .claude/skills/my-skill/SKILL.md
# Should be under 115 words (~150 tokens)
```

### Verify Script Isolation
```bash
# Script should work standalone
python scripts/operation.py --param value
echo $?  # Should be 0 or 1
```

### Verify Minimal Output
```bash
# Output should be 1-3 lines max
python scripts/operation.py 2>&1 | wc -l
# Should be <= 5 lines
```

## References

- [MCP Code Execution (Anthropic Blog)](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Code Skills](https://docs.anthropic.com/en/docs/claude-code)
- [Goose Documentation](https://block.github.io/goose/)
- [AAIF Standards](https://aaif.io/)
