# Docusaurus Deployment - Reference Documentation

**Version**: 1.0.0
**Created**: 2026-01-27
**Purpose**: Generate and deploy Docusaurus documentation site for LearnFlow

## Overview

The `docusaurus-deploy` skill creates, builds, and deploys a Docusaurus documentation site. It initializes a Docusaurus project, generates API documentation from OpenAPI specs, builds the static site, and deploys to Kubernetes via NGINX.

### Key Features

- **Auto-Initialization**: Creates Docusaurus project with classic template
- **API Doc Generation**: Generates documentation from OpenAPI/Swagger specs
- **Static Build**: Optimized production build
- **K8s Deployment**: Deploys via NGINX on Kubernetes
- **TypeScript**: Uses TypeScript configuration
- **Cross-Agent Compatible**: Works with both Claude Code and Goose

## Architecture

```
Documentation Pipeline:
  OpenAPI Specs ─┐
                 ├──▶ Docusaurus ──▶ Static Build ──▶ K8s NGINX
  Markdown Docs ─┘

Kubernetes Layout:
  ┌─────────────────────────────────────────┐
  │  Namespace: learnflow                    │
  │                                          │
  │  ┌──────────────┐    ┌───────────────┐  │
  │  │ ConfigMap    │    │ Deployment    │  │
  │  │ nginx.conf   │───▶│ nginx:alpine  │  │
  │  └──────────────┘    │ 2 replicas    │  │
  │                      └───────┬───────┘  │
  │                      ┌───────▼───────┐  │
  │                      │ Service       │  │
  │                      │ ClusterIP     │  │
  │                      │ :80           │  │
  │                      └───────────────┘  │
  └─────────────────────────────────────────┘
```

## Components

### 1. init_docusaurus.py

Initializes a new Docusaurus project.

```bash
python scripts/init_docusaurus.py [OPTIONS]

Options:
  --project-name TEXT    Project name (required)
  --output-dir TEXT      Output directory (required)

Exit Codes:
  0 - Project initialized
  1 - Node.js version < 18, npx failed
```

**What It Does:**
1. Verifies Node.js 18+ is installed
2. Creates output directory
3. Runs `npx create-docusaurus@latest` with classic template and TypeScript
4. Reports success and next steps

### 2. generate_api_docs.py

Generates API documentation from OpenAPI specifications.

```bash
python scripts/generate_api_docs.py [OPTIONS]

Options:
  --openapi-spec TEXT    Path to OpenAPI spec (JSON or YAML) (required)
  --output TEXT          Output directory for docs (required)

Exit Codes:
  0 - Docs generated
  1 - Spec file not found, invalid format
```

**What It Does:**
1. Validates OpenAPI spec file exists
2. Loads and parses JSON or YAML spec
3. Extracts API metadata (title, version)
4. Installs Docusaurus OpenAPI plugin (if needed)
5. Generates Markdown with endpoint listings
6. Writes `api-reference.md` to output directory

**Output Format:**
```markdown
# API Reference: Service Name

**Version:** 1.0.0

## Endpoints

### GET /api/concepts
Retrieve Python concepts

### POST /api/exercises
Submit code exercise
...
```

### 3. build_docs.py

Builds the Docusaurus site for production.

```bash
python scripts/build_docs.py [OPTIONS]

Options:
  --docs-dir TEXT    Docusaurus project directory (required)

Exit Codes:
  0 - Build successful
  1 - Missing package.json, build failed
```

**What It Does:**
1. Validates docs directory and package.json
2. Installs dependencies if `node_modules` missing
3. Runs `npm run build`
4. Verifies `build/` directory created
5. Reports file count

### 4. deploy_docs.py

Deploys built documentation to Kubernetes.

```bash
python scripts/deploy_docs.py [OPTIONS]

Options:
  --namespace TEXT    Target namespace (required)
  --docs-dir TEXT    Docusaurus project directory (required)
  --domain TEXT      Domain for Ingress (optional)

Exit Codes:
  0 - Deployed successfully
  1 - Build directory missing, kubectl error
```

**What It Does:**
1. Validates `build/` directory exists
2. Creates namespace if needed
3. Deploys NGINX ConfigMap (SPA routing)
4. Creates Deployment (2 replicas of nginx:alpine)
5. Creates Service (ClusterIP)
6. Reports access instructions

**NGINX Configuration:**
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**Note**: Build files need to be copied to pods after deployment:
```bash
kubectl cp build/ <pod>:/usr/share/nginx/html/ -n learnflow
```

