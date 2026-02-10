---
name: better-auth-setup
description: Configure Better Auth with role-based authentication for Next.js + Neon PostgreSQL
version: 2.0.0
---

# Better Auth Setup

## When to Use
- Add role-based authentication (student/teacher) to Next.js app
- Set up email/password login with Neon PostgreSQL
- Protect routes with session-based middleware

## Prerequisites
- Next.js 14+ application
- Neon PostgreSQL connection string (see `neon-postgres-setup`)

## Instructions
1. Install: `python scripts/install_better_auth.py --project-dir <path>`
2. Configure: `python scripts/configure_auth.py --project-dir <path> --database-url <neon-url>`
3. Pages: `python scripts/generate_auth_pages.py --project-dir <path>`
4. Middleware: `python scripts/add_middleware.py --project-dir <path>`

## Validation
- [ ] Better Auth packages installed (better-auth, pg)
- [ ] Auth config with role field and Neon SSL handling
- [ ] Login/signup pages with role selection (student/teacher)
- [ ] Role-based redirect after login
- [ ] `.env.local` has DATABASE_URL, AUTH_SECRET

See [REFERENCE.md](./REFERENCE.md) for role-based patterns and Neon SSL troubleshooting.
