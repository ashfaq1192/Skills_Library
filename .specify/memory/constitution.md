<!--
Sync Impact Report:
- Version: 1.0.0 (initial constitution for skills-library repository)
- Purpose: Govern skill development for Hackathon III Skills Library
- Scope: Skill creation, testing, and maintenance standards
- Parent Constitution: ../../../.specify/memory/constitution.md (hackathon-wide)
-->

# Skills Library Constitution

## Mission Statement

This repository provides **reusable, autonomous Skills** that teach AI agents (Claude Code and Goose) how to build cloud-native, event-driven applications using the MCP Code Execution pattern.

**Success Criteria:** Any AI agent can use these skills to deploy production-ready infrastructure with a single prompt.

## Core Principles

### I. MCP Code Execution Pattern (MANDATORY)

**Heavy Logic in Scripts, Minimal Instructions in SKILL.md**

Every skill MUST follow this architecture:
- **SKILL.md**: ~100 tokens (instructions only - WHAT to do)
- **scripts/**: 0 tokens loaded (HOW to do it - executed, not read)
- **REFERENCE.md**: Deep docs (loaded on-demand only)

**Token Budget per Skill:**
- SKILL.md: ≤150 tokens (strict limit)
- Script output: ≤50 tokens (filtered results only)
- Total context consumption: ≤200 tokens per skill invocation

**Script Design Principles:**
- Execute operations directly (kubectl, psql, helm, kafka-python, etc.)
- Filter data BEFORE returning to agent (e.g., 10,000 rows → 5 relevant rows)
- Return only: status message + minimal essential data
- Exit codes: 0 = success, non-zero = failure (agent can check)
- Never dump full datasets, logs, or verbose output into agent context

**Anti-Pattern (DON'T DO THIS):**
```yaml
# BAD: Loading MCP server into agent context
# ~/.claude/mcp.json
{
  "servers": {
    "kubernetes": { "command": "mcp-k8s-server" }
  }
}
# Problem: 15,000 tokens loaded at startup (41% context consumed)
```

**Correct Pattern:**
```markdown
# SKILL.md (~100 tokens)
## Instructions
1. Run: `python scripts/deploy_kafka.py --namespace learnflow`
2. Verify: Check output shows "✓ Kafka ready"

# scripts/deploy_kafka.py (0 tokens loaded, executed only)
# - Runs kubectl/helm commands
# - Checks pod readiness
# - Returns: "✓ Kafka ready: 3/3 brokers running"
```

**Rationale:** Direct MCP integration = 41% token consumption. Code execution = 3% consumption (78.5% reduction).

---

### II. Cross-Agent Compatibility (MANDATORY)

**Every Skill MUST Work Identically on Claude Code AND Goose**

Compatibility checklist (MUST pass before skill is considered complete):
- [ ] Skills in `.claude/skills/` directory (both agents read from here)
- [ ] SKILL.md follows standard format (YAML frontmatter + Markdown)
- [ ] Scripts are executable standalone: `chmod +x scripts/*.sh`
- [ ] No hardcoded agent-specific paths (e.g., `~/.claude/`)
- [ ] Tested with Claude Code: `claude "Use <skill> to deploy Kafka"`
- [ ] Tested with Goose: `goose "Use <skill> to deploy Kafka"`
- [ ] Both agents produce equivalent results
- [ ] Any quirks documented in REFERENCE.md

**Common Portability Issues:**
- ❌ Using agent-specific environment variables
- ❌ Assuming specific working directories
- ❌ Hardcoding absolute paths
- ✅ Using relative paths from skill directory
- ✅ Accepting parameters via command-line arguments
- ✅ Detecting environment and adapting (e.g., detect OS, check if kubectl installed)

**Rationale:** Cross-agent compatibility is 5% of hackathon evaluation. Skills that only work on one agent are not truly reusable.

---

### III. Skill Autonomy (MANDATORY)

**Single Prompt → Complete Deployment, Zero Manual Intervention**

Gold standard:
```bash
claude "Deploy Kafka to Kubernetes namespace 'learnflow'"
# ✓ Kafka deployed with 3 brokers
# ✓ Topics created: learning.events, code.submitted, struggle.detected
# ✓ Health checks passing
# No follow-up questions, no manual steps, no "please run X next"
```

Autonomy requirements:
- Skill MUST handle all steps end-to-end (no "now run this other skill" instructions)
- MUST verify success and report clear status
- MUST handle common failures gracefully (e.g., namespace doesn't exist → create it)
- MUST provide actionable error messages if it fails
- MUST NOT ask clarifying questions (instructions should be complete)

**When Autonomy is Impossible:**
- If user input is genuinely required (e.g., "Enter database password"), skill MUST:
  - Clearly document this in SKILL.md under "Prerequisites"
  - Provide defaults or environment variable options
  - Explain why the input is necessary

**Rationale:** Skills Autonomy is 15% of evaluation (highest weight). Manual intervention reduces score dramatically.

---

### IV. Skill Structure Standards (MANDATORY)

**Consistent Directory Layout for All Skills**

Required structure:
```
.claude/skills/<skill-name>/
├── SKILL.md              # ~100 tokens: name, description, instructions, validation
├── REFERENCE.md          # Deep docs: architecture, troubleshooting, examples
└── scripts/
    ├── *.py              # Python scripts (preferred for complex logic)
    ├── *.sh              # Bash scripts (for simple kubectl/helm operations)
    └── templates/        # Optional: K8s manifests, config files
```

**SKILL.md Required Sections:**
```markdown
---
name: skill-name
description: One-line description (under 60 chars)
version: 1.0.0
---

# Skill Name

Brief overview (1-2 sentences).

## When to Use
- Use case 1
- Use case 2

## Prerequisites
- Requirement 1 (e.g., "Kubernetes cluster running")
- Requirement 2 (e.g., "kubectl configured")

## Instructions
1. Step 1: `python scripts/command.py --arg value`
2. Step 2: Verify output shows "✓ Success"

## Validation
- [ ] Check 1 (how to verify it worked)
- [ ] Check 2

## Troubleshooting
- Issue: Symptom → Solution

## See Also
- REFERENCE.md for deep documentation
```

**REFERENCE.md Recommended Sections:**
- Architecture Overview (what the skill deploys)
- Technical Details (how it works internally)
- Configuration Options (all script parameters explained)
- Advanced Usage (complex scenarios)
- Troubleshooting Guide (common issues and solutions)
- Examples (real-world use cases)

**Rationale:** Consistent structure makes skills discoverable and maintainable. Judges can quickly assess quality.

---

### V. Testing and Validation (MANDATORY)

**All Skills MUST Be Tested with Both Agents Before Submission**

Testing workflow:
1. **Unit test**: Run script directly: `python scripts/deploy.py --dry-run`
2. **Integration test with Claude Code**:
   ```bash
   cd skills-library
   claude "Use <skill-name> to <task>"
   # Verify: deployment succeeds, output is clear
   ```
3. **Integration test with Goose**:
   ```bash
   cd skills-library
   goose "Use <skill-name> to <task>"
   # Verify: same result as Claude Code
   ```
4. **Validation checks**: Complete all checkboxes in SKILL.md validation section
5. **Edge cases**: Test with missing prerequisites, invalid inputs, etc.

**Validation checklist template** (include in every SKILL.md):
```markdown
## Validation
- [ ] Script runs without errors
- [ ] Output shows clear success message
- [ ] Deployed resources are healthy (e.g., pods running)
- [ ] Tested with Claude Code
- [ ] Tested with Goose
- [ ] REFERENCE.md is complete
```

**Required test scenarios:**
- ✅ Happy path (everything works)
- ✅ Missing prerequisites (e.g., kubectl not installed)
- ✅ Resource already exists (idempotent behavior)
- ✅ Invalid parameters (graceful error handling)
- ✅ Network/cluster failures (clear error messages)

**Rationale:** Untested skills will fail during hackathon judging when agents try to use them.

---

### VI. Documentation Standards (MANDATORY)

**Skills Are Teaching Materials - Documentation MUST Be Excellent**

Documentation requirements:
- SKILL.md MUST be readable by non-experts (judges may not be K8s experts)
- REFERENCE.md MUST explain WHY, not just WHAT
- Scripts MUST include comments for complex logic
- Error messages MUST be actionable (tell user what to do, not just what went wrong)

**Good Error Message Example:**
```
❌ Error: kubectl not found in PATH
→ Install kubectl: https://kubernetes.io/docs/tasks/tools/
→ Or run: brew install kubectl
```

**Bad Error Message Example:**
```
Error: command not found
```

**SKILL.md Writing Guidelines:**
- Use active voice ("Deploy Kafka" not "Kafka will be deployed")
- Be specific ("Run in namespace 'learnflow'" not "Run in target namespace")
- Provide examples (show actual commands, not placeholders)
- Use checkboxes for validation (makes testing explicit)

**REFERENCE.md Writing Guidelines:**
- Explain architecture (what components are deployed, how they interact)
- Document all configuration options (script parameters, environment variables)
- Include troubleshooting for predictable failures
- Provide real-world examples beyond the basic case

**Rationale:** Documentation is 10% of evaluation. Skills are educational tools, not just scripts.

---

### VII. Security and Safety (MANDATORY)

**Skills MUST Be Safe to Run on Development and Production Clusters**

Security requirements:
- ❌ NEVER hardcode credentials, tokens, or secrets
- ✅ Use environment variables: `DB_PASSWORD`, `API_KEY`
- ✅ Use Kubernetes Secrets for sensitive data
- ✅ Document required environment variables in SKILL.md

**Safe Script Practices:**
- Validate inputs (prevent injection attacks)
- Use `--dry-run` flags where possible (let user preview changes)
- Confirm destructive operations (e.g., "Delete namespace? [y/N]")
- Set timeouts (don't hang forever waiting for pods)
- Clean up on failure (don't leave partial deployments)

**Example: Safe Secret Handling**
```python
# BAD: Hardcoded secret
db_password = "hardcoded_password_123"

# GOOD: Environment variable
import os
db_password = os.getenv("NEON_DB_PASSWORD")
if not db_password:
    print("❌ Error: NEON_DB_PASSWORD environment variable not set")
    exit(1)
```

**Rationale:** Skills will be run by judges. Insecure or destructive skills risk disqualification.

---

## Skill Development Workflow

### Creating a New Skill

1. **Plan**: Define what the skill does, why it's needed, who will use it
2. **Create structure**: `mkdir -p .claude/skills/<skill-name>/scripts`
3. **Write SKILL.md** (~100 tokens):
   - YAML frontmatter (name, description, version)
   - When to Use, Prerequisites, Instructions, Validation
4. **Implement scripts**:
   - Start with Python or Bash script that executes the operation
   - Make it executable: `chmod +x scripts/*.sh`
   - Test standalone: `python scripts/deploy.py --help`
5. **Write REFERENCE.md**:
   - Architecture overview
   - Configuration options
   - Troubleshooting guide
6. **Test with Claude Code**: `claude "Use <skill> to <task>"`
7. **Test with Goose**: `goose "Use <skill> to <task>"`
8. **Commit**: `git commit -m "feat: add <skill-name> skill with MCP code execution"`

### Updating an Existing Skill

1. **Read current SKILL.md and REFERENCE.md** (understand what it does)
2. **Test current version** (ensure you don't break working functionality)
3. **Make changes** (update scripts, SKILL.md, REFERENCE.md)
4. **Bump version** (PATCH: bug fix, MINOR: new feature, MAJOR: breaking change)
5. **Re-test with both agents** (ensure compatibility maintained)
6. **Update REFERENCE.md** (document what changed and why)
7. **Commit**: `git commit -m "fix(<skill>): resolve timeout issue in deployment script"`

---

## Required Skills for Hackathon III

### Core Infrastructure Skills (7 Required)
1. **agents-md-gen** - Generate AGENTS.md for repository context
2. **k8s-foundation** - Kubernetes operations and health checks
3. **kafka-k8s-setup** - Deploy Apache Kafka with required topics
4. **neon-postgres-setup** - Setup Neon PostgreSQL with LearnFlow schemas
5. **dapr-setup** - Install Dapr runtime on Kubernetes
6. **mcp-code-execution** - Implement MCP Code Execution pattern
7. **docusaurus-deploy** - Deploy documentation site

### Application Skills (4 Required)
8. **fastapi-dapr-agent** - Generate FastAPI microservices with Dapr + AI agents
9. **nextjs-k8s-deploy** - Deploy Next.js apps with Monaco Editor
10. **better-auth-setup** - Configure Better Auth authentication
11. **kong-gateway-setup** - Deploy Kong API Gateway

### Optional Skills (Phase 9-10)
12. **argocd-deployment** - GitOps continuous deployment
13. **prometheus-grafana-setup** - Monitoring and observability
14. **cloud-deploy** - Deploy to Azure/GCP/Oracle Cloud

---

## Governance

### Version Control
- SKILL.md versions use semantic versioning (MAJOR.MINOR.PATCH)
- Breaking changes MUST bump MAJOR version and document migration path
- Skills are immutable once published (don't modify 1.0.0, release 2.0.0 instead)

### Quality Gates
Before marking a skill as complete:
- [ ] SKILL.md is ≤150 tokens
- [ ] Scripts are executable and tested standalone
- [ ] Tested with Claude Code (works as expected)
- [ ] Tested with Goose (equivalent result)
- [ ] REFERENCE.md is comprehensive
- [ ] No hardcoded secrets or credentials
- [ ] Validation checklist in SKILL.md is complete
- [ ] Error messages are actionable

### Submission Checklist
Before submitting skills-library repository:
- [ ] All 11+ required skills are present
- [ ] Each skill passes quality gates above
- [ ] README.md explains how to use the skills
- [ ] AGENTS.md describes repository structure
- [ ] PHRs created for skill development process
- [ ] No manual application code (skills generate code, not developers)

---

**Version**: 1.0.0 | **Created**: 2026-01-27 | **Last Amended**: 2026-01-27