## Usage

### Full Pipeline

```bash
cd /path/to/learnflow-app

# 1. Initialize (if no docs directory exists)
python .claude/skills/docusaurus-deploy/scripts/init_docusaurus.py \
  --project-name learnflow \
  --output-dir ./docs

# 2. Generate API docs (optional, if OpenAPI specs exist)
python .claude/skills/docusaurus-deploy/scripts/generate_api_docs.py \
  --openapi-spec ./src/services/concepts-service/openapi.json \
  --output ./docs/docs/api

# 3. Build
python .claude/skills/docusaurus-deploy/scripts/build_docs.py \
  --docs-dir ./docs

# 4. Deploy to K8s
python .claude/skills/docusaurus-deploy/scripts/deploy_docs.py \
  --namespace learnflow \
  --docs-dir ./docs
```

### With Claude Code or Goose

```bash
"Use docusaurus-deploy to build and deploy LearnFlow documentation"
```

### Accessing Documentation

```bash
# Port-forward
kubectl port-forward -n learnflow svc/learnflow-docs 8080:80

# Open: http://localhost:8080
```

## LearnFlow Documentation Structure

```
docs/
├── docs/
│   ├── intro.md                    # Welcome page
│   ├── getting-started/
│   │   ├── installation.md         # Setup guide
│   │   └── quickstart.md           # Quick start
│   ├── architecture/
│   │   ├── overview.md             # System architecture
│   │   ├── services.md             # Microservice details
│   │   └── events.md               # Event-driven patterns
│   ├── api/
│   │   ├── triage.md               # Triage Service API
│   │   ├── concepts.md             # Concepts Service API
│   │   ├── exercises.md            # Exercise Service API
│   │   └── execution.md            # Code Execution API
│   └── development/
│       ├── contributing.md         # Contribution guide
│       └── skills.md               # Skills development
├── src/                            # Custom components
├── static/                         # Static assets
├── docusaurus.config.ts            # Site configuration
├── sidebars.ts                     # Sidebar navigation
└── package.json
```

## Configuration

### docusaurus.config.ts

```typescript
const config: Config = {
  title: 'LearnFlow',
  tagline: 'AI-Powered Python Learning Platform',
  url: 'https://docs.learnflow.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'learnflow',
  projectName: 'learnflow-docs',
  presets: [
    ['classic', {
      docs: { sidebarPath: './sidebars.ts' },
      theme: { customCss: './src/css/custom.css' },
    }],
  ],
};
```

### Sidebar Configuration

```typescript
const sidebars: SidebarsConfig = {
  docs: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: ['getting-started/installation', 'getting-started/quickstart'],
    },
    {
      type: 'category',
      label: 'Architecture',
      items: ['architecture/overview', 'architecture/services', 'architecture/events'],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: ['api/triage', 'api/concepts', 'api/exercises', 'api/execution'],
    },
  ],
};
```

## Troubleshooting

### Build Fails

```bash
# Check Node version
node --version  # Need v18+

# Clear cache
rm -rf node_modules .docusaurus build
npm install
npm run build

# Check for broken links
npm run build 2>&1 | grep "broken"
```

### Plugin Errors

```bash
# Verify all plugins installed
npm ls docusaurus-plugin-openapi-docs

# Reinstall if needed
npm install docusaurus-plugin-openapi-docs docusaurus-theme-openapi-docs
```

### Deployment Not Accessible

```bash
# Check pods running
kubectl get pods -n learnflow -l app=learnflow-docs

# Check service
kubectl get svc -n learnflow learnflow-docs

# Check logs
kubectl logs -n learnflow -l app=learnflow-docs
```

### Static Files Not Loading

```bash
# Copy build files to running pods
for pod in $(kubectl get pods -n learnflow -l app=learnflow-docs -o jsonpath='{.items[*].metadata.name}'); do
  kubectl cp build/ $pod:/usr/share/nginx/html/ -n learnflow
done
```

## Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| Node.js | 18+ | Build runtime |
| npm | 9+ | Package manager |
| Docusaurus | 3.x | Documentation framework |
| nginx:alpine | Latest | Static file serving |
| kubectl | 1.24+ | Kubernetes deployment |

## References

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [Docusaurus OpenAPI Plugin](https://github.com/PaloAltoNetworks/docusaurus-openapi-docs)
- [Docusaurus Deployment Guide](https://docusaurus.io/docs/deployment)
- [NGINX Configuration](https://nginx.org/en/docs/)
