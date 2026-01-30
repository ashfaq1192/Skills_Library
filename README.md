# Skills Library - Hackathon III

**Reusable, Autonomous Skills for Building Cloud-Native Applications with AI Agents**

This repository contains production-ready Skills that teach AI agents (Claude Code, Goose, and Codex) how to build cloud-native, event-driven applications using the **MCP Code Execution pattern**.

## 🎯 What This Repository Does

This is **Repository 1** of two deliverables for Hackathon III: Reusable Intelligence and Cloud-Native Mastery.

**Mission:** Provide Skills that enable any AI agent to deploy production-ready infrastructure with a single prompt.

**Success Criteria:** Clone this repo → Run one prompt → Complete deployment works.

## 📦 Available Skills

### Core Infrastructure Skills (Required)

| Skill | Purpose | Status |
|-------|---------|--------|
| `agents-md-gen` | Generate AGENTS.md for repository context | ✅ Complete |
| `k8s-foundation` | Kubernetes operations and health checks | ✅ Complete |
| `kafka-k8s-setup` | Deploy Apache Kafka with required topics | ✅ Complete |
| `neon-postgres-setup` | Setup Neon PostgreSQL with schemas | ✅ Complete |
| `dapr-setup` | Install Dapr runtime on Kubernetes | ✅ Complete |
| `mcp-code-execution` | Implement MCP Code Execution pattern | ✅ Complete |
| `docusaurus-deploy` | Deploy documentation site | ✅ Complete |

### Application Skills (Required)

| Skill | Purpose | Status |
|-------|---------|--------|
| `fastapi-dapr-agent` | Generate FastAPI microservices with Dapr + AI | ✅ Complete |
| `nextjs-k8s-deploy` | Deploy Next.js apps with Monaco Editor | ✅ Complete |
| `better-auth-setup` | Configure Better Auth authentication | ✅ Complete |
| `kong-gateway-setup` | Deploy Kong API Gateway | ✅ Complete |

### Optional Skills (Bonus)

| Skill | Purpose | Status |
|-------|---------|--------|
| `argocd-deployment` | GitOps continuous deployment | 📋 Planned |
| `prometheus-grafana-setup` | Monitoring and observability | 📋 Planned |
| `cloud-deploy` | Deploy to Azure/GCP/Oracle Cloud | 📋 Planned |

## 🚀 Quick Start

### Prerequisites

- **Kubernetes cluster** running (Minikube for development)
- **kubectl** configured and working
- **Python 3.9+** installed
- **Claude Code** or **Goose** AI agent installed

### Using Skills with Claude Code

```bash
# Clone this repository
git clone <your-repo-url> skills-library
cd skills-library

# Use a skill (example: deploy Kafka)
claude "Use kafka-k8s-setup to deploy Kafka to namespace 'learnflow'"
```

### Using Skills with Goose

```bash
# Same skills, same commands
goose "Use kafka-k8s-setup to deploy Kafka to namespace 'learnflow'"
```

**Key Feature:** All skills work identically on both Claude Code and Goose (cross-agent compatibility).

## 📚 How Skills Work

### The MCP Code Execution Pattern

Instead of loading MCP tools into agent context (which consumes 41% of tokens), we use:

