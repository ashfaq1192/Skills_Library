# GKE Deployment Pitfalls

Hard-won lessons from real deployments. Read this BEFORE every deployment.

---

## Pitfall #1: "Failed to Fetch" — localhost URLs Baked into Frontend

**Severity**: CRITICAL — App loads but nothing works

**What happens**:
Next.js `NEXT_PUBLIC_*` environment variables are replaced with their literal values
during `npm run build`. They become hardcoded strings in the JavaScript bundle.
If they're unset or point to `localhost` during the Docker build, the browser will
try to call `localhost:8000` in production — which doesn't exist.

**How to detect**:
- Open browser DevTools → Network tab → look for requests to `localhost:8000`
- Or: `kubectl exec deploy/todo-frontend -- grep -r "localhost:8000" .next/`

**The fix**:
Pass correct URLs as Docker build args:
```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://34.57.215.48 \
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL=http://34.44.146.146 \
  ...
```

**Why NOT just set env vars in K8s?**:
Because Next.js `NEXT_PUBLIC_*` vars are compile-time, not runtime. Setting them in
a K8s ConfigMap or Secret has ZERO effect on the client-side JavaScript. The values
are already frozen in the `.next/` build output.

| Variable Prefix | When It's Read | Can Change at Runtime? |
|-----------------|----------------|----------------------|
| `NEXT_PUBLIC_*` | `npm run build` (compile time) | NO — baked into JS |
| No prefix (e.g. `DATABASE_URL`) | Server startup (runtime) | YES — via K8s env |

---

## Pitfall #2: .dockerignore Blocks .env Files

**Severity**: HIGH — Build succeeds but with wrong values

**What happens**:
You create a `.env` or `.env.local` file with the correct URLs, but the
`.dockerignore` contains:
```
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
```
Docker silently ignores these files. The build uses defaults (localhost).

**How to detect**:
```bash
# Check what's in .dockerignore
cat <frontend-source>/.dockerignore | grep env
```

**The fix**:
Use `--build-arg` instead of `.env` files. Build args bypass `.dockerignore` entirely.

**Alternative** (if you must use files):
`.env.production` (without `.local` suffix) is often NOT in `.dockerignore`.
But `--build-arg` is more explicit and reliable.

---

## Pitfall #3: CORS Rejection

**Severity**: HIGH — Login/API calls fail silently

**What happens**:
The backend's `CORS_ORIGINS` defaults to `http://localhost:3000`. When the browser
at `http://34.44.146.146` makes a request to `http://34.57.215.48`, the backend
rejects it because the origin isn't in the allowed list.

**How to detect**:
- Browser DevTools → Console → "CORS policy" error
- Browser DevTools → Network tab → preflight OPTIONS request returns 403

**The fix**:
Set `CORS_ORIGINS` env var on the backend to include the frontend LB IP:
```bash
CORS_ORIGINS=http://34.44.146.146,http://localhost:3000
```

This is a RUNTIME env var for FastAPI, so it can be set via K8s Secret/ConfigMap
without rebuilding the backend image.

---

## Pitfall #4: BETTER_AUTH_SECRET Not Set During Build

**Severity**: LOW — Warning only, but confusing

**What happens**:
During `npm run build`, Next.js pre-renders pages and initializes Better Auth.
Without `BETTER_AUTH_SECRET`, you see:
```
[Error [BetterAuthError]: You are using the default secret.
Please set `BETTER_AUTH_SECRET` in your environment variables...]
```

**Impact**: The build succeeds. The error only affects static page generation,
not runtime auth. Auth works correctly at runtime when the K8s secret provides
the real `BETTER_AUTH_SECRET`.

**The fix**: Ignore during build. Or pass a dummy value:
```bash
--build-arg BETTER_AUTH_SECRET=build-time-placeholder
```

---

## Pitfall #5: Wrong Platform Architecture

**Severity**: HIGH — Pod crashes with exec format error

**What happens**:
Building on Apple Silicon (M1/M2/M3) produces ARM64 images by default.
GKE nodes are x86_64 (AMD64). The pod crashes immediately.

**How to detect**:
```bash
kubectl describe pod <pod-name> -n todo-app
# Look for: "exec format error" in events
```

**The fix**:
Always specify platform in the build command:
```bash
docker build --platform linux/amd64 ...
```

---

## Pitfall #6: JWT Secret Mismatch

**Severity**: HIGH — Login succeeds but all API calls fail

**What happens**:
Frontend's `JWT_SECRET_KEY` and backend's `JWT_SECRET_KEY` don't match.
The frontend generates tokens the backend can't verify, returning 401 on every request.

**How to detect**:
- Login works, but task list is empty or shows "unauthorized"
- Backend logs show JWT validation errors

**The fix**:
Use the SAME secret value in both frontend and backend K8s secrets.
Generate once: `openssl rand -hex 32` and use everywhere.

---

## Pitfall #7: Chicken-and-Egg — Need IPs Before Building

**Severity**: MEDIUM — Workflow confusion

**What happens**:
You need LoadBalancer IPs to bake into the frontend image, but IPs are only
assigned after you deploy services to GKE.

**The fix (two-pass deployment)**:
1. **First pass**: Deploy with any image (even broken) to get LoadBalancer IPs
2. **Record IPs**: `kubectl get svc -n todo-app`
3. **Second pass**: Rebuild frontend with correct IPs, push, update deployment

This is normal. Don't try to guess IPs or use internal cluster IPs.

---

## Pitfall #8: Forgetting to Restart Pods After Secret Update

**Severity**: MEDIUM — Old config still running

**What happens**:
You update K8s secrets but existing pods still use the old values.
K8s does NOT auto-restart pods when secrets change.

**The fix**:
```bash
# Force restart all pods in namespace
kubectl delete pods --all --namespace=todo-app

# Or restart specific deployment
kubectl rollout restart deployment/todo-backend -n todo-app
kubectl rollout restart deployment/todo-frontend -n todo-app
```
