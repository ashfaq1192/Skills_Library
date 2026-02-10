#!/usr/bin/env python3
"""Configure Better Auth with Neon PostgreSQL, role field, and SSL handling.

Matches actual LearnFlow production patterns:
- Neon PostgreSQL with SSL (sslmode stripped from URL, configured via Pool options)
- Custom role field (student/teacher) on user model
- Trusted origins for CORS
- Better Auth React client for session management
"""
import sys, argparse
from pathlib import Path

# Auth config matching actual LearnFlow auth.ts
AUTH_CONFIG_TS = '''import { betterAuth } from "better-auth";
import { Pool } from "pg";

// Strip sslmode from connection string - we configure SSL explicitly below
const dbUrl = (process.env.DATABASE_URL || "").replace(/[?&]sslmode=[^&]*/g, "").replace(/\\?$/, "");

export const auth = betterAuth({
  database: new Pool({
    connectionString: dbUrl,
    ssl: { rejectUnauthorized: false },
  }),
  secret: process.env.AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
  trustedOrigins: [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
  ],
  emailAndPassword: {
    enabled: true,
  },
  user: {
    additionalFields: {
      role: {
        type: "string",
        defaultValue: "student",
        input: true,
      },
    },
  },
});
'''

# Auth client matching actual LearnFlow auth-client.ts
AUTH_CLIENT_TS = '''import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: typeof window !== "undefined" ? window.location.origin : "http://localhost:3000",
});

export const { useSession, signIn, signUp, signOut } = authClient;
'''

# API route handler matching actual pattern
AUTH_API_ROUTE = '''import { auth } from "../../../../../lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
'''

ENV_TEMPLATE = '''# Better Auth Configuration
DATABASE_URL="{database_url}"
AUTH_SECRET="{auth_secret}"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
'''


def configure_auth(project_dir, database_url):
    """Configure Better Auth with Neon PostgreSQL and role field."""
    project_path = Path(project_dir)

    if not project_path.exists():
        print(f"Error: Project directory not found: {project_dir}")
        return 1

    print(f"Configuring Better Auth with Neon PostgreSQL...")

    # Create lib directory
    lib_dir = project_path / "lib"
    lib_dir.mkdir(exist_ok=True)

    # Write auth config with role field and Neon SSL handling
    auth_file = lib_dir / "auth.ts"
    auth_file.write_text(AUTH_CONFIG_TS)
    print(f"  Created: lib/auth.ts (with role field + Neon SSL)")

    # Write auth client
    auth_client_file = lib_dir / "auth-client.ts"
    auth_client_file.write_text(AUTH_CLIENT_TS)
    print(f"  Created: lib/auth-client.ts (React client with useSession, signIn, signUp, signOut)")

    # Create API route: src/app/api/auth/[...all]/route.ts
    # Handle both src/app and app directory structures
    app_dir = project_path / "src" / "app" if (project_path / "src" / "app").exists() else project_path / "app"
    api_route_dir = app_dir / "api" / "auth" / "[...all]"
    api_route_dir.mkdir(parents=True, exist_ok=True)

    api_route_file = api_route_dir / "route.ts"
    api_route_file.write_text(AUTH_API_ROUTE)
    print(f"  Created: api/auth/[...all]/route.ts")

    # Create .env.local
    import secrets
    auth_secret = secrets.token_urlsafe(32)
    env_content = ENV_TEMPLATE.format(
        database_url=database_url if database_url else "your-neon-connection-string",
        auth_secret=auth_secret,
    )
    env_file = project_path / ".env.local"
    if not env_file.exists():
        env_file.write_text(env_content)
        print(f"  Created: .env.local (with generated AUTH_SECRET)")
    else:
        print(f"  Skipped: .env.local already exists")

    # Create .env.local.template
    template_content = ENV_TEMPLATE.format(
        database_url="postgresql://user:pass@host/db?sslmode=require",
        auth_secret="generate-with-openssl-rand-base64-32",
    )
    template_file = project_path / ".env.local.template"
    template_file.write_text(template_content)
    print(f"  Created: .env.local.template")

    print(f"\n✓ Better Auth configured")
    print(f"  Database: Neon PostgreSQL (SSL enabled)")
    print(f"  Auth: email/password with role field (student/teacher)")
    print(f"  Role field: user.role (default: 'student', input: true)")
    print(f"\n  Key patterns:")
    print(f"    - sslmode stripped from URL, SSL configured via Pool options")
    print(f"    - Role field added as additionalFields on user model")
    print(f"    - Auth client exports: useSession, signIn, signUp, signOut")
    print(f"\n→ Next: python scripts/generate_auth_pages.py --project-dir {project_dir}")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure Better Auth for LearnFlow")
    parser.add_argument("--project-dir", required=True, help="Next.js project directory")
    parser.add_argument("--database-url", default="",
                       help="Neon PostgreSQL connection string")
    args = parser.parse_args()
    sys.exit(configure_auth(args.project_dir, args.database_url))
