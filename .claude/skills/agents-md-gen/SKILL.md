---
name: agents-md-gen
description: Generate AGENTS.md files for repositories
version: 1.0.0
---

# AGENTS.md Generator

## When to Use
- Setting up a new repository
- After major structural changes

## Instructions
1. Analyze: `python scripts/analyze_repo.py`
2. Generate: `python scripts/generate_agents.py`
3. Validate: `python scripts/validate.py --verbose`

## Validation
- [ ] AGENTS.md exists at repository root
- [ ] Contains required sections
- [ ] Validation exits with code 0

See [REFERENCE.md](./REFERENCE.md) for details.
