#!/usr/bin/env python3
"""Generate authentication pages for Better Auth."""
import sys, argparse
from pathlib import Path

LOGIN_PAGE = '''\"use client\"

import { useState } from \"react\"
import { useRouter } from \"next/navigation\"
import { authClient } from \"@/lib/auth-client\"

export default function LoginPage() {
  const [email, setEmail] = useState(\"\")
  const [password, setPassword] = useState(\"\")
  const [error, setError] = useState(\"\")
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(\"\")

    try {
      await authClient.signIn.email({ email, password })
      router.push(\"/dashboard\")
    } catch (err) {
      setError(\"Invalid credentials\")
    }
  }

  return (
    <div className=\"min-h-screen flex items-center justify-center\">
      <div className=\"max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow\">
        <h2 className=\"text-3xl font-bold text-center\">Sign In</h2>

        {error && (
          <div className=\"bg-red-50 text-red-500 p-3 rounded\">{error}</div>
        )}

        <form onSubmit={handleSubmit} className=\"space-y-6\">
          <div>
            <label className=\"block text-sm font-medium\">Email</label>
            <input
              type=\"email\"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className=\"mt-1 block w-full rounded border p-2\"
              required
            />
          </div>

          <div>
            <label className=\"block text-sm font-medium\">Password</label>
            <input
              type=\"password\"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className=\"mt-1 block w-full rounded border p-2\"
              required
            />
          </div>

          <button
            type=\"submit\"
            className=\"w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700\"
          >
            Sign In
          </button>
        </form>

        <p className=\"text-center text-sm\">
          Don\\'t have an account?{\" \"}
          <a href=\"/signup\" className=\"text-blue-600 hover:underline\">
            Sign up
          </a>
        </p>
      </div>
    </div>
  )
}
'''

SIGNUP_PAGE = '''\"use client\"

import { useState } from \"react\"
import { useRouter } from \"next/navigation\"
import { authClient } from \"@/lib/auth-client\"

export default function SignupPage() {
  const [email, setEmail] = useState(\"\")
  const [password, setPassword] = useState(\"\")
  const [name, setName] = useState(\"\")
  const [error, setError] = useState(\"\")
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(\"\")

    try {
      await authClient.signUp.email({ email, password, name })
      router.push(\"/dashboard\")
    } catch (err) {
      setError(\"Failed to create account\")
    }
  }

  return (
    <div className=\"min-h-screen flex items-center justify-center\">
      <div className=\"max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow\">
        <h2 className=\"text-3xl font-bold text-center\">Create Account</h2>

        {error && (
          <div className=\"bg-red-50 text-red-500 p-3 rounded\">{error}</div>
        )}

        <form onSubmit={handleSubmit} className=\"space-y-6\">
          <div>
            <label className=\"block text-sm font-medium\">Name</label>
            <input
              type=\"text\"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className=\"mt-1 block w-full rounded border p-2\"
              required
            />
          </div>

          <div>
            <label className=\"block text-sm font-medium\">Email</label>
            <input
              type=\"email\"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className=\"mt-1 block w-full rounded border p-2\"
              required
            />
          </div>

          <div>
            <label className=\"block text-sm font-medium\">Password</label>
            <input
              type=\"password\"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className=\"mt-1 block w-full rounded border p-2\"
              required
              minLength={8}
            />
          </div>

          <button
            type=\"submit\"
            className=\"w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700\"
          >
            Sign Up
          </button>
        </form>

        <p className=\"text-center text-sm\">
          Already have an account?{\" \"}
          <a href=\"/login\" className=\"text-blue-600 hover:underline\">
            Sign in
          </a>
        </p>
      </div>
    </div>
  )
}
'''

AUTH_CLIENT = '''import { createAuthClient } from \"better-auth/react\"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || \"http://localhost:3000\",
})
'''

def generate_auth_pages(project_dir):
    """Generate login and signup pages."""
    project_path = Path(project_dir)

    if not project_path.exists():
        print(f"❌ Project directory not found: {project_dir}")
        return 1

    print(f"→ Generating auth pages...")

    # Create auth client
    lib_dir = project_path / "lib"
    lib_dir.mkdir(exist_ok=True)

    auth_client_file = lib_dir / "auth-client.ts"
    auth_client_file.write_text(AUTH_CLIENT)

    print(f"  ✓ Created: lib/auth-client.ts")

    # Create login page
    login_dir = project_path / "app" / "login"
    login_dir.mkdir(parents=True, exist_ok=True)

    login_page = login_dir / "page.tsx"
    login_page.write_text(LOGIN_PAGE)

    print(f"  ✓ Created: app/login/page.tsx")

    # Create signup page
    signup_dir = project_path / "app" / "signup"
    signup_dir.mkdir(parents=True, exist_ok=True)

    signup_page = signup_dir / "page.tsx"
    signup_page.write_text(SIGNUP_PAGE)

    print(f"  ✓ Created: app/signup/page.tsx")

    print(f"\n✓ Auth pages generated")
    print(f"  Routes:")
    print(f"    - /login")
    print(f"    - /signup")
    print(f"\n→ Next: python scripts/add_middleware.py --project-dir {project_dir}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, help="Next.js project directory")
    args = parser.parse_args()
    sys.exit(generate_auth_pages(args.project_dir))
