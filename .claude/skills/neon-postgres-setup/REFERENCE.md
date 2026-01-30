# Neon PostgreSQL Setup - Reference Documentation

**Version**: 1.0.0
**Created**: 2026-01-27
**Purpose**: Configure Neon serverless PostgreSQL with LearnFlow application schemas

## Overview

The `neon-postgres-setup` skill provisions a Neon serverless PostgreSQL database, creates LearnFlow schemas, and stores credentials in Kubernetes Secrets. Neon provides serverless, auto-scaling PostgreSQL with branching and instant provisioning - not a self-hosted database.

### Key Features

- **Serverless PostgreSQL**: Auto-scaling compute with scale-to-zero
- **Database Branching**: Create database branches for development/testing
- **LearnFlow Schemas**: Pre-built tables for users, exercises, submissions, events, struggles
- **K8s Integration**: Credentials stored as Kubernetes Secrets
- **Cross-Agent Compatible**: Works with both Claude Code and Goose

## Architecture

```
    ┌─────────────────────┐       ┌──────────────────┐
    │   Kubernetes        │       │   Neon Cloud      │
    │   ┌──────────────┐  │       │   ┌────────────┐  │
    │   │ K8s Secret   │──┼───────┼──▶│ PostgreSQL │  │
    │   │ DATABASE_URL │  │       │   │ Serverless │  │
    │   └──────┬───────┘  │       │   │ Database   │  │
    │          │          │       │   └────────────┘  │
    │   ┌──────▼───────┐  │       │                   │
    │   │ Microservice │  │       │   Tables:         │
    │   │ (FastAPI)    │  │       │   - users          │
    │   └──────────────┘  │       │   - exercises      │
    └─────────────────────┘       │   - submissions    │
                                  │   - learning_events│
                                  │   - struggles      │
                                  └──────────────────┘
```

## Components

### 1. create_project.py

Creates a new Neon PostgreSQL project.

```bash
python scripts/create_project.py [OPTIONS]

Options:
  --name TEXT      Project name (required)
  --region TEXT    Cloud region (default: aws-us-east-1)

Environment:
  NEON_API_KEY     Neon API key (required)

Exit Codes:
  0 - Project created
  1 - Missing API key or neonctl not installed
```

**Supported Regions:**
- `aws-us-east-1` (US East - Virginia)
- `aws-us-west-2` (US West - Oregon)
- `aws-eu-west-1` (EU - Ireland)
- `aws-ap-southeast-1` (Asia Pacific - Singapore)

### 2. get_connection.py

Retrieves database connection string for a project.

```bash
python scripts/get_connection.py [OPTIONS]

Options:
  --project TEXT    Neon project ID (required)

Environment:
  NEON_API_KEY     Neon API key (required)

Exit Codes:
  0 - Connection string retrieved
  1 - Missing API key or project not found
```

**Output**: Connection string in `postgresql://user:pass@host/dbname?sslmode=require` format.

### 3. init_schemas.py

Creates LearnFlow database tables.

```bash
python scripts/init_schemas.py [OPTIONS]

Options:
  --connection-string TEXT    Neon connection string (required)

Exit Codes:
  0 - Schemas created
  1 - Connection failed or SQL error
```

**Tables Created:**

| Table | Columns | Purpose |
|-------|---------|---------|
| `users` | id, email, name, created_at | User accounts |
| `exercises` | id, title, description, difficulty, created_at | Coding challenges |
| `submissions` | id, user_id, exercise_id, code, status, created_at | Student code submissions |
| `learning_events` | id, user_id, event_type, event_data (JSONB), created_at | Activity tracking |
| `struggles` | id, user_id, exercise_id, struggle_type, detected_at | Struggle detection |

**Relationships:**
- `submissions.user_id` -> `users.id`
- `submissions.exercise_id` -> `exercises.id`
- `struggles.user_id` -> `users.id`
- `struggles.exercise_id` -> `exercises.id`
- `learning_events.user_id` -> `users.id`

### 4. create_secret.py

