---
name: neon-postgres-setup
description: Setup Neon PostgreSQL with LearnFlow schemas
version: 1.0.0
---

# Neon PostgreSQL Setup

## When to Use
- Provision database for LearnFlow
- Create application schemas
- Store credentials in Kubernetes

## Prerequisites
- `NEON_API_KEY` environment variable set
- `pip install psycopg2-binary` and `npm install -g neonctl`

## Instructions
1. Create project: `python scripts/create_project.py --name learnflow --region aws-us-east-1`
2. Get connection: `python scripts/get_connection.py --project <project-id>`
3. Init schemas: `python scripts/init_schemas.py --connection-string <conn-string>`
4. K8s secret: `python scripts/create_secret.py --namespace learnflow --connection-string <conn-string>`
5. Validate: `python scripts/list_tables.py --connection-string <conn-string>`

## Validation
- [ ] Neon project created
- [ ] Tables exist (users, exercises, submissions, learning_events, struggles)
- [ ] K8s secret created

See [REFERENCE.md](./REFERENCE.md) for schema details and troubleshooting.
