#!/usr/bin/env python3
"""Configure Better Auth with database and OAuth providers."""
import sys, argparse
from pathlib import Path

AUTH_CONFIG_TS = '''import { betterAuth } from "better-auth"
import { Pool } from "pg"

const pool = new Pool({{
  connectionString: process.env.DATABASE_URL,
}})

export const auth = betterAuth({{
  database: {{
    provider: "postgres",
    pool,
  }},
  emailAndPassword: {{
    enabled: true,
  }},
  socialProviders: {{{social_config}
  }},
  secret: process.env.AUTH_SECRET || "your-secret-key-change-in-production",
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
}})
'''

SOCIAL_GOOGLE = '''
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },'''

SOCIAL_GITHUB = '''
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },'''

AUTH_API_ROUTE = '''import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"

export const { GET, POST } = toNextJsHandler(auth)
'''

ENV_TEMPLATE = '''# Better Auth Configuration
DATABASE_URL="your-neon-connection-string"
AUTH_SECRET="generate-a-secure-random-string"
NEXT_PUBLIC_APP_URL="http://localhost:3000"

# OAuth Providers (optional)
{oauth_env}
'''

def configure_auth(project_dir, database_url, providers):
    """Configure Better Auth."""
    project_path = Path(project_dir)

    if not project_path.exists():
        print(f"❌ Project directory not found: {project_dir}")
        return 1

    print(f"→ Configuring Better Auth...")

    # Create lib directory
    lib_dir = project_path / "lib"
    lib_dir.mkdir(exist_ok=True)

    # Generate social provider config
    social_config = ""
    oauth_env = ""

    if providers:
        provider_list = [p.strip().lower() for p in providers.split(',')]

        if 'google' in provider_list:
            social_config += SOCIAL_GOOGLE
            oauth_env += "GOOGLE_CLIENT_ID=your-google-client-id\n"
            oauth_env += "GOOGLE_CLIENT_SECRET=your-google-client-secret\n"

        if 'github' in provider_list:
            social_config += SOCIAL_GITHUB
            oauth_env += "GITHUB_CLIENT_ID=your-github-client-id\n"
            oauth_env += "GITHUB_CLIENT_SECRET=your-github-client-secret\n"

    # Write auth config
    auth_config = AUTH_CONFIG_TS.format(social_config=social_config)
    auth_file = lib_dir / "auth.ts"
    auth_file.write_text(auth_config)

    print(f"  ✓ Created: lib/auth.ts")

    # Create API route
    api_route_dir = project_path / "app" / "api" / "auth" / "[...all]"
    api_route_dir.mkdir(parents=True, exist_ok=True)

    api_route_file = api_route_dir / "route.ts"
    api_route_file.write_text(AUTH_API_ROUTE)

    print(f"  ✓ Created: app/api/auth/[...all]/route.ts")

    # Create .env.local template
    env_content = ENV_TEMPLATE.format(oauth_env=oauth_env)
    env_file = project_path / ".env.local.template"
    env_file.write_text(env_content)

    print(f"  ✓ Created: .env.local.template")

    # Update actual .env.local if database_url provided
    if database_url and database_url != "your-neon-connection-string":
        env_local = project_path / ".env.local"
        current_env = env_local.read_text() if env_local.exists() else ""

        if "DATABASE_URL" not in current_env:
            with env_local.open('a') as f:
                f.write(f"\n# Better Auth\\nDATABASE_URL=\"{database_url}\"\\n")
            print(f"  ✓ Updated: .env.local")

    print(f"\n✓ Better Auth configured")
    print(f"  Database: PostgreSQL")
    print(f"  Providers: email/password{', ' + providers if providers else ''}")
    print(f"\n⚠ Action required:")
    print(f"  1. Copy .env.local.template to .env.local")
    print(f"  2. Fill in OAuth credentials (if using)")
    print(f"  3. Generate AUTH_SECRET: openssl rand -base64 32")
    print(f"\n→ Next: python scripts/generate_auth_pages.py --project-dir {project_dir}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, help="Next.js project directory")
    parser.add_argument("--database-url", default="your-neon-connection-string",
                       help="Neon PostgreSQL connection string")
    parser.add_argument("--providers", help="Comma-separated OAuth providers (google,github)")
    args = parser.parse_args()
    sys.exit(configure_auth(args.project_dir, args.database_url, args.providers))
