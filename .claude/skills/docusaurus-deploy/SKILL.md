---
name: docusaurus-deploy
description: |
  Deploy Docusaurus documentation site from project docs and OpenAPI specs. This skill
  should be used when creating documentation websites, auto-generating API docs from
  FastAPI/OpenAPI, or deploying static documentation sites to Kubernetes/cloud platforms.
---

# Docusaurus Deployment

Generate and deploy Docusaurus documentation site for LearnFlow platform.

## When to Use

- Create documentation website for project
- Auto-generate API docs from OpenAPI specs
- Deploy documentation to Kubernetes
- Set up searchable, versioned documentation

## Prerequisites

- Node.js 18+ installed:
  ```bash
  node --version  # Should be v18 or higher
  npm --version
  ```
- Docker installed (for containerization)
- `kubectl` access (for K8s deployment)
- Project documentation in markdown format (optional)
- OpenAPI specs (optional, for auto-generated API docs)

## Before Implementation

Gather context to ensure successful documentation deployment:

| Source | Gather |
|--------|--------|
| **Project** | Project name, existing docs location, API specs available |
| **User** | Documentation structure preferences, domain name for deployment |
| **Cluster** | Target namespace, ingress configuration |

## Required Clarifications

1. **Project Information**: What is your project name and purpose?
   - Use for site title and branding
   - Example: "LearnFlow" or user's application name

2. **Existing Documentation**: Do you have existing documentation?
   - If yes: Where is it located? (path to docs/ directory)
   - If no: Start with minimal template

3. **API Documentation**: Do you have OpenAPI/Swagger specs?
   - If yes: Provide path(s) to spec files
   - If no: Skip API docs generation

4. **Deployment Target**: Where should the documentation be deployed?
   - Kubernetes namespace (default: same as application)
   - Domain name (optional, for Ingress configuration)

## Instructions

### 1. Initialize Docusaurus
```bash
python scripts/init_docusaurus.py --project-name learnflow --output-dir ./docusaurus
```

### 2. Generate API Docs
```bash
python scripts/generate_api_docs.py --openapi-spec <path> --output ./docusaurus/docs/api
```

### 3. Build Documentation
```bash
python scripts/build_docs.py --docs-dir ./docusaurus
```

### 4. Deploy to K8s
```bash
python scripts/deploy_docs.py --namespace <namespace> --domain docs.learnflow.com
```

## Validation

- [ ] Docusaurus site builds successfully
- [ ] API docs generated from OpenAPI
- [ ] Site accessible at configured domain
- [ ] Search functionality works

## Troubleshooting

- **Build fails**: Check Node.js version (need 18+), verify package.json syntax
- **Plugin errors**: Ensure all plugins installed, check compatibility
- **Deployment fails**: Verify namespace exists, check Docker image built
- **Site not accessible**: Check ingress configuration, verify service running

## Official Documentation

- Docusaurus: https://docusaurus.io/docs
- OpenAPI Plugin: https://github.com/PaloAltoNetworks/docusaurus-openapi-docs
- Deployment Guide: https://docusaurus.io/docs/deployment
