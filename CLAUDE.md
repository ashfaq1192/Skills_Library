# Claude Code Rules - Skills Library (Hackathon III)

## Repository Purpose

This is **Repository 1** of Hackathon III deliverables: A library of reusable Skills that teach AI agents (Claude Code and Goose) how to build cloud-native, event-driven applications using the MCP Code Execution pattern.

**Important:** This repository is designed to work standalone OR as part of a larger workspace.

## Quick Reference

- **Constitution:** `.specify/memory/constitution.md` - Skill development principles
- **Available Skills:** See README.md for catalog
- **Skill Structure:** `.claude/skills/<skill-name>/`
- **PHRs:** `history/prompts/` - Development process tracking
- **ADRs:** `history/adr/` - Architecture decisions

## Core Principles (Skill Development)

### 1. MCP Code Execution Pattern
- **SKILL.md:** ~100 tokens (instructions only)
- **scripts/:** Heavy logic (executed, not loaded into context)
- **Result:** 78.5% token reduction vs. direct MCP integration

### 2. Cross-Agent Compatibility
- Every skill MUST work on BOTH Claude Code and Goose
- Test with both agents before considering complete

### 3. Skill Autonomy
- Single prompt → complete deployment
- Zero manual intervention
- Clear validation checkboxes

## Skill Development Workflow

### Creating a New Skill

1. **Plan the skill:**
   ```bash
   claude "Create a spec for <skill-name> that <description>"
   ```

2. **Create structure:**
   ```bash
   mkdir -p .claude/skills/<skill-name>/scripts
   ```

3. **Write SKILL.md (~100 tokens):**
   - YAML frontmatter: name, description, version
   - When to Use, Prerequisites, Instructions, Validation
   - See `.specify/templates/` for templates

4. **Implement scripts:**
   - Python for complex logic
   - Bash for simple kubectl/helm operations
   - Make executable: `chmod +x scripts/*.sh`

5. **Write REFERENCE.md:**
   - Architecture overview
   - Configuration options
   - Troubleshooting guide

6. **Test with both agents:**
   ```bash
   claude "Use <skill-name> to <task>"
   goose "Use <skill-name> to <task>"  # Same result expected
   ```

7. **Commit:**
   ```bash
   git commit -m "feat: add <skill-name> skill with MCP code execution"
   ```

### Updating an Existing Skill

