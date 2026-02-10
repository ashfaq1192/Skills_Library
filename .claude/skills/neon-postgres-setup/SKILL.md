---
name: neon-postgres-setup
description: Setup Neon PostgreSQL with Better Auth schemas and Dapr state store
version: 2.0.0
---

# Neon PostgreSQL Setup

## When to Use
- Provision database for LearnFlow
- Initialize schemas (Better Auth auto-creates user tables, custom tables for app data)
- Store credentials in Kubernetes secrets

## Prerequisites
- Neon account and `NEON_API_KEY` environment variable
- `pip install psycopg2-binary`

## Instructions
1. Create project: `python scripts/create_project.py --name learnflow --region aws-us-east-1`
2. Get connection: `python scripts/get_connection.py --project <project-id>`
3. Init schemas: `python scripts/init_schemas.py --connection-string <conn-string>`
4. K8s secret: `python scripts/create_secret.py --namespace learnflow --connection-string <conn-string>`
5. Validate: `python scripts/list_tables.py --connection-string <conn-string>`

## Validation
- [ ] Neon project created with SSL connection
- [ ] Better Auth tables auto-created (user, session, account, verification)
- [ ] Custom tables created (exercises, submissions, learning_events, struggles)
- [ ] K8s secrets created (postgres-credentials for Dapr, frontend .env.local)

See [REFERENCE.md](./REFERENCE.md) for schema details, SSL config, and Better Auth integration.