Creates Kubernetes Secret with database credentials.

```bash
python scripts/create_secret.py [OPTIONS]

Options:
  --namespace TEXT           Target namespace (required)
  --connection-string TEXT  Neon connection string (required)
  --secret-name TEXT        Secret name (default: postgres-credentials)

Exit Codes:
  0 - Secret created
  1 - kubectl not available or namespace error
```

**Secret Format:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-credentials
  namespace: learnflow
type: Opaque
data:
  DATABASE_URL: <base64-encoded-connection-string>
```

### 5. list_tables.py

Lists tables and row counts for validation.

```bash
python scripts/list_tables.py [OPTIONS]

Options:
  --connection-string TEXT    Database connection string (required)

Exit Codes:
  0 - Tables found and listed
  1 - No tables found or connection error
```

## Usage

### Single Command Workflow

```bash
export NEON_API_KEY="your-neon-api-key"

python scripts/create_project.py --name learnflow --region aws-us-east-1
python scripts/get_connection.py --project <project-id>
python scripts/init_schemas.py --connection-string "<connection-string>"
python scripts/create_secret.py --namespace learnflow --connection-string "<connection-string>"
python scripts/list_tables.py --connection-string "<connection-string>"
```

### With Claude Code or Goose

```bash
"Use neon-postgres-setup to create a LearnFlow database and initialize schemas"
```

## Neon-Specific Features

### Database Branching

Create branches for development/testing without copying data:

```bash
neonctl branches create --project-id <id> --name dev-branch
```

### Auto-Scaling

Neon automatically scales compute based on load:
- **Scale to zero**: No charges when inactive
- **Auto-scaling**: 0.25 to 8 compute units
- **Connection pooling**: Built-in PgBouncer

### SSL/TLS

All Neon connections use SSL by default (`sslmode=require`). No additional configuration needed.

## Integration with Dapr

Access database via Dapr state store component:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: learnflow
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-credentials
      key: DATABASE_URL
```

## Dependencies

| Dependency | Installation | Purpose |
|-----------|-------------|---------|
| psycopg2-binary | `pip install psycopg2-binary` | PostgreSQL driver |
| neonctl | `npm install -g neonctl` | Neon CLI tool |
| kubectl | System package | K8s secret management |

## Troubleshooting

### Connection Timeout

**Cause**: Firewall, VPN, or Neon project suspended
```bash
# Test direct connectivity
psql "<connection-string>" -c "SELECT 1"
# Check project status
neonctl projects list
```
**Fix**: Activate project in Neon console, check network rules

### Authentication Failed

**Cause**: Invalid API key or expired credentials
```bash
echo $NEON_API_KEY  # Verify set
neonctl projects list  # Test API key
```
**Fix**: Regenerate API key at https://console.neon.tech/app/settings/api-keys

### Schema Creation Fails

**Cause**: Connection string format error or insufficient permissions
```bash
# Verify connection string format
psql "postgresql://user:pass@host/dbname?sslmode=require" -c "\dt"
```
**Fix**: Ensure connection string includes `?sslmode=require`

### K8s Secret Not Working

**Cause**: Namespace doesn't exist or base64 encoding issues
```bash
kubectl get namespace learnflow
kubectl get secret postgres-credentials -n learnflow -o yaml
```
**Fix**: Create namespace first, verify secret data is base64 encoded

## Security Best Practices

- **Never commit** connection strings to git (use .env files)
- **Use K8s Secrets** for database credentials in production
- **Rotate passwords** quarterly via Neon console
- **Enable IP allowlists** in Neon for production
- **SSL is mandatory** - Neon enforces `sslmode=require`
- **Least privilege** - create separate database roles for each service

## References

- [Neon Documentation](https://neon.tech/docs)
- [Neon API Reference](https://api-docs.neon.tech/)
- [neonctl CLI](https://neon.tech/docs/reference/neon-cli)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Dapr PostgreSQL State Store](https://docs.dapr.io/reference/components-reference/supported-state-stores/setup-postgresql/)
