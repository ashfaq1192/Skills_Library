---
name: mcp-code-execution
description: |
  Reference implementation and guide for MCP Code Execution pattern. This skill should
  be used when learning how to create token-efficient skills, understanding the pattern
  of wrapping operations in scripts, or teaching AI agents about code execution approach.
---

# MCP Code Execution Pattern

Learn and implement the MCP Code Execution pattern for token-efficient skills.

## Pattern Overview

**Problem**: Direct MCP integration loads tools into context (15,000+ tokens), consuming 41% before work begins.

**Solution**: Code Execution pattern achieves 78.5% token reduction:
1. **SKILL.md** (~100 tokens) - Instructions (WHAT to do)
2. **scripts/** (0 tokens loaded) - Executable code (HOW to do it)
3. **Result** (< 50 tokens) - Filtered output only

## When to Use

- Creating new skills for Claude Code/Goose
- Reducing token consumption in existing skills
- Wrapping MCP operations in scripts
- Teaching the pattern to other developers

## Prerequisites

- Understanding of MCP (Model Context Protocol) concepts
- Python 3.8+ for script development
- Familiarity with agent workflows (Claude Code or Goose)
- Target operation tools installed (kubectl, psql, helm, etc.)

## Before Implementation

Gather context to ensure successful MCP Code Execution implementation:

| Source | Gather |
|--------|--------|
| **Existing MCP Integration** | Current token usage, MCP server configuration, tools loaded |
| **Target Operation** | What MCP operation to wrap (kubectl, database query, API call) |
| **Expected Data Volume** | Size of data returned by operation (rows, objects, file sizes) |
| **Filtering Requirements** | What subset of data is actually needed by agent |

## Required Clarifications

1. **Current Implementation**: What is the starting point?
   - Direct MCP integration (MCP server with tools loaded at startup)
   - Manual script execution (no standardized pattern)
   - Existing skill structure (needs optimization)

2. **Operation Complexity**: How complex is the wrapped operation?
   - Simple command (single kubectl/psql call)
   - Multi-step workflow (deploy → verify → configure)
   - Data transformation (filter, aggregate, format)

3. **Output Requirements**: What output should reach agent context?
   - Status only ("✓ Success" or "❌ Failed")
   - Summary statistics ("5/5 pods running, 3 topics created")
   - Filtered data (specific rows, objects, or fields)
   - Full output (only when small and essential)

4. **Error Handling**: How should errors be communicated?
   - Exit codes (0 for success, non-zero for failure)
   - Structured error messages with actionable guidance
   - Logs for debugging (separate from context output)

## Pattern Implementation

### 1. Minimal SKILL.md
```markdown
---
name: example-skill
description: Brief description under 1024 chars
---

## Instructions
1. Run: `python scripts/operation.py --param value`
2. Verify: Check output shows "✓ Success"
```

### 2. Script Execution
```python
# scripts/operation.py
import subprocess

# Execute operation (kubectl, psql, API calls, etc.)
result = subprocess.run(["kubectl", "get", "pods"], ...)

# Filter data BEFORE returning to context
# Return only: status + minimal essential data
if result.returncode == 0:
    print("✓ 5/5 pods running")  # NOT full kubectl output
    return 0
```

### 3. Result in Context
```
User: "Use example-skill"
Agent reads SKILL.md (~100 tokens) → Executes script → Gets "✓ 5/5 pods running" (~10 tokens)
Total context: ~110 tokens vs 15,000+ with direct MCP
```

## Token Comparison

| Approach | Startup | Per Use | Total (5 uses) |
|----------|---------|---------|----------------|
| Direct MCP | 15,000 | 500 | 17,500 |
| Code Execution | 0 | 110 | 550 |
| **Savings** | **100%** | **78%** | **96.9%** |

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Solution |
|--------------|--------------|----------|
| Loading full MCP tools | 15,000+ tokens at startup | Use Code Execution pattern |
| Returning full datasets | Floods context with noise | Filter in script, return summary |
| Complex logic in SKILL.md | Inflates token count | Move to scripts/ directory |
| No error handling | Cryptic failures | Return actionable error messages |

## Official Documentation

- MCP Code Execution: https://www.anthropic.com/engineering/code-execution-with-mcp
- Claude Code: https://claude.com/claude-code
- Goose: https://block.github.io/goose/
