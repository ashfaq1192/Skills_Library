# Better Auth Setup - Reference Documentation

**Version**: 1.0.0
**Created**: 2026-01-27
**Purpose**: Configure Better Auth authentication in Next.js applications

## Overview

The `better-auth-setup` skill integrates Better Auth into Next.js applications, providing email/password authentication, OAuth providers (Google, GitHub), JWT sessions, and route protection middleware. Better Auth is a modern, framework-agnostic authentication library that replaces NextAuth/Auth.js with a simpler API.

### Key Features

- **Email/Password Auth**: Registration and login with bcrypt hashing
- **OAuth Providers**: Google and GitHub OAuth integration
- **JWT Sessions**: Stateless token-based sessions
- **Route Protection**: Middleware for authenticated/public routes
- **Login/Signup Pages**: Pre-built React pages with Tailwind CSS
- **Database Integration**: Works with Neon PostgreSQL via `neon-postgres-setup`
- **Cross-Agent Compatible**: Works with both Claude Code and Goose

## Architecture

```
┌───────────────────────────────────────────────┐
│  Next.js Application                          │
│                                               │
│  ┌──────────────┐    ┌─────────────────────┐  │
│  │ middleware.ts │    │ lib/auth.ts         │  │
│  │ Route guard   │    │ Better Auth config  │  │
│  └──────┬───────┘    └──────────┬──────────┘  │
│         │                       │             │
│  ┌──────▼───────┐    ┌─────────▼──────────┐  │
│  │ Pages        │    │ API Route          │  │
│  │ /login       │    │ /api/auth/[...all] │  │
│  │ /signup      │    │ Handles all auth   │  │
│  └──────────────┘    └──────────┬─────────┘  │
│                                 │             │
│  ┌──────────────┐    ┌─────────▼──────────┐  │
│  │ auth-client  │    │ OAuth Providers    │  │
│  │ Client SDK   │    │ Google, GitHub     │  │
│  └──────────────┘    └──────────┬─────────┘  │
│                                 │             │
└─────────────────────────────────┼─────────────┘
                                  │
                         ┌────────▼────────┐
                         │ Neon PostgreSQL  │
                         │ User storage     │
                         └─────────────────┘
```

## Components

### 1. install_better_auth.py

Installs required npm packages.

```bash
python scripts/install_better_auth.py [OPTIONS]

Options:
  --project-dir TEXT    Next.js project directory (required)

Exit Codes:
  0 - Packages installed
  1 - Missing package.json, npm error
```

**Packages Installed:**
| Package | Purpose |
|---------|---------|
| `better-auth` | Core authentication library |
| `@better-auth/react` | React hooks and components |
| `jose` | JWT token handling |
| `bcryptjs` | Password hashing |

### 2. configure_auth.py

Sets up Better Auth configuration with database and providers.

```bash
python scripts/configure_auth.py [OPTIONS]

Options:
  --project-dir TEXT     Next.js project directory (required)
  --database-url TEXT    Neon connection string (default: placeholder)
  --providers TEXT       Comma-separated OAuth providers (optional, e.g., "google,github")

Exit Codes:
  0 - Configuration generated
  1 - Project directory invalid
```

**Generated Files:**

| File | Purpose |
|------|---------|
| `lib/auth.ts` | Better Auth configuration with database and providers |
| `app/api/auth/[...all]/route.ts` | API catch-all route for auth endpoints |
| `.env.local.template` | Environment variable template |

**auth.ts Template:**
```typescript
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: {
    provider: "pg",
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
  },
});
```

### 3. generate_auth_pages.py

Creates login and signup pages.

```bash
python scripts/generate_auth_pages.py [OPTIONS]

Options:
  --project-dir TEXT    Next.js project directory (required)

Exit Codes:
  0 - Pages created
  1 - Project directory invalid
```

**Generated Files:**

| File | Route | Purpose |
|------|-------|---------|
| `lib/auth-client.ts` | N/A | Client-side auth utilities |
| `app/login/page.tsx` | `/login` | Login form (email/password) |
| `app/signup/page.tsx` | `/signup` | Registration form (name/email/password) |

**Page Features:**
- React hooks (useState, useRouter)
- Form validation with error messages
- Redirect to `/dashboard` on success
- Cross-links between login and signup
- Tailwind CSS styling

### 4. add_middleware.py

Adds route protection middleware.

