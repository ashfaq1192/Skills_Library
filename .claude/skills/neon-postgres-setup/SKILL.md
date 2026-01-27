---
name: neon-postgres-setup
description: |
  Setup Neon PostgreSQL serverless database with LearnFlow schemas. This skill should
  be used when provisioning cloud PostgreSQL database, creating application schemas,
  or configuring database access for microservices. Uses Neon's serverless PostgreSQL
  (not self-hosted) with automatic scaling and branching capabilities.
---

# Neon PostgreSQL Setup

Configure Neon serverless PostgreSQL database with LearnFlow application schemas.

## When to Use

- Provision Neon PostgreSQL database for application
- Create database schemas and tables for LearnFlow
- Configure database access credentials
- Set up connection pooling for microservices

## Prerequisites

- Python 3.9+ with packages:
  ```bash
  pip install psycopg2-binary
  npm install -g neonctl
  ```
- Neon account and API key (get from https://neon.tech)
- Environment variable: `NEON_API_KEY`
- `kubectl` access for K8s secret creation

## Before Implementation

Gather context to ensure successful setup:

| Source | Gather |
|--------|--------|
| **User** | Neon account status, preferred region, target namespace |
| **Project** | Application name, database schemas needed |
| **Environment** | Kubernetes cluster access for secrets |

## Required Clarifications

1. **Neon Account**: Do you have a Neon account and API key?
   - If no: Guide user to create account at https://neon.tech
   - If yes: What region do you prefer? (aws-us-east-1, aws-us-west-2, aws-eu-west-1)

2. **Database Purpose**: What is this database for?
   - For LearnFlow: Use default schemas (users, exercises, submissions, learning_events, struggles)
   - For custom application: Ask user to provide schema SQL file or table definitions

3. **Kubernetes Integration**: What namespace should store the database secret?
   - Default: Use application namespace
   - Verify: `kubectl get namespace <namespace>` before proceeding

## Instructions

### 1. Create Neon Project
```bash
python scripts/create_project.py --name learnflow --region aws-us-east-1
```
Creates new Neon project with database instance.

### 2. Get Connection String
```bash
python scripts/get_connection.py --project <project-id>
```
Retrieves connection string for application use.

### 3. Initialize Schemas
```bash
python scripts/init_schemas.py --connection-string <conn-string>
```
Creates LearnFlow tables: users, exercises, submissions, learning_events, struggles.

### 4. Create K8s Secret
```bash
python scripts/create_secret.py --namespace <namespace> --connection-string <conn-string>
```
Stores database credentials in Kubernetes Secret for pods.

## Validation

- [ ] Neon project created: Check Neon console
- [ ] Connection string works: `psql <connection-string> -c '\l'`
- [ ] Tables exist: Use `scripts/list_tables.py`
- [ ] K8s secret created: `kubectl get secret -n <namespace>`

## Troubleshooting

- **Connection timeout**: Check firewall rules, verify Neon project is active
- **Authentication failed**: Verify `NEON_API_KEY` is correct, regenerate if needed
- **Schema creation fails**: Check connection string format, ensure database exists
- **K8s secret not found**: Verify namespace exists, check kubectl access

## Security Best Practices

- Never commit connection strings to git
- Use K8s Secrets for database credentials
- Rotate database passwords quarterly
- Use connection pooling (pgbouncer) for production
- Enable SSL connections (included in Neon by default)

## Official Documentation

- Neon Docs: https://neon.tech/docs
- Neon API Reference: https://api-docs.neon.tech/
- PostgreSQL Best Practices: https://wiki.postgresql.org/wiki/Don%27t_Do_This
