#!/usr/bin/env python3
"""Add authentication middleware to Next.js app."""
import sys, argparse
from pathlib import Path

MIDDLEWARE_TS = '''import { NextResponse } from \"next/server\"
import type { NextRequest } from \"next/server\"

// Routes that require authentication
const protectedRoutes = [\"/dashboard\", \"/profile\", \"/settings\"]

// Routes that should redirect to dashboard if authenticated
const authRoutes = [\"/login\", \"/signup\"]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Check if route requires authentication
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  )
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route))

  // Get session cookie
  const sessionCookie = request.cookies.get(\"better-auth.session_token\")
  const hasSession = !!sessionCookie

  // Redirect to login if accessing protected route without session
  if (isProtectedRoute && !hasSession) {
    const url = new URL(\"/login\", request.url)
    url.searchParams.set(\"from\", pathname)
    return NextResponse.redirect(url)
  }

  // Redirect to dashboard if accessing auth routes with session
  if (isAuthRoute && hasSession) {
    return NextResponse.redirect(new URL(\"/dashboard\", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     * - api routes
     */
    \"/((?!_next/static|_next/image|favicon.ico|.*\\\\.(?:svg|png|jpg|jpeg|gif|webp)$|api).*)\",
  ],
}
'''

def add_middleware(project_dir):
    """Add authentication middleware."""
    project_path = Path(project_dir)

    if not project_path.exists():
        print(f"❌ Project directory not found: {project_dir}")
        return 1

    # Check if middleware already exists
    middleware_file = project_path / "middleware.ts"

    if middleware_file.exists():
        print(f"⚠ middleware.ts already exists")
        backup_file = project_path / "middleware.ts.backup"
        middleware_file.rename(backup_file)
        print(f"  Backed up to: middleware.ts.backup")

    # Write middleware
    middleware_file.write_text(MIDDLEWARE_TS)

    print(f"✓ Middleware added: middleware.ts")
    print(f"\n→ Protected routes:")
    print(f"  - /dashboard")
    print(f"  - /profile")
    print(f"  - /settings")
    print(f"\n→ Customize:")
    print(f"  Edit protectedRoutes array in middleware.ts")
    print(f"\n✓ Better Auth setup complete!")
    print(f"\n→ Test authentication:")
    print(f"  1. npm run dev")
    print(f"  2. Visit http://localhost:3000/signup")
    print(f"  3. Create account and test login")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, help="Next.js project directory")
    args = parser.parse_args()
    sys.exit(add_middleware(args.project_dir))
