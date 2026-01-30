---
name: docusaurus-deploy
description: Deploy Docusaurus documentation site
version: 1.0.0
---

# Docusaurus Deployment

## When to Use
- Create documentation website
- Auto-generate API docs from OpenAPI specs
- Deploy docs to Kubernetes

## Prerequisites
- Node.js 18+ (`node --version`)
- Docker installed (for K8s deployment)

## Instructions
1. Init: `python scripts/init_docusaurus.py --project-name learnflow --output-dir ./docs`
2. API docs: `python scripts/generate_api_docs.py --openapi-spec <path> --output ./docs/docs/api`
3. Build: `python scripts/build_docs.py --docs-dir ./docs`
4. Deploy: `python scripts/deploy_docs.py --namespace learnflow --docs-dir ./docs`

## Validation
- [ ] Docusaurus site builds
- [ ] API docs generated
- [ ] Site accessible via port-forward

See [REFERENCE.md](./REFERENCE.md) for configuration and structure.