1. **SKILL.md** (~100 tokens) - Instructions for the agent (WHAT to do)
2. **scripts/** (0 tokens loaded) - Python/Bash scripts that execute operations (HOW to do it)
3. **REFERENCE.md** (loaded on-demand) - Deep documentation and troubleshooting

**Example: kafka-k8s-setup skill**

```
.claude/skills/kafka-k8s-setup/
├── SKILL.md                 # ~100 tokens: "Run python scripts/deploy_kafka.py"
├── REFERENCE.md             # Deep docs: architecture, configuration, troubleshooting
└── scripts/
    ├── deploy_kafka.py      # Does the actual work (kubectl, helm commands)
    └── templates/
        └── kafka-values.yaml # Helm values template
```

When agent runs the skill:
1. Reads SKILL.md (~100 tokens)
2. Executes `python scripts/deploy_kafka.py`
3. Script filters data and returns: "✓ Kafka ready: 3/3 brokers running" (~10 tokens)

**Result:** 78.5% fewer tokens used compared to direct MCP integration.

## 🛠️ Creating a New Skill

Follow our systematic workflow:

### 1. Plan Your Skill

```bash
# Create a spec for the skill
claude "Create a spec for <skill-name> skill that <description>"
```

### 2. Create Skill Structure

```bash
mkdir -p .claude/skills/<skill-name>/scripts
cd .claude/skills/<skill-name>
```

### 3. Write SKILL.md (~100 tokens)

```markdown
---
name: skill-name
description: One-line description
version: 1.0.0
---

# Skill Name

Brief overview (1-2 sentences).

## When to Use
- Use case 1
- Use case 2

## Prerequisites
- Requirement 1

## Instructions
1. Run: `python scripts/command.py --arg value`
2. Verify: Check output shows "✓ Success"

## Validation
- [ ] Check 1
- [ ] Tested with Claude Code
- [ ] Tested with Goose

## See Also
- REFERENCE.md for deep documentation
```

### 4. Implement Scripts

```bash
# Create Python script that does the work
cat > scripts/deploy.py <<'EOF'
#!/usr/bin/env python3
import subprocess
import sys

def deploy():
    # Execute kubectl/helm/psql commands
    result = subprocess.run(["kubectl", "apply", "-f", "manifest.yaml"],
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Deployment successful")
        return 0
    else:
        print(f"❌ Error: {result.stderr}")
        return 1

if __name__ == "__main__":
    sys.exit(deploy())
EOF

chmod +x scripts/deploy.py
```

### 5. Write REFERENCE.md

Include:
- Architecture overview
- Configuration options
- Troubleshooting guide
- Advanced examples

### 6. Test with Both Agents

```bash
# Test with Claude Code
claude "Use <skill-name> to <task>"

# Test with Goose
goose "Use <skill-name> to <task>"
```

### 7. Commit

```bash
git add .claude/skills/<skill-name>
git commit -m "feat: add <skill-name> skill with MCP code execution"
```

## 📖 Documentation

- **Constitution:** `.specify/memory/constitution.md` - Skill development principles
- **Templates:** `.specify/templates/` - Spec, plan, and task templates
- **PHRs:** `history/prompts/` - Prompt History Records (development process)
- **ADRs:** `history/adr/` - Architecture Decision Records

## 🧪 Testing Standards

Every skill MUST pass these tests before submission:

- [ ] **Unit test:** Script runs standalone: `python scripts/deploy.py --dry-run`
- [ ] **Integration test (Claude Code):** `claude "Use <skill> to <task>"`
- [ ] **Integration test (Goose):** `goose "Use <skill> to <task>"` (same result)
- [ ] **Validation:** All checkboxes in SKILL.md validation section complete
- [ ] **Token count:** SKILL.md ≤150 tokens
- [ ] **Security:** No hardcoded credentials or secrets

## 🏆 Evaluation Criteria

These skills will be judged on:

| Criterion | Weight | What We Optimize For |
|-----------|--------|---------------------|
| Skills Autonomy | 15% | Single prompt → complete deployment |
| Token Efficiency | 10% | SKILL.md ~100 tokens, scripts do heavy lifting |
| Cross-Agent Compatibility | 5% | Works on Claude Code AND Goose |
| Architecture | 20% | Correct Dapr, Kafka, stateless patterns |
| MCP Integration | 10% | Code execution pattern implemented |
| Documentation | 10% | Comprehensive REFERENCE.md and examples |
| Spec-Kit Plus Usage | 15% | High-level specs translate to tasks |
| Application Completion | 15% | LearnFlow app built entirely via skills |

## 🔧 Project Structure

```
skills-library/
├── README.md                    # This file
├── AGENTS.md                    # Repository context for AI agents
├── .claude/skills/              # Skills directory (works for Claude + Goose)
│   ├── agents-md-gen/           # ✅ Complete
│   │   ├── SKILL.md
│   │   ├── REFERENCE.md
│   │   └── scripts/
│   ├── kafka-k8s-setup/         # 📋 Planned
│   └── ...                      # Other skills
├── .specify/                    # SpecKit Plus (planning framework)
│   ├── memory/constitution.md   # Skill development principles
│   ├── scripts/bash/            # PHR/ADR creation scripts
│   └── templates/               # Spec, plan, task templates
└── history/
    ├── prompts/                 # Prompt History Records
    │   ├── constitution/        # Constitution-related PHRs
    │   └── general/             # General development PHRs
    └── adr/                     # Architecture Decision Records
```

## 🤝 Contributing

### Development Workflow

1. **Read the constitution:** `.specify/memory/constitution.md`
2. **Create a spec:** Use SpecKit Plus templates
3. **Implement skill:** Follow structure guidelines
4. **Test thoroughly:** Both Claude Code and Goose
5. **Document well:** SKILL.md + REFERENCE.md
6. **Commit with PHR:** Track your development process

### Quality Standards

- SKILL.md MUST be ≤150 tokens
- Scripts MUST be executable: `chmod +x scripts/*.sh`
- Error messages MUST be actionable
- No hardcoded secrets (use environment variables)
- Cross-agent compatibility verified

## 📝 Related Repositories

- **LearnFlow Application** (Repository 2): Application built ENTIRELY by AI agents using these skills
- **Hackathon III Requirements**: Official requirements and evaluation criteria

## 📞 Support

- **Issues:** Create an issue in this repository
- **Documentation:** See `.specify/memory/constitution.md`
- **Examples:** Check `history/prompts/` for development examples

## 📄 License

See LICENSE file in this repository.

---

**Version:** 1.0.0
**Last Updated:** 2026-01-27
**Hackathon:** Reusable Intelligence and Cloud-Native Mastery (Hackathon III)
**Submission:** https://forms.gle/Mrhf9XZsuXN4rWJf7
