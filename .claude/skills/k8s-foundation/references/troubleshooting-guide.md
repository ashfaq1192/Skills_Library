# Kubernetes Troubleshooting Guide

Systematic approach to diagnosing and fixing common K8s issues.

## Troubleshooting Workflow

```
1. Identify symptoms (pod status, service behavior)
   ↓
2. Check events (kubectl describe)
   ↓
3. Examine logs (kubectl logs)
   ↓
4. Verify configuration (labels, selectors, env vars)
   ↓
5. Test connectivity (kubectl exec, port-forward)
   ↓
6. Fix and verify
```

## Common Issues and Solutions

### Pods Stuck in Pending

**Symptoms**: Pod shows `Pending` status for extended time.

**Diagnosis**:
```bash
kubectl describe pod <pod-name> -n <namespace>
```

**Common Causes**:

1. **Insufficient Resources**
   ```
   Events: 0/3 nodes are available: insufficient memory/cpu
   ```
   **Fix**: Reduce resource requests or add nodes

2. **No Matching Nodes**
   ```
   Events: 0/3 nodes are available: node selector/affinity mismatch
   ```
   **Fix**: Adjust node selectors or labels

3. **PersistentVolumeClaim Not Bound**
   ```
   Events: pod has unbound immediate PersistentVolumeClaims
   ```
   **Fix**: Create PV or check StorageClass

### Pods in CrashLoopBackOff

**Symptoms**: Pod repeatedly crashes and restarts.

**Diagnosis**:
```bash
kubectl logs <pod-name> -n <namespace> --previous
kubectl describe pod <pod-name> -n <namespace>
```

**Common Causes**:

1. **Application Errors**
   - Check logs for stack traces, errors
   - Verify application configuration
   - Test application locally first

2. **Missing Dependencies**
   - Database not available
   - Required services not running
   - Environment variables not set

3. **Liveness Probe Failing**
   - Probe too aggressive (short timeout)
   - Application slow to start
   - Health endpoint misconfigured

**Fixes**:
```yaml
# Increase initial delay
livenessProbe:
  initialDelaySeconds: 60  # Give app time to start
```

### ImagePullBackOff

**Symptoms**: Cannot pull container image.

**Diagnosis**:
```bash
kubectl describe pod <pod-name> -n <namespace>
```

**Common Causes**:

1. **Image Name Typo**
   ```
   Error: manifest for image:tag not found
   ```
   **Fix**: Correct image name and tag

2. **Private Registry Authentication**
   ```
   Error: pull access denied
   ```
   **Fix**: Create imagePullSecret:
   ```bash
   kubectl create secret docker-registry regcred \
     --docker-server=<registry> \
     --docker-username=<user> \
     --docker-password=<pass>
   ```

   Then reference in pod spec:
   ```yaml
   imagePullSecrets:
   - name: regcred
   ```

3. **Rate Limiting (Docker Hub)**
   ```
   Error: toomanyrequests
   ```
   **Fix**: Use authenticated pulls or mirror registry

### Service Not Routing Traffic

**Symptoms**: Service exists but requests fail or timeout.

**Diagnosis**:
```bash
kubectl get endpoints <service-name> -n <namespace>
kubectl describe service <service-name> -n <namespace>
```

**Common Causes**:

1. **Selector Mismatch**
   - Service selector doesn't match pod labels
   - Check: `kubectl get pods -n <namespace> --show-labels`
   - Fix: Align selectors with pod labels

2. **No Ready Pods**
   - Pods exist but readiness probe failing
   - Check: `kubectl get pods -n <namespace>`
   - Fix: Check pod logs, adjust readiness probe

3. **Target Port Wrong**
   - Service targeting wrong container port
   - Fix: Verify `targetPort` matches container's `containerPort`

### DNS Resolution Failing

**Symptoms**: Pods cannot resolve service names.

**Diagnosis**:
```bash
kubectl exec -it <pod-name> -n <namespace> -- nslookup kubernetes.default
```

**Fixes**:

1. **Check CoreDNS**
   ```bash
   kubectl get pods -n kube-system -l k8s-app=kube-dns
   ```

2. **Verify DNS Policy**
   ```yaml
   dnsPolicy: ClusterFirst  # Default, uses cluster DNS
   ```

3. **Test Service DNS**
   ```bash
   # Full FQDN
   <service>.<namespace>.svc.cluster.local
   ```

### Persistent Volume Issues

**Symptoms**: PVC stays in `Pending`, or data not persisting.

**Diagnosis**:
```bash
kubectl get pvc -n <namespace>
kubectl describe pvc <pvc-name> -n <namespace>
kubectl get pv
```

**Common Causes**:

1. **No Available PV**
   - No PV matches PVC requirements
   - Fix: Create PV or use dynamic provisioning

2. **StorageClass Missing**
   ```yaml
   storageClassName: standard  # Must exist
   ```
   - Check: `kubectl get storageclass`

3. **Access Mode Mismatch**
   - PV and PVC have incompatible access modes
   - Fix: Match accessModes (ReadWriteOnce, ReadWriteMany, etc.)

## Diagnostic Commands

### Quick Health Check
```bash
# Cluster health
kubectl cluster-info
kubectl get nodes
kubectl get pods --all-namespaces

# Specific namespace
kubectl get all -n <namespace>
```

### Detailed Investigation
```bash
# Pod details
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace>
kubectl logs <pod> -n <namespace> --previous  # Previous crash

# Events (last hour)
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Resource usage
kubectl top nodes
kubectl top pods -n <namespace>
```

### Interactive Debugging
```bash
# Execute commands in pod
kubectl exec -it <pod> -n <namespace> -- /bin/bash

# Port forward for testing
kubectl port-forward <pod> -n <namespace> 8080:8080

# Copy files from pod
kubectl cp <namespace>/<pod>:/path/to/file ./local-file
```

### Network Debugging
```bash
# Test service connectivity
kubectl run tmp --rm -i --tty --image=busybox -n <namespace> -- /bin/sh
# Inside pod:
wget -O- <service-name>:<port>

# Check service endpoints
kubectl get endpoints <service> -n <namespace>
```

## Prevention

### Pre-deployment Checklist
- [ ] Resource requests and limits set
- [ ] Liveness and readiness probes configured
- [ ] Correct image name and tag
- [ ] ImagePullSecrets for private registries
- [ ] Service selector matches pod labels
- [ ] ConfigMaps and Secrets exist
- [ ] Namespace exists and has quotas
- [ ] Network policies allow required traffic

### Monitoring
- Set up cluster monitoring (Prometheus + Grafana)
- Configure alerts for pod crashes, high resource usage
- Log aggregation (ELK, Loki)
- Distributed tracing for microservices

## Official Resources

- [Kubernetes Debugging](https://kubernetes.io/docs/tasks/debug/)
- [Application Introspection](https://kubernetes.io/docs/tasks/debug/debug-application/)
- [Cluster Troubleshooting](https://kubernetes.io/docs/tasks/debug/debug-cluster/)