1. Read current SKILL.md and REFERENCE.md
2. Test current version (don't break working functionality)
3. Make changes and bump version (semver)
4. Re-test with both agents
5. Update REFERENCE.md with changes
6. Commit with descriptive message

## Required Skills Checklist

### Core Infrastructure (7 Required)
- [ ] agents-md-gen - Generate AGENTS.md
- [ ] k8s-foundation - K8s operations
- [ ] kafka-k8s-setup - Deploy Kafka
- [ ] neon-postgres-setup - Setup Neon DB
- [ ] dapr-setup - Install Dapr
- [ ] mcp-code-execution - MCP pattern implementation
- [ ] docusaurus-deploy - Deploy docs

### Application Skills (4 Required)
- [ ] fastapi-dapr-agent - Generate microservices
- [ ] nextjs-k8s-deploy - Deploy Next.js
- [ ] better-auth-setup - Configure auth
- [ ] kong-gateway-setup - Deploy API gateway

## Quality Gates (Must Pass Before Skill is Complete)

- [ ] SKILL.md is ≤150 tokens
- [ ] Scripts are executable: `chmod +x scripts/*.sh`
- [ ] Tested with Claude Code - works as expected
- [ ] Tested with Goose - equivalent result
- [ ] REFERENCE.md is comprehensive
- [ ] No hardcoded secrets or credentials
- [ ] Validation checklist in SKILL.md is complete
- [ ] Error messages are actionable
- [ ] PHR created documenting development process

## PHR Creation for Skills

After creating/updating a skill, create a PHR:

```bash
# Use the sp.phr skill if available, or create manually
# PHRs go in: history/prompts/general/ (for skill development)
```

**PHR Requirements:**
- Record user input verbatim
- Capture key assistant output
- List files created/modified
- Document testing results
- Note any architectural decisions

## Evaluation Criteria Reminders

Your skills will be judged on:

| Criterion | Weight | What to Optimize |
|-----------|--------|------------------|
| Skills Autonomy | 15% | Single prompt → complete deployment |
| Token Efficiency | 10% | SKILL.md ~100 tokens, scripts do work |
| Cross-Agent | 5% | Works on Claude Code AND Goose |
| Architecture | 20% | Correct cloud-native patterns |
| MCP Integration | 10% | Code execution pattern implemented |
| Documentation | 10% | Comprehensive REFERENCE.md |

## Common Skill Patterns

### Pattern 1: Deploy Infrastructure (Kafka, PostgreSQL, Dapr)

**SKILL.md Template:**
```markdown
---
name: kafka-k8s-setup
description: Deploy Apache Kafka to Kubernetes
version: 1.0.0
---

## Instructions
1. Run: `python scripts/deploy_kafka.py --namespace <namespace>`
2. Verify: Output shows "✓ Kafka ready: 3/3 brokers running"

## Validation
- [ ] Kafka pods are running: `kubectl get pods -n <namespace>`
- [ ] Topics created successfully
- [ ] Health checks passing
```

**Script Pattern:**
```python
#!/usr/bin/env python3
import subprocess, sys

def deploy_kafka(namespace):
    # 1. Execute helm/kubectl commands
    result = subprocess.run([...], capture_output=True, text=True)

    # 2. Filter output (don't dump everything to context)
    if result.returncode == 0:
        # 3. Return minimal success message
        print(f"✓ Kafka ready: 3/3 brokers running")
        return 0
    else:
        # 4. Provide actionable error
        print(f"❌ Error: {result.stderr}")
        print(f"→ Check kubectl access: kubectl cluster-info")
        return 1

if __name__ == "__main__":
    namespace = sys.argv[1] if len(sys.argv) > 1 else "default"
    sys.exit(deploy_kafka(namespace))
```

### Pattern 2: Generate Code (FastAPI microservices, Next.js)

**SKILL.md Template:**
```markdown
---
name: fastapi-dapr-agent
description: Generate FastAPI microservice with Dapr + AI
version: 1.0.0
---

## Instructions
1. Run: `python scripts/generate_service.py --name <service-name> --output <path>`
2. Verify: Output shows "✓ Service generated: <path>"

## Validation
- [ ] Service code generated
- [ ] Dapr configuration present
- [ ] Health endpoint exists
- [ ] Requirements.txt included
```

**Script Pattern:**
```python
#!/usr/bin/env python3
from pathlib import Path
import jinja2

def generate_service(name, output_path):
    # 1. Load template
    template = Path("templates/fastapi_service.py.j2").read_text()

    # 2. Render with parameters
    rendered = jinja2.Template(template).render(service_name=name)

    # 3. Write files
    output = Path(output_path)
    output.mkdir(parents=True, exist_ok=True)
    (output / "main.py").write_text(rendered)

    # 4. Return minimal success message
    print(f"✓ Service generated: {output}")
    return 0
```

## Troubleshooting

### Issue: "Skill not recognized by agent"
**Solution:**
- Verify SKILL.md is in `.claude/skills/<name>/SKILL.md`
- Check YAML frontmatter syntax (--- at start and end)
- Restart agent session

### Issue: "Script execution fails"
**Solution:**
- Test script directly: `python scripts/script.py`
- Check file is executable: `chmod +x scripts/*.sh`
- Verify prerequisites are met (kubectl, helm, etc.)

### Issue: "Works in Claude Code but not Goose"
**Solution:**
- Check for agent-specific paths (e.g., `~/.claude/`)
- Use relative paths from skill directory
- Test script standalone without agent

## Security Guidelines

- ❌ NEVER hardcode credentials, tokens, secrets
- ✅ Use environment variables: `os.getenv("DB_PASSWORD")`
- ✅ Use Kubernetes Secrets for sensitive data
- ✅ Validate inputs to prevent injection
- ✅ Document required env vars in SKILL.md

## Working with Parent Workspace

If this repository is part of a larger workspace (Hackathon-III/):
- Parent workspace may have shared resources (specs/, research docs)
- This repository should still work standalone
- All skill-specific files stay in this repository
- PHRs can be created in either location

## Submission Requirements

Before submitting skills-library:
- [ ] All required skills (11 minimum) are present
- [ ] Each skill passes quality gates
- [ ] README.md is complete and accurate
- [ ] AGENTS.md reflects current structure
- [ ] .gitignore excludes temporary files
- [ ] No hardcoded secrets or credentials
- [ ] PHRs demonstrate development process

## References

- **Full Constitution:** `.specify/memory/constitution.md`
- **README:** README.md (skill catalog and quick start)
- **AGENTS.md:** Repository structure and conventions
- **Templates:** `.specify/templates/` (spec, plan, task templates)
- **Hackathon Requirements:** (see parent workspace if available)

---

**Version:** 1.0.0
**Last Updated:** 2026-01-27
**Hackathon:** Reusable Intelligence and Cloud-Native Mastery (Hackathon III)
