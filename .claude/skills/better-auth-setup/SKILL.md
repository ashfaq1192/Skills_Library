---
name: better-auth-setup
description: |
  Configure Better Auth authentication in Next.js applications. This skill should be
  used when adding authentication, implementing login/signup flows, or integrating
  OAuth providers (Google, GitHub) with Better Auth library.
---

# Better Auth Setup

Configure Better Auth authentication for Next.js applications.

## When to Use

- Add authentication to Next.js app
- Set up email/password login
- Configure OAuth providers (Google, GitHub)
- Implement JWT-based sessions

## Prerequisites

- Next.js 14+ application: `npx create-next-app@latest`
- Database connection (PostgreSQL via Neon): See `neon-postgres-setup` skill
- OAuth credentials (if using providers): Google Cloud Console, GitHub OAuth Apps
- Node.js 18+ and npm/yarn installed

## Before Implementation

Gather context to ensure successful authentication setup:

| Source | Gather |
|--------|--------|
| **Next.js Project** | Project directory path, app router vs pages router, TypeScript config |
| **Database** | Neon connection string, database name, user credentials |
| **OAuth Providers** | Client IDs/secrets for Google/GitHub, redirect URLs configured |
| **Environment** | Development vs production, domain/URL for callbacks |

## Required Clarifications

1. **Authentication Methods**: Which authentication methods are needed?
   - Email/password only
   - OAuth providers (Google, GitHub, both)
   - Magic link authentication

2. **Session Strategy**: How should sessions be managed?
   - JWT tokens (stateless)
   - Database sessions (stateful)
   - Session duration requirements (e.g., 7 days, 30 days)

3. **Protected Routes**: Which routes require authentication?
   - List specific paths (e.g., /dashboard, /profile, /api/*)
   - Public vs authenticated route patterns

4. **User Schema**: What user data should be stored?
   - Basic (email, name, avatar)
   - Extended (role, preferences, metadata)
   - Custom fields for application

## Instructions

### 1. Install Better Auth
```bash
python scripts/install_better_auth.py --project-dir <path>
```

### 2. Configure Auth
```bash
python scripts/configure_auth.py \
  --project-dir <path> \
  --database-url <neon-connection-string> \
  --providers google,github
```

### 3. Generate Auth Pages
```bash
python scripts/generate_auth_pages.py --project-dir <path>
```

Creates: `/app/login`, `/app/signup`, `/app/auth/callback`

### 4. Add Middleware
```bash
python scripts/add_middleware.py --project-dir <path>
```

Protects routes requiring authentication.

## Validation

- [ ] Better Auth installed
- [ ] Auth API routes created
- [ ] Login page accessible
- [ ] OAuth flow works
- [ ] Protected routes redirect to login

## Troubleshooting

| Issue | Solution |
|-------|----------|
| OAuth redirect fails | Verify redirect URLs match in provider console and config |
| Database connection error | Check Neon connection string format and credentials |
| TypeScript errors | Ensure `@auth/core` types installed: `npm i -D @types/node` |
| Session not persisting | Check middleware configuration and cookie settings |

## Official Documentation

- Better Auth: https://www.better-auth.com/docs
- Google OAuth: https://developers.google.com/identity/protocols/oauth2
- GitHub OAuth: https://docs.github.com/en/apps/oauth-apps
