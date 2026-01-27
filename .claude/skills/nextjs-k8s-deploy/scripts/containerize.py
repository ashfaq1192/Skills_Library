#!/usr/bin/env python3
"""Containerize Next.js application."""
import subprocess, sys, argparse
from pathlib import Path

NEXTJS_DOCKERFILE = '''FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Disable telemetry during build
ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
'''

NEXTJS_CONFIG_NOTE = '''
# Note: Add to next.config.js for standalone build:
module.exports = {
  output: 'standalone',
}
'''

def containerize(project_dir, tag):
    """Build Docker image for Next.js app."""
    project_path = Path(project_dir)

    if not project_path.exists():
        print(f"❌ Project directory not found: {project_dir}")
        return 1

    # Check if .next exists
    next_dir = project_path / ".next"
    if not next_dir.exists():
        print(f"⚠ .next directory not found - build may be needed")
        print(f"→ Build first: python scripts/build_nextjs.py --project-dir {project_dir}")

    # Create Dockerfile if it doesn't exist
    dockerfile = project_path / "Dockerfile"
    if not dockerfile.exists():
        print("→ Creating Dockerfile...")
        dockerfile.write_text(NEXTJS_DOCKERFILE)
        print(f"  ✓ Dockerfile created")
        print(f"\n⚠ Note: Update next.config.js to include: output: 'standalone'")

    print(f"→ Building Docker image: {tag}")

    # Build image
    result = subprocess.run(
        ["docker", "build", "-t", tag, "."],
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=600
    )

    if result.returncode != 0:
        print(f"❌ Build failed: {result.stderr.strip()}")
        return 1

    # Get image size
    result = subprocess.run(
        ["docker", "images", tag, "--format", "{{.Size}}"],
        capture_output=True,
        text=True
    )

    size = result.stdout.strip() if result.returncode == 0 else "unknown"

    print(f"✓ Docker image built: {tag}")
    print(f"  Size: {size}")
    print(f"\n→ Test locally:")
    print(f"  docker run -p 3000:3000 {tag}")
    print(f"\n→ Generate manifests:")
    print(f"  python scripts/generate_manifests.py --image {tag}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, help="Next.js project directory")
    parser.add_argument("--tag", required=True, help="Docker image tag")
    args = parser.parse_args()
    sys.exit(containerize(args.project_dir, args.tag))
