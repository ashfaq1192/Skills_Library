---
name: better-auth-setup
description: Configure Better Auth authentication for Next.js
version: 1.0.0
---

# Better Auth Setup

## When to Use
- Add authentication to Next.js app
- Set up email/password and OAuth login
- Protect routes with middleware

## Prerequisites
- Next.js 14+ application
- Neon PostgreSQL connection string (see `neon-postgres-setup`)

## Instructions
1. Install: `python scripts/install_better_auth.py --project-dir <path>`
2. Configure: `python scripts/configure_auth.py --project-dir <path> --database-url <url> --providers google,github`
3. Pages: `python scripts/generate_auth_pages.py --project-dir <path>`
4. Middleware: `python scripts/add_middleware.py --project-dir <path>`

## Validation
- [ ] Better Auth packages installed
- [ ] Auth API routes created
- [ ] Login/signup pages generated
- [ ] Protected routes redirect unauthenticated users

See [REFERENCE.md](./REFERENCE.md) for OAuth setup and troubleshooting.
