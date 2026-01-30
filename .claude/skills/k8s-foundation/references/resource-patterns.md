# Kubernetes Resource Patterns

Common patterns and templates for K8s resources.

## Deployment Pattern

Standard microservice deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
  labels:
    app: myapp
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: v1
    spec:
      serviceAccountName: myapp-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: myapp
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: myapp-config
              key: LOG_LEVEL
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: myapp-secret
              key: password
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - myapp
              topologyKey: kubernetes.io/hostname
```

## Service Patterns

### ClusterIP (Internal)

Default service type for internal communication:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
```

### LoadBalancer (External)

Expose service externally:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-lb
  namespace: production
spec:
  type: LoadBalancer
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
```

### Headless Service

For StatefulSets or service discovery:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-headless
spec:
  clusterIP: None
  selector:
    app: myapp
  ports:
  - port: 8080
```

## ConfigMap Pattern

Configuration management:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
  namespace: production
data:
  # Simple values
  LOG_LEVEL: "info"
  API_ENDPOINT: "https://api.example.com"

  # File content
  app.properties: |
    server.port=8080
    server.context-path=/api
    logging.level=INFO
```

Usage in pod:
```yaml
# As environment variables
envFrom:
- configMapRef:
    name: myapp-config

# As volume mount
volumes:
- name: config
  configMap:
    name: myapp-config
volumeMounts:
- name: config
  mountPath: /etc/config
```

## Secret Pattern

Sensitive data management:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secret
  namespace: production
type: Opaque
stringData:
  username: admin
  password: secretpassword123
  api-key: abc123xyz
```

Usage in pod:
```yaml
env:
- name: DB_USERNAME
  valueFrom:
    secretKeyRef:
      name: myapp-secret
      key: username
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: myapp-secret
      key: password
```

## Ingress Pattern

HTTP/HTTPS routing:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp
            port:
              number: 80
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
```

## StatefulSet Pattern

For stateful applications:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mydb
  namespace: production
spec:
  serviceName: mydb-headless
  replicas: 3
  selector:
    matchLabels:
      app: mydb
  template:
    metadata:
      labels:
        app: mydb
    spec:
      containers:
      - name: mydb
        image: postgres:14
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mydb-secret
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

## Job Pattern

One-time or batch jobs:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-migration
  namespace: production
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: migrate
        image: myapp-migrator:v1.0.0
        command: ["python", "migrate.py"]
        env:
        - name: DB_HOST
          value: "postgres.production.svc.cluster.local"
  backoffLimit: 3
  activeDeadlineSeconds: 600
```

## CronJob Pattern

Scheduled tasks:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup
  namespace: production
spec:
  schedule: "0 2 * * *"  # Daily at 2am
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: backup-tool:v1.0.0
            command: ["sh", "-c", "backup.sh"]
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
```

## PersistentVolumeClaim Pattern

Storage requests:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: myapp-storage
  namespace: production
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: standard
```

## Multi-Container Pod Pattern

Sidecar, ambassador, adapter patterns:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-with-sidecar
spec:
  containers:
  # Main application
  - name: myapp
    image: myapp:v1.0.0
    ports:
    - containerPort: 8080
    volumeMounts:
    - name: shared-data
      mountPath: /app/data

  # Sidecar (log shipping)
  - name: log-shipper
    image: fluent/fluent-bit:latest
    volumeMounts:
    - name: shared-data
      mountPath: /data

  volumes:
  - name: shared-data
    emptyDir: {}
```

## HorizontalPodAutoscaler Pattern

Auto-scaling based on metrics:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Official References

- [Kubernetes API Reference](https://kubernetes.io/docs/reference/kubernetes-api/)
- [Workload Resources](https://kubernetes.io/docs/concepts/workloads/)
- [Service Resources](https://kubernetes.io/docs/concepts/services-networking/)
- [Configuration Resources](https://kubernetes.io/docs/concepts/configuration/)
