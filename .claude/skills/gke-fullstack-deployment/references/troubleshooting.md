# GKE Deployment Troubleshooting Guide

Symptom-based guide. Find your error, follow the fix.

---

## "Failed to fetch" / Network errors in browser

**Symptom**: App loads but login/tasks fail. DevTools shows requests to `localhost`.

**Cause**: `NEXT_PUBLIC_*` vars were not set during `docker build`.

**Diagnose**:
```bash
# Check what URL is baked into the image
kubectl exec deploy/todo-frontend -n todo-app -- \
  grep -r "localhost:8000" .next/ 2>/dev/null | head -5
```
If there's output, the image has localhost baked in.

**Fix**: Rebuild frontend with `--build-arg`:
```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://<BACKEND_LB_IP> \
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL=http://<FRONTEND_LB_IP> \
  --build-arg BETTER_AUTH_URL=http://<FRONTEND_LB_IP> \
  --platform linux/amd64 \
  -t <USER>/todo-frontend:<NEW_VERSION> \
  -f <DOCKERFILE> <SOURCE>
docker push <USER>/todo-frontend:<NEW_VERSION>
# Update deploy.yaml and restart pods
```

---

## CORS errors in browser console

**Symptom**: Console shows "Access to fetch blocked by CORS policy".

**Cause**: Backend `CORS_ORIGINS` doesn't include frontend LB IP.

**Diagnose**:
```bash
kubectl exec deploy/todo-backend -n todo-app -- env | grep CORS
```

**Fix**:
```bash
# Option A: Update secret
kubectl delete secret project-secrets -n todo-app --ignore-not-found
kubectl create secret generic project-secrets -n todo-app \
  --from-literal=CORS_ORIGINS="http://<FRONTEND_LB_IP>,http://localhost:3000" \
  # ... other secrets ...

# Option B: Quick env override (no secret rebuild)
kubectl set env deployment/todo-backend \
  CORS_ORIGINS="http://<FRONTEND_LB_IP>,http://localhost:3000" \
  -n todo-app
```

---

## 401 Unauthorized on all API calls

**Symptom**: Login succeeds but every API request returns 401.

**Cause**: JWT secret mismatch between frontend and backend.

**Diagnose**:
```bash
# Compare secrets (will show base64-encoded values)
kubectl get secret project-secrets -n todo-app -o jsonpath='{.data.JWT_SECRET_KEY}' | base64 -d
```

**Fix**: Ensure `JWT_SECRET_KEY` is identical in both frontend and backend env.

---

## Pod in CrashLoopBackOff

**Symptom**: `kubectl get pods` shows `CrashLoopBackOff`.

**Diagnose**:
```bash
# Check logs
kubectl logs deploy/todo-frontend -n todo-app --previous
kubectl logs deploy/todo-backend -n todo-app --previous

# Check events
kubectl describe pod -l app=todo-frontend -n todo-app
```

**Common causes**:
| Log Message | Cause | Fix |
|-------------|-------|-----|
| `exec format error` | ARM64 image on AMD64 node | Rebuild with `--platform linux/amd64` |
| `MODULE_NOT_FOUND` | Missing dependency | Check Dockerfile COPY steps |
| `ECONNREFUSED` | DB connection failed | Verify `DATABASE_URL` in secret |
| `BETTER_AUTH_SECRET` error | Missing auth secret | Add to K8s secret |

---

## LoadBalancer stuck on `<pending>`

**Symptom**: `kubectl get svc` shows EXTERNAL-IP as `<pending>` indefinitely.

**Cause**: GKE can't provision a LoadBalancer (quota, permissions, or cluster issue).

**Diagnose**:
```bash
kubectl describe svc todo-frontend-lb -n todo-app
# Look for events with error messages
```

**Fixes**:
- Check GKE quotas: `gcloud compute project-info describe --project <PROJECT>`
- Ensure the cluster has the correct IAM roles for LoadBalancer provisioning
- Try `kubectl delete svc <svc-name> -n todo-app` and recreate

---

## Image pull errors (ImagePullBackOff)

**Symptom**: Pod shows `ImagePullBackOff` or `ErrImagePull`.

**Diagnose**:
```bash
kubectl describe pod -l app=todo-frontend -n todo-app
# Look for "Failed to pull image" in events
```

**Common causes**:
| Error | Fix |
|-------|-----|
| "unauthorized" | `docker login` then push again |
| "not found" | Check image name/tag matches exactly |
| "manifest unknown" | Image wasn't pushed for linux/amd64 |

---

## Frontend shows blank page (no errors)

**Symptom**: Page loads but is blank. No console errors.

**Diagnose**:
```bash
# Check if standalone output was generated
kubectl exec deploy/todo-frontend -n todo-app -- ls -la .next/
# Should have standalone/ and static/ directories
```

**Cause**: `next.config.js` missing `output: "standalone"`.

**Fix**: The Dockerfile should add it automatically. If not, add to `next.config.js`:
```js
const nextConfig = {
  output: "standalone",
  // ... rest of config
};
```

---

## Health check failing

**Symptom**: Pod restarts repeatedly. Events show "Liveness probe failed".

**Diagnose**:
```bash
kubectl describe pod -l app=todo-backend -n todo-app | grep -A5 "Liveness"
```

**Common causes**:
- App takes too long to start → increase `initialDelaySeconds`
- Health endpoint not implemented → add `/health` route
- Wrong port in health check → match container port

---

## Quick Diagnostic Commands

```bash
# Overall status
kubectl get all -n todo-app

# Pod logs (follow)
kubectl logs -f deploy/todo-frontend -n todo-app
kubectl logs -f deploy/todo-backend -n todo-app

# Env vars in running pod
kubectl exec deploy/todo-backend -n todo-app -- env | sort

# Test backend from inside cluster
kubectl run curl --rm -it --image=curlimages/curl -n todo-app -- \
  curl http://todo-backend:8000/health

# Test backend from outside
curl http://<BACKEND_LB_IP>/health

# Check resource usage
kubectl top pods -n todo-app
```
