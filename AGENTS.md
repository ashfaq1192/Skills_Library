# AGENTS.md

**Project**: Skills Library - Reusable Intelligence for Cloud-Native Applications
**Purpose**: Repository 1 of Hackathon III - Reusable skills that enable AI agents to build cloud-native apps autonomously
**Pattern**: MCP Code Execution (SKILL.md ~100 tokens + scripts execute operations)

## Project Structure

```
skills-library/
├── AGENTS.md                           # This file
├── README.md                           # Skill catalog and usage guide
├── .claude/skills/                     # All reusable skills
│   ├── agents-md-gen/                  # Generate AGENTS.md files
│   ├── k8s-foundation/                # Kubernetes operations and health checks
│   ├── kafka-k8s-setup/               # Deploy Kafka with Strimzi + KRaft
│   ├── neon-postgres-setup/           # Setup Neon PostgreSQL with schemas
│   ├── dapr-setup/                    # Install Dapr runtime on K8s
│   ├── mcp-code-execution/            # MCP Code Execution pattern reference
│   ├── docusaurus-deploy/             # Deploy documentation site
│   ├── fastapi-dapr-agent/            # Generate FastAPI microservices with Dapr + AI
│   ├── nextjs-k8s-deploy/            # Deploy Next.js with Monaco Editor to K8s
│   ├── better-auth-setup/            # Configure Better Auth + Neon PostgreSQL
│   ├── kong-gateway-setup/           # Deploy Kong API Gateway on K8s
│   ├── gke-fullstack-deployment/     # Deploy full-stack apps to GKE
│   ├── skill-creator-pro/            # Create new production-grade skills
│   └── skill-validator/              # Validate skills against quality criteria
├── .specify/                          # SpecKit Plus framework
│   ├── memory/constitution.md         # Skill development principles
│   ├── scripts/bash/                  # PHR/ADR creation scripts
│   └── templates/                     # Spec, plan, task templates
└── history/
    ├── prompts/                       # Prompt History Records
    └── adr/                           # Architecture Decision Records
```

## Skills Catalog

| Skill | Purpose | Category |
|-------|---------|----------|
| `agents-md-gen` | Generate AGENTS.md for repository context | Infrastructure |
| `k8s-foundation` | Kubernetes cluster operations and health checks | Infrastructure |
| `kafka-k8s-setup` | Deploy Apache Kafka with Strimzi operator and KRaft | Infrastructure |
| `neon-postgres-setup` | Setup Neon PostgreSQL with Better Auth schemas | Infrastructure |
| `dapr-setup` | Install Dapr runtime on Kubernetes | Infrastructure |
| `mcp-code-execution` | MCP Code Execution pattern implementation | Infrastructure |
| `docusaurus-deploy` | Deploy Docusaurus documentation site | Infrastructure |
| `fastapi-dapr-agent` | Generate FastAPI microservices with Dapr + OpenAI | Application |
| `nextjs-k8s-deploy` | Deploy Next.js with Monaco Editor and service proxy | Application |
| `better-auth-setup` | Configure Better Auth with role-based auth | Application |
| `kong-gateway-setup` | Deploy Kong Ingress Controller on Kubernetes | Application |
| `gke-fullstack-deployment` | Deploy full-stack apps to GKE with Docker, secrets, Kong LB | Cloud |
| `skill-creator-pro` | Create new production-grade reusable skills | Meta |
| `skill-validator` | Validate skills against 9-category quality scoring | Meta |

## Skill Structure Convention

Every skill follows this structure:

```
.claude/skills/<skill-name>/
├── SKILL.md              # ~100 tokens max (instructions only)
├── REFERENCE.md          # Deep docs (loaded on-demand)
└── scripts/
    ├── *.py              # Python scripts that execute operations
    ├── *.sh              # Bash scripts for deployment
    └── templates/        # Config/code templates
```

### MCP Code Execution Pattern

Skills use the MCP Code Execution pattern for token efficiency:

1. **SKILL.md** tells the agent WHAT to do (~100 tokens loaded)
2. **scripts/** does the actual work (0 tokens loaded - executed, not read)
3. Only the final result enters context (minimal tokens, e.g., "Done")

**Result:** 78-98% fewer tokens vs direct MCP tool integration.

## Conventions for AI Agents

### Creating Skills
- SKILL.md MUST be ~100 tokens (instructions only, no implementation)
- Heavy logic goes in `scripts/` directory
- Scripts must be executable: `chmod +x scripts/*.sh`
- Include REFERENCE.md for deep documentation
- YAML frontmatter required: name, description, version

### Testing Skills
- Every skill MUST work on both Claude Code and Goose
- Test standalone: `python scripts/deploy.py --dry-run`
- Test with Claude Code: `claude "Use <skill-name> to <task>"`
- Test with Goose: `goose "Use <skill-name> to <task>"`

### Commit Style
- `feat: add <skill-name> skill with MCP code execution`
- `fix: update <skill-name> to handle <edge-case>`
- `docs: update <skill-name> REFERENCE.md with <topic>`

## Related

- **[LearnFlow App](https://github.com/ashfaq1192/Hackathon_III_LearnFlow_App)**: Application built entirely by AI agents using these skills — [Live Demo](http://35.222.110.147)

---
*Skills in this repository follow the MCP Code Execution pattern for token-efficient AI agent automation.*
