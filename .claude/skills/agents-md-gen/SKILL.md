---
name: agents-md-gen
description: Generate AGENTS.md files for repositories by analyzing structure and conventions
version: 1.0.0
---

# agents-md-gen

Generate standardized AGENTS.md files following AAIF standards.

## When to Use

- Setting up a new repository that needs AGENTS.md
- Regenerating AGENTS.md after structural changes
- Validating existing AGENTS.md quality

## Prerequisites

- Python 3.8+ installed: `python3 --version`
- Repository with recognizable structure (src/, tests/, etc.)
- Git repository initialized: `git status` (optional but recommended)
- Write access to repository root directory

## Before Implementation

Gather context to ensure accurate AGENTS.md generation:

| Source | Gather |
|--------|--------|
| **Repository Structure** | Directory tree, main code locations, build artifacts to exclude |
| **Tech Stack** | Languages, frameworks, build tools, package managers |
| **Conventions** | Code style (PEP8, ESLint), naming patterns, file organization |
| **Documentation** | Existing README.md, CONTRIBUTING.md, code comments density |

## Required Clarifications

1. **Repository Type**: What kind of repository is this?
   - Application (monolith, microservices)
   - Library/framework (reusable components)
   - Skills library (AI agent skills)
   - Documentation site (Docusaurus, MkDocs)

2. **Target Audience**: Who will use AGENTS.md?
   - AI agents only (Claude Code, Goose)
   - Human developers + agents (hybrid)
   - Cross-functional teams (include non-technical context)

3. **Detail Level**: How detailed should AGENTS.md be?
   - Minimal (structure + conventions only)
   - Standard (+ architecture overview, common tasks)
   - Comprehensive (+ examples, troubleshooting, FAQs)

4. **Maintenance Strategy**: How will AGENTS.md stay current?
   - Manual updates (developer responsibility)
   - Regenerate on major changes (use this skill)
   - Automated CI/CD validation (check on PRs)

## Instructions

Execute from repository root:

```bash
# 1. Analyze repository structure
python .claude/skills/agents-md-gen/scripts/analyze_repo.py

# 2. Generate AGENTS.md
python .claude/skills/agents-md-gen/scripts/generate_agents.py

# 3. Validate output
python .claude/skills/agents-md-gen/scripts/validate.py --verbose
```

One-liner:
```bash
python .claude/skills/agents-md-gen/scripts/analyze_repo.py && \
python .claude/skills/agents-md-gen/scripts/generate_agents.py && \
python .claude/skills/agents-md-gen/scripts/validate.py
```

## Validation

- [ ] .agents_analysis.json created (intermediate data)
- [ ] AGENTS.md created at repository root
- [ ] File contains 7 required sections
- [ ] Validation returns exit code 0
- [ ] File size > 100 bytes

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Script not found | Run from repository root, verify skill installed in `.claude/skills/` |
| Permission denied | Check file permissions, ensure scripts are executable |
| Incomplete sections | Review .agents_analysis.json, add missing context manually |
| Validation fails | Check AGENTS.md structure, ensure all required sections present |

## Official Documentation

- AAIF Standards: https://aaif.io/
- AGENTS.md Spec: https://aaif.io/agents-md
- Claude Code: https://claude.com/claude-code