```bash
python scripts/add_middleware.py [OPTIONS]

Options:
  --project-dir TEXT    Next.js project directory (required)

Exit Codes:
  0 - Middleware created
  1 - Project directory invalid
```

**Route Configuration:**

| Route Pattern | Behavior |
|--------------|----------|
| `/dashboard/*` | Requires authentication |
| `/profile/*` | Requires authentication |
| `/settings/*` | Requires authentication |
| `/login` | Redirects to `/dashboard` if authenticated |
| `/signup` | Redirects to `/dashboard` if authenticated |
| All others | Public access |

**Middleware Logic:**
1. Checks for session cookie (`better-auth.session_token`)
2. Unauthenticated users on protected routes -> redirect to `/login`
3. Authenticated users on auth routes -> redirect to `/dashboard`

## Usage

### Full Setup Pipeline

```bash
cd /path/to/learnflow-app/src/frontend

# 1. Install packages
python .claude/skills/better-auth-setup/scripts/install_better_auth.py \
  --project-dir .

# 2. Configure auth (with Neon database)
python .claude/skills/better-auth-setup/scripts/configure_auth.py \
  --project-dir . \
  --database-url "postgresql://user:pass@host/db?sslmode=require" \
  --providers google,github

# 3. Generate login/signup pages
python .claude/skills/better-auth-setup/scripts/generate_auth_pages.py \
  --project-dir .

# 4. Add route protection
python .claude/skills/better-auth-setup/scripts/add_middleware.py \
  --project-dir .
```

### With Claude Code or Goose

```bash
"Use better-auth-setup to add authentication to the LearnFlow frontend"
```

## Environment Variables

```bash
# .env.local
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require

# OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Auth
BETTER_AUTH_SECRET=your-random-secret-key
BETTER_AUTH_URL=http://localhost:3000
```

## OAuth Provider Setup

### Google

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID
3. Add authorized redirect: `http://localhost:3000/api/auth/callback/google`
4. Copy Client ID and Secret to `.env.local`

### GitHub

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create new OAuth App
3. Set callback URL: `http://localhost:3000/api/auth/callback/github`
4. Copy Client ID and Secret to `.env.local`

## Integration with Neon PostgreSQL

Better Auth stores user data in the Neon database created by `neon-postgres-setup`:

```bash
# 1. First set up Neon database
"Use neon-postgres-setup to create the LearnFlow database"

# 2. Then configure auth with the connection string
"Use better-auth-setup to add auth using the Neon connection string"
```

Better Auth auto-creates its own tables (user, session, account, verification) on first run.

## Troubleshooting

### OAuth Redirect Fails

```bash
# Verify redirect URLs match exactly
# Google: http://localhost:3000/api/auth/callback/google
# GitHub: http://localhost:3000/api/auth/callback/github

# Check BETTER_AUTH_URL matches your app URL
echo $BETTER_AUTH_URL
```

### Database Connection Error

```bash
# Test connection directly
psql $DATABASE_URL -c "SELECT 1"

# Verify .env.local has correct DATABASE_URL
cat .env.local | grep DATABASE_URL
```

### TypeScript Errors

```bash
# Install type definitions
npm install -D @types/node @types/react

# Verify tsconfig.json includes lib directory
```

### Session Not Persisting

```bash
# Check cookie settings in browser DevTools
# Verify BETTER_AUTH_SECRET is set
# Check middleware.ts isn't blocking auth API routes
```

### Middleware Redirect Loop

```bash
# Ensure /api/auth/* routes are NOT in protected paths
# Check middleware.ts matcher configuration
# Verify auth pages are in the public routes list
```

## Security Considerations

- **Never commit** `.env.local` to git
- **Use strong secrets**: Generate with `openssl rand -base64 32`
- **HTTPS in production**: Set secure cookie flags
- **Rate limiting**: Add rate limiting to auth endpoints via Kong
- **Password requirements**: Configure minimum password length in auth config
- **Session expiry**: Configure appropriate session duration

## Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| better-auth | Latest | Core auth library |
| @better-auth/react | Latest | React integration |
| jose | Latest | JWT handling |
| bcryptjs | Latest | Password hashing |
| Next.js | 14+ | Framework |
| Neon PostgreSQL | N/A | User data storage |

## References

- [Better Auth Documentation](https://www.better-auth.com/docs)
- [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Setup](https://docs.github.com/en/apps/oauth-apps)
