# Pod

## Minimal Example
```yaml
apiVersion: v1
kind: Pod
metadata:
  # The unique name of the pod within the namespace
  name: nginx-minimal
  # Namespace where the pod will run
  namespace: default
spec:
  containers:
    # Name of the container inside the pod
  - name: web-server
    # Docker Hub image for nginx
    image: nginx:1.25.3
    ports:
    # The port container exposes
    - containerPort: 80
```

## Production Example
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-production
  namespace: production
  # Labels used for grouping, routing, and selection
  labels:
    app: secure-web
    tier: frontend
    environment: production
  # Annotations for external integrations (e.g., Prometheus)
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "80"
spec:
  # Restrict container privileges for host-level security
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001
    seccompProfile:
      type: RuntimeDefault
  # Grace period to allow application to exit cleanly before termination (seconds)
  terminationGracePeriodSeconds: 60
  # Ensure pod only schedules on specific node architectures
  nodeSelector:
    kubernetes.io/arch: amd64
  containers:
  - name: nginx-app
    image: nginx:1.25.3-alpine
    # Do not pull image if already present on host node
    imagePullPolicy: IfNotPresent
    ports:
    - name: http
      containerPort: 80
      protocol: TCP
    # Env vars loaded from secure ConfigMaps
    env:
    - name: APP_ENV
      value: "production"
    # Overwrite container security context
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: false
    # Resource allocations to guarantee and limit consumption
    resources:
      requests:
        cpu: 250m
        memory: 256Mi
      limits:
        cpu: 500m
        memory: 512Mi
    # Readiness probe determines when pod is ready to accept traffic
    readinessProbe:
      httpGet:
        path: /index.html
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3
    # Liveness probe restarts container if application hangs/crashes
    livenessProbe:
      httpGet:
        path: /index.html
        port: 80
      initialDelaySeconds: 15
      periodSeconds: 20
      timeoutSeconds: 5
      successThreshold: 1
      failureThreshold: 3
```

## Advanced Example
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-advanced-pod
  namespace: production
  labels:
    app: advanced-app
    version: v1.2.0
spec:
  # Disabling service account auto-mount to prevent token theft if compromised
  automountServiceAccountToken: false
  # Node scheduling affinity rules
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: topology.kubernetes.io/zone
            operator: In
            values:
            - us-east-1a
            - us-east-1b
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - advanced-app
          topologyKey: kubernetes.io/hostname
  # Tolerations allow scheduling on tainted nodes (e.g., control plane)
  tolerations:
  - key: "node-role.kubernetes.io/control-plane"
    operator: "Exists"
    effect: "NoSchedule"
  # Ensures even distribution across failure domains
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app: advanced-app
  # Init containers execute before main application containers
  initContainers:
  - name: wait-for-database
    image: busybox:1.36.1
    command: ['sh', '-c', 'until nc -z -w 2 database.production.svc.cluster.local 5432; do echo waiting for db; sleep 2; done']
    resources:
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        cpu: 100m
        memory: 128Mi
  containers:
  - name: main-application
    image: python:3.11-alpine
    command: ["python", "-m", "http.server", "8080"]
    ports:
    - name: http-port
      containerPort: 8080
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 300m
        memory: 256Mi
    # Lifecycle events
    lifecycle:
      postStart:
        exec:
          command: ["/bin/sh", "-c", "echo App Started >> /var/log/app.log"]
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 15"]
    volumeMounts:
    - name: shared-data
      mountPath: /var/log
  - name: sidecar-logger
    image: alpine:3.18
    command: ["tail", "-f", "/var/log/app.log"]
    resources:
      requests:
        cpu: 50m
        memory: 64Mi
      limits:
        cpu: 100m
        memory: 128Mi
    volumeMounts:
    - name: shared-data
      mountPath: /var/log
  volumes:
  # Ephemeral in-memory emptyDir shared between containers
  - name: shared-data
    emptyDir:
      medium: Memory

---

# Deployment

## Minimal Example
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment-minimal
  namespace: default
spec:
  # Desired number of pod replicas
  replicas: 2
  # Used to associate Pods with this Deployment
  selector:
    matchLabels:
      app: nginx-min
  template:
    metadata:
      labels:
        app: nginx-min
    spec:
      containers:
      - name: nginx
        image: nginx:1.25.3
        ports:
        - containerPort: 80
```

## Production Example
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-api-production
  namespace: production
  labels:
    app: web-api
    tier: backend
    environment: production
spec:
  replicas: 3
  # History limit of old ReplicaSets retained for rollback purposes
  revisionHistoryLimit: 10
  # Strategy for updating pods
  strategy:
    type: RollingUpdate
    rollingUpdate:
      # Max number of pods that can be created above the desired amount during update
      maxSurge: 25%
      # Max number of pods that can be unavailable during update
      maxUnavailable: 0
  selector:
    matchLabels:
      app: web-api
  template:
    metadata:
      labels:
        app: web-api
        tier: backend
    spec:
      containers:
      - name: api-container
        image: node:20-alpine
        command: ["node", "server.js"]
        ports:
        - name: http-api
          containerPort: 3000
        env:
        - name: DB_HOST
          value: "postgres.production.svc.cluster.local"
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: token
        resources:
          requests:
            cpu: 200m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        # Startup probe handles slow-starting legacy apps
        startupProbe:
          httpGet:
            path: /healthz
            port: 3000
          failureThreshold: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /healthz
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 15
```

## Advanced Example
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-worker-advanced
  namespace: production
  labels:
    app: worker
    component: consumer
spec:
  replicas: 5
  # Seconds to wait for new Pod to be ready before marking it as progress stalled
  progressDeadlineSeconds: 600
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: worker
  template:
    metadata:
      labels:
        app: worker
    spec:
      # Topology placement constraints
      topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app: worker
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - worker
            topologyKey: kubernetes.io/hostname
      serviceAccountName: worker-service-account
      containers:
      - name: worker-app
        image: redis:7.2-alpine
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1024Mi
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 30 && redis-cli shutdown"]
        volumeMounts:
        - name: worker-storage
          mountPath: /data
      volumes:
      - name: worker-storage
        persistentVolumeClaim:
          claimName: worker-pvc-production

---

# StatefulSet

## Minimal Example
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web-statefulset-minimal
  namespace: default
spec:
  # DNS domain pattern linked to StatefulSet pods
  serviceName: "nginx-service"
  replicas: 2
  selector:
    matchLabels:
      app: nginx-stateful
  template:
    metadata:
      labels:
        app: nginx-stateful
    spec:
      containers:
      - name: nginx
        image: nginx:1.25.3
        ports:
        - containerPort: 80
```

## Production Example
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: cache-cluster
  namespace: database
  labels:
    app: redis-cluster
spec:
  serviceName: "redis-hs"
  replicas: 3
  # Parallel vs OrderedReady pod lifecycle management
  podManagementPolicy: OrderedReady
  updateStrategy:
    type: RollingUpdate
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
      - name: redis
        image: redis:7.2-alpine
        command: ["redis-server", "--appendonly", "yes"]
        ports:
        - name: db-port
          containerPort: 6379
        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
        volumeMounts:
        - name: redis-data
          mountPath: /data
  # PVC definitions dynamically generated for each StatefulSet Pod
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "local-path"
      resources:
        requests:
          storage: 10Gi
```

## Advanced Example
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: elasticsearch-ha
  namespace: database
  labels:
    app: elasticsearch
spec:
  serviceName: "elasticsearch-headless"
  replicas: 3
  # Updates will only roll out to index greater than or equal to partition
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0
  podManagementPolicy: Parallel
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - elasticsearch
            topologyKey: kubernetes.io/hostname
      # Non-privileged initialization to configure host file system limits
      initContainers:
      - name: sysctl-setup
        image: busybox:1.36.1
        command: ["sysctl", "-w", "vm.max_map_count=262144"]
        securityContext:
          privileged: true
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
          limits:
            cpu: 100m
            memory: 128Mi
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:8.11.1
        env:
        - name: cluster.name
          value: "k8s-logs"
        - name: discovery.seed_hosts
          value: "elasticsearch-headless"
        - name: cluster.initial_master_nodes
          value: "elasticsearch-ha-0,elasticsearch-ha-1,elasticsearch-ha-2"
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        ports:
        - name: http
          containerPort: 9200
        - name: transport
          containerPort: 9300
        volumeMounts:
        - name: es-data
          mountPath: /usr/share/elasticsearch/data
  volumeClaimTemplates:
  - metadata:
      name: es-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "local-path"
      resources:
        requests:
          storage: 50Gi

---

# DaemonSet

## Minimal Example
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter-minimal
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: node-exporter-min
  template:
    metadata:
      labels:
        app: node-exporter-min
    spec:
      containers:
      - name: node-exporter
        image: prom/node-exporter:v1.7.0
```

## Production Example
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: prom-node-exporter
  namespace: monitoring
  labels:
    app: node-exporter
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      # Ensures the DaemonSet runs on control plane and worker nodes alike
      tolerations:
      - operator: Exists
        effect: NoSchedule
      - operator: Exists
        effect: NoExecute
      # Allows sharing host namespaces to gather host system metrics
      hostNetwork: true
      hostPID: true
      containers:
      - name: node-exporter
        image: prom/node-exporter:v1.7.0
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
        ports:
        - name: metrics
          containerPort: 9100
          hostPort: 9100
        volumeMounts:
        - name: rootfs
          mountPath: /host/root
          readOnly: true
      volumes:
      - name: rootfs
        hostPath:
          path: /

---

# Job

## Minimal Example
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: batch-job-minimal
  namespace: default
spec:
  template:
    spec:
      containers:
      - name: compute-pi
        image: perl:5.38
        command: ["perl", "-Mbignum=bpi", "-wle", "print bpi(100)"]
      # Jobs must have a RestartPolicy of Never or OnFailure
      restartPolicy: Never
```

## Production Example
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-migrator-production
  namespace: production
  labels:
    app: migrator
spec:
  # Max retries before marking the job as failed
  backoffLimit: 4
  # Absolute deadline (seconds) before terminating the job
  activeDeadlineSeconds: 1800
  # Keep job record in cluster for 2 hours after completion
  ttlSecondsAfterFinished: 7200
  template:
    metadata:
      labels:
        app: migrator
    spec:
      restartPolicy: OnFailure
      containers:
      - name: migrator-task
        image: postgres:15-alpine
        command: ["psql", "-h", "postgres", "-U", "postgres", "-d", "prod", "-c", "REINDEX TABLE logs;"]
        env:
        - name: PGPASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1024Mi
```

## Advanced Example
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-image-processor
  namespace: production
spec:
  # Run 3 pods concurrently
  parallelism: 3
  # Entire job complete after 6 successful pod completions
  completions: 6
  backoffLimit: 3
  activeDeadlineSeconds: 3600
  # Ensures pods receive unique ordered index labels (0 to 5)
  completionMode: Indexed
  suspend: false
  template:
    metadata:
      labels:
        app: image-processing
    spec:
      restartPolicy: OnFailure
      containers:
      - name: processor
        image: python:3.11-alpine
        command: ["python", "-c", "import os; print(f'Processing index {os.environ.get(\"JOB_COMPLETION_INDEX\")}')"]
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi

---

# CronJob

## Minimal Example
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: periodic-cleanup-minimal
  namespace: default
spec:
  # Executed every minute
  schedule: "* * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: clean-logs
            image: busybox:1.36.1
            command: ["echo", "cleaned up"]
          restartPolicy: OnFailure
```

## Production Example
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup-cronjob
  namespace: production
spec:
  # Executed daily at midnight
  schedule: "0 0 * * *"
  # Deadline in seconds for starting the job if it misses scheduled time
  startingDeadlineSeconds: 200
  # Concurrency controls: Allow, Forbid, Replace
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: pg-dump
            image: postgres:15-alpine
            command: ["pg_dump", "-h", "postgres-service", "-U", "admin", "-F", "c", "-b", "-v", "-f", "/backup/db_backup.dump", "prod_db"]
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: password
            resources:
              requests:
                cpu: 500m
                memory: 512Mi
              limits:
                cpu: 1000m
                memory: 1024Mi
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc-production
```

## Advanced Example
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: system-health-reporter
  namespace: system-monitoring
spec:
  # Executed every Sunday at 3 AM
  schedule: "0 3 * * 0"
  timeZone: "America/New_York"
  concurrencyPolicy: Forbid
  startingDeadlineSeconds: 120
  suspend: false
  successfulJobsHistoryLimit: 1
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      activeDeadlineSeconds: 1200
      template:
        spec:
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
          restartPolicy: Never
          containers:
          - name: reporter-agent
            image: curlimages/curl:8.4.0
            command: ["curl", "-X", "POST", "-d", "{\"status\":\"healthy\"}", "https://api.uptime.com/ping"]
            resources:
              requests:
                cpu: 100m
                memory: 64Mi
              limits:
                cpu: 200m
                memory: 128Mi

---

# Service

## Minimal Example
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service-minimal
  namespace: default
spec:
  # Defaults to ClusterIP
  type: ClusterIP
  selector:
    app: web-server
  ports:
  - port: 80
    targetPort: 80
```

## Production Example
```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service-production
  namespace: production
  labels:
    app: backend-api
    tier: service
spec:
  type: ClusterIP
  # Session affinity based on client IP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
  selector:
    app: backend-api
  ports:
  - name: http-api
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: https-api
    port: 443
    targetPort: 8443
    protocol: TCP
```

## Advanced Example
```yaml
apiVersion: v1
kind: Service
metadata:
  name: database-headless-service
  namespace: database
spec:
  # Headless service configuration (ClusterIP set to None)
  clusterIP: None
  # Publish services address even if pod is not ready
  publishNotReadyAddresses: true
  selector:
    app: cluster-db
  ports:
  - name: db-replication
    port: 5432
    targetPort: 5432
```

---

# Ingress

## Minimal Example
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minimal-ingress
  namespace: default
spec:
  rules:
  - host: app.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service-minimal
            port:
              number: 80
```

## Production Example
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress-production
  namespace: production
  annotations:
    # Cert-manager automatic certificate provisioning annotation
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    # Target Ingress Controller
    kubernetes.io/ingress.class: "nginx"
    # Enable SSL Redirects
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  # Secret name containing TLS private key and certificate
  tls:
  - hosts:
    - api.company.com
    secretName: company-tls-cert
  rules:
  - host: api.company.com
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: api-service-production
            port:
              number: 80
```

## Advanced Example
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: advanced-traefik-ingress
  namespace: production
  annotations:
    # Traefik routing configuration / rewrite annotation
    traefik.ingress.kubernetes.io/router.middlewares: "production-ip-whitelist@kubernetescrd"
    # Custom rate-limiting annotations
    nginx.ingress.kubernetes.io/limit-connections: "20"
    nginx.ingress.kubernetes.io/limit-rps: "10"
spec:
  ingressClassName: traefik
  tls:
  - hosts:
    - dashboard.company.com
    secretName: wildcard-tls
  rules:
  - host: dashboard.company.com
    http:
      paths:
      - path: /admin
        pathType: Exact
        backend:
          service:
            name: admin-console-service
            port:
              number: 8080
      - path: /assets
        pathType: Prefix
        backend:
          service:
            name: asset-service
            port:
              number: 9000

---

# NetworkPolicy

## Minimal Example
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: default
spec:
  # Pod selector evaluates to all pods in the namespace
  podSelector: {}
  # Restricts both incoming and outgoing traffic
  policyTypes:
  - Ingress
  - Egress
```

## Production Example
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend-api
  policyTypes:
  - Ingress
  ingress:
  # Allow traffic only from FrontEnd Pods in the same namespace
  - from:
    - podSelector:
        matchLabels:
          app: frontend-ui
    ports:
    - protocol: TCP
      port: 8080
```

## Advanced Example
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: granular-egress-ingress-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: database-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    # Cross-namespace selector matching label in tenant namespaces
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: billing
      podSelector:
        matchLabels:
          app: billing-processor
    ports:
    - protocol: TCP
      port: 5432
  egress:
  # Allow egress traffic only to specific external IP blocks and standard DNS port
  - to:
    - ipBlock:
        cidr: 192.168.1.0/24
        except:
        - 192.168.1.50/32
    ports:
    - protocol: TCP
      port: 80
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53

---

# PersistentVolume

## Minimal Example
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: hostpath-pv-minimal
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  # Mount path directly on host machine (for local testing/k3s)
  hostPath:
    path: "/data/volume-minimal"
```

## Production Example
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv-production
  labels:
    volume-type: shared-assets
spec:
  capacity:
    storage: 100Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  # Reclaim policies: Retain, Recycle, Delete
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual-nfs
  mountOptions:
    - hard
    - nfsvers=4.1
  # NFS network server configurations
  nfs:
    path: /exports/assets
    server: 192.168.1.25
```

## Advanced Example
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-nvme-pv-advanced
spec:
  capacity:
    storage: 500Gi
  volumeMode: Block
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  storageClassName: local-nvme
  local:
    path: /mnt/disks/ssd1
  # Pin local PV to a specific cluster node
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - worker-node-01

---

# PersistentVolumeClaim

## Minimal Example
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: web-pvc-minimal
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

## Production Example
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc-production
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  # Link PVC to specific StorageClass
  storageClassName: local-path
  resources:
    requests:
      storage: 20Gi
```

## Advanced Example
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: analytics-pvc-advanced
  namespace: production
spec:
  accessModes:
    - ReadWriteMany
  volumeMode: Block
  storageClassName: premium-rwo
  resources:
    requests:
      storage: 200Gi
  # Filter which persistent volumes qualify using label selectors
  selector:
    matchLabels:
      tier: analytics-backend
```

---

# StorageClass

## Minimal Example
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage-minimal
# Provisioner for local filesystem mapping
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
```

## Production Example
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: production-ebs-sc
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
# Reclaim volumes automatically when PVC is deleted
reclaimPolicy: Delete
# Allow volume size modification post-creation
allowVolumeExpansion: true
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
```

## Advanced Example
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: highly-advanced-local-path
provisioner: rancher.io/local-path
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Retain
allowVolumeExpansion: true
# Standard host mount configurations
mountOptions:
  - debug
  - noatime
parameters:
  # Path configured inside the Rancher k3s host node environment
  configFile: '{"nodePathMap":[{"node":"DEFAULT_PATH_FOR_NON_LISTED_NODES","paths":["/opt/local-path-provisioner"]}]}'
```

---

# ConfigMap

## Minimal Example
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config-minimal
  namespace: default
data:
  # Simple literal key-value pairs
  database_name: "users_db"
  app_port: "8080"
```

## Production Example
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: application-config-production
  namespace: production
  labels:
    app: payment-api
data:
  # Multi-line config file contents mapped directly inside data block
  application.properties: |
    server.port=8080
    spring.datasource.url=jdbc:postgresql://postgres.production.svc.cluster.local:5432/finance
    spring.datasource.username=finance_app
    logging.level.org.springframework=WARN
  features.json: |
    {
      "enable_new_gateway": true,
      "max_retry_limit": 5
    }
```

## Advanced Example
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-conf-advanced
  namespace: production
  annotations:
    config-version: "1.4.0"
# Binary Data fields can host non-utf-8 binary contents
binaryData:
  favicon.ico: iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAMUlEQVR42mNk+M9QDwADGIECEBfX0vAAAAAElFTkSuQmCC
data:
  nginx.conf: |
    user  nginx;
    worker_processes  auto;
    error_log  /var/log/nginx/error.log notice;
    pid        /var/run/nginx.pid;
    events {
        worker_connections  1024;
    }
    http {
        include       /etc/nginx/mime.types;
        default_type  application/octet-stream;
        sendfile        on;
        keepalive_timeout  65;
        server {
            listen       80;
            server_name  localhost;
            location / {
                root   /usr/share/nginx/html;
                index  index.html index.htm;
            }
        }
    }
```

---

# Secret

## Minimal Example
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secret-minimal
  namespace: default
# Opaque is default type for raw strings encoded to base64
type: Opaque
data:
  # Value: "admin" encoded to base64
  db-user: YWRtaW4=
  # Value: "supersecret" encoded to base64
  db-pass: c3VwZXJzZWNyZXQ=
```

## Production Example
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secure-tls-secret
  namespace: production
# Predefined type for SSL/TLS private key and certificate
type: kubernetes.io/tls
data:
  # Base64 encoded public certificate contents
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCg==
  # Base64 encoded private key contents
  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCg==
```

## Advanced Example
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: private-registry-secret
  namespace: production
# Secret type specifically used for storing private docker configuration logins
type: kubernetes.io/dockerconfigjson
data:
  # Base64 representation of a complete docker config JSON configuration
  .dockerconfigjson: eyJhdXRocyI6eyJndHIuaW8iOnsidXNlcm5hbWUiOiJzdmMtY2xpIiwicGFzc3dvcmQiOiJQYXNzMTIzIiwiZW1haWwiOiJzdmNAY28uY29tIiwiYXV0aCI6ImMzWmpaRzl0YVhNZmNHRnpjM2R2Y21RPSJ9fX0=
```

---

# ServiceAccount

## Minimal Example
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: service-account-minimal
  namespace: default
```

## Production Example
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: aws-iam-sa-production
  namespace: production
  annotations:
    # Integration annotation for AWS IAM Roles for Service Accounts (IRSA)
    eks.amazonaws.com/role-arn: "arn:aws:iam::123456789012:role/k8s-s3-access-role"
# Prevent pod from automatically mounting current SA token to mount point
automountServiceAccountToken: true
```

## Advanced Example
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: custom-sa-advanced
  namespace: production
automountServiceAccountToken: false
# Specify secrets used globally to pull images using this SA
imagePullSecrets:
- name: private-registry-secret
```

---

# Role

## Minimal Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader-minimal
  namespace: default
rules:
  # Empty API group matches Core group
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

## Production Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-developer-role
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "persistentvolumeclaims"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets"]
  verbs: ["get", "list", "watch", "create", "update", "patch"]
```

## Advanced Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: restricted-config-updater
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  # Scope role capabilities to a specific configmap by name
  resourceNames: ["app-config-minimal"]
  verbs: ["get", "update", "patch"]
```

---

# RoleBinding

## Minimal Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods-minimal-binding
  namespace: default
# Map user directly to designated role
subjects:
- kind: User
  name: "alice@company.com"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader-minimal
  apiGroup: rbac.authorization.k8s.io
```

## Production Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-developer-binding
  namespace: production
subjects:
# Assigning local service accounts
- kind: ServiceAccount
  name: aws-iam-sa-production
  namespace: production
# Assigning entire team group mapped in IDP configuration
- kind: Group
  name: "oidc:dev-group"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: app-developer-role
  apiGroup: rbac.authorization.k8s.io
```

## Advanced Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: system-admin-binding
  namespace: system-monitoring
subjects:
- kind: ServiceAccount
  name: custom-sa-advanced
  namespace: production
roleRef:
  # Linking namespace level role binding directly to cluster-wide clusterRole
  kind: ClusterRole
  name: admin
  apiGroup: rbac.authorization.k8s.io
```

---

# ClusterRole

## Minimal Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-node-reader-minimal
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list"]
```

## Production Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: persistent-volume-manager
rules:
- apiGroups: [""]
  resources: ["persistentvolumes", "namespaces"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["storage.k8s.io"]
  resources: ["storageclasses"]
  verbs: ["get", "list", "watch"]
```

## Advanced Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: custom-aggregated-monitor
# Role aggregation rules using label selector combinations
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.monitoring.io/aggregate-to-monitoring: "true"
rules: [] # Automatically populated by control plane
```

---

# ClusterRoleBinding

## Minimal Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-node-reader-binding
subjects:
- kind: User
  name: "bob@company.com"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-node-reader-minimal
  apiGroup: rbac.authorization.k8s.io
```

## Production Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: pv-manager-global-binding
subjects:
- kind: Group
  name: "oidc:storage-admins"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: persistent-volume-manager
  apiGroup: rbac.authorization.k8s.io
```

## Advanced Example
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-admin-global-binding
subjects:
- kind: ServiceAccount
  name: default
  namespace: kube-system
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

---

# HorizontalPodAutoscaler

## Minimal Example
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hpa-minimal
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment-minimal
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
```

## Production Example
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa-production
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-api-production
  minReplicas: 2
  maxReplicas: 10
  metrics:
  # Monitor average cpu utilization
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
  # Monitor average memory utilization
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 350Mi
```

## Advanced Example
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: advanced-ingress-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-api-production
  minReplicas: 3
  maxReplicas: 15
  # Precision tuning of scaling behaviors and cooldown windows
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
      selectPolicy: Min
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

---

# VerticalPodAutoscaler

## Minimal Example
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vpa-minimal
  namespace: default
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment-minimal
  # Recommender computes metrics but doesn't apply updates automatically
  updatePolicy:
    updateMode: "Off"
```

## Production Example
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-vpa-production
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-api-production
  updatePolicy:
    # VPA recreates pods to automatically apply adjusted resource requirements
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: "api-container"
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 1000m
        memory: 1024Mi
      controlledResources: ["cpu", "memory"]
```

## Advanced Example
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: database-vpa-advanced
  namespace: database
spec:
  targetRef:
    apiVersion: apps/v1
    kind: StatefulSet
    name: cache-cluster
  updatePolicy:
    updateMode: "Initial"
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      # Ensure scaling is restricted only to Memory scaling requirements
      controlledResources: ["memory"]
      minAllowed:
        memory: 256Mi
      maxAllowed:
        memory: 4Gi
      # Suppress resource calculation limits on specific application sidecars
    - containerName: "redis"
      mode: "Auto"
```

---

# PriorityClass

## Minimal Example
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: low-priority-minimal
value: 1000
# Not a default priority allocation
globalDefault: false
```

## Production Example
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority-production
value: 1000000
globalDefault: false
description: "High priority class assigned to production APIs and databases."
# Preemption policy options: PreemptLowerPriority, Never
preemptionPolicy: PreemptLowerPriority
```

## Advanced Example
```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: critical-non-preemptive-advanced
# Maximum value for custom non-system priorities
value: 99999999
globalDefault: false
# Protect workloads but prevent evicting existing pods
preemptionPolicy: Never
description: "Workload priority that schedules ahead of others without terminating running pods."
```

---

# PodDisruptionBudget

## Minimal Example
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: pdb-minimal
  namespace: default
spec:
  # Guarantee at least 1 replica remains online during voluntary disruptions
  minAvailable: 1
  selector:
    matchLabels:
      app: nginx-min
```

## Production Example
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb-production
  namespace: production
spec:
  # Define constraint using maximum concurrent offline pods
  maxUnavailable: 1
  selector:
    matchLabels:
      app: web-api
```

## Advanced Example
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: worker-pdb-advanced
  namespace: production
spec:
  # Dynamic configuration using percentage targets
  minAvailable: 75%
  selector:
    matchLabels:
      app: worker
```

---

# HelmChart

## Minimal Example
```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: redis-helm-minimal
  namespace: kube-system
spec:
  chart: redis
  # Standard Helm Chart repository source URL
  repo: https://charts.bitnami.com/bitnami
  targetNamespace: default
```

## Production Example
```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: cert-manager-production
  namespace: kube-system
spec:
  chart: cert-manager
  version: v1.13.2
  repo: https://charts.jetstack.io
  targetNamespace: cert-manager
  # Create namespace if it does not exist
  createNamespace: true
  # Map configurations directly into chart's values system
  valuesContent: |
    installCRDs: true
    replicaCount: 2
    resources:
      limits:
        cpu: 200m
        memory: 256Mi
      requests:
        cpu: 100m
        memory: 128Mi
```

## Advanced Example
```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: prometheus-stack-advanced
  namespace: kube-system
spec:
  chart: kube-prometheus-stack
  version: 51.5.0
  repo: https://prometheus-community.github.io/helm-charts
  targetNamespace: monitoring
  createNamespace: true
  bootstrap: false
  # Inline parameters can override or append to yaml settings
  set:
    prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.storageClassName: "local-path"
  valuesContent: |
    grafana:
      enabled: true
      adminPassword: "StrongAdminPasswordExample"
      persistence:
        enabled: true
        storageClassName: "local-path"
        size: 10Gi
    prometheusOperator:
      resources:
        limits:
          cpu: 500m
          memory: 512Mi
        requests:
          cpu: 200m
          memory: 256Mi
```

---

# HelmChartConfig

## Minimal Example
```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: rke2-ingress-nginx
  # Namespace must match original HelmChart deployment namespace
  namespace: helm-system
spec:
  valuesContent: |
    controller:
      replicaCount: 2
```

## Production Example
```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  # Extends or overrides original Traefik k3s defaults
  valuesContent: |
    additionalArguments:
      - "--providers.kubernetesingress.ingressclass=traefik"
      - "--log.level=INFO"
    ports:
      websecure:
        tls:
          enabled: true
```

## Advanced Example
```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChartConfig
metadata:
  name: traefik
  namespace: kube-system
spec:
  valuesContent: |
    globalArguments:
      - "--global.checknewversion=false"
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "300m"
        memory: "256Mi"
    service:
      spec:
        externalTrafficPolicy: Local
    logs:
      general:
        level: WARN
      access:
        enabled: true
        fields:
          headers:
            names:
              User-Agent: keep
```

---

# ServiceMonitor

## Minimal Example
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: minimal-servicemonitor
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: web-server
  endpoints:
  - port: metrics
```

## Production Example
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: api-servicemonitor-production
  namespace: monitoring
  labels:
    # Essential release label for Prometheus Operator detection
    release: prometheus-stack
spec:
  selector:
    matchLabels:
      app: backend-api
  # Restricts discovery scan targets to specific namespace scopes
  namespaceSelector:
    matchNames:
    - production
  endpoints:
  - port: http-api
    path: /metrics
    interval: 15s
    scrapeTimeout: 10s
```

## Advanced Example
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: advanced-gateway-monitor
  namespace: monitoring
  labels:
    release: prometheus-stack
spec:
  selector:
    matchLabels:
      app: backend-api
  namespaceSelector:
    any: true
  endpoints:
  - port: https-api
    path: /actuator/prometheus
    scheme: https
    interval: 10s
    scrapeTimeout: 5s
    tlsConfig:
      insecureSkipVerify: true
    # Granular Prometheus relabeling execution targets
    metricRelabelings:
    - sourceLabels: [__name__]
      regex: "(jvm_memory_used_bytes|http_server_requests_seconds_count)"
      action: keep
```

---

# PodMonitor

## Minimal Example
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: minimal-podmonitor
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: worker
  podMetricsEndpoints:
  - port: metrics
```

## Production Example
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: sidecar-podmonitor-production
  namespace: monitoring
  labels:
    release: prometheus-stack
spec:
  selector:
    matchLabels:
      app: worker
  namespaceSelector:
    matchNames:
    - production
  podMetricsEndpoints:
  - port: http-port
    path: /metrics
    interval: 30s
    scrapeTimeout: 15s
```

## Advanced Example
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: multi-port-podmonitor-advanced
  namespace: monitoring
  labels:
    release: prometheus-stack
spec:
  selector:
    matchLabels:
      tier: analytics-backend
  namespaceSelector:
    any: true
  podMetricsEndpoints:
  - port: http-port
    path: /metrics/app
    interval: 15s
  - port: sidecar-logger
    path: /metrics/sidecar
    interval: 60s
    metricRelabelings:
    - sourceLabels: [status]
      regex: "404"
      action: drop
```

---

# ResourceQuota

## Minimal Example
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: quota-minimal
  namespace: default
spec:
  hard:
    # Limit maximum concurrent pods in this namespace
    pods: "10"
```

## Production Example
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-resource-quota
  namespace: production
spec:
  hard:
    # Total sum of cpu requests across all containers
    requests.cpu: "4"
    # Total sum of memory requests across all containers
    requests.memory: "8Gi"
    # Total sum of cpu limits across all containers
    limits.cpu: "8"
    # Total sum of memory limits across all containers
    limits.memory: "16Gi"
    # Storage and volume limits
    requests.storage: "100Gi"
    persistentvolumeclaims: "10"
    services: "15"
    configmaps: "30"
    secrets: "50"
```

## Advanced Example
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: advanced-scoped-quota
  namespace: production
spec:
  # Restrict quota application using scoping vectors
  scopes:
  - NotTerminating
  hard:
    requests.cpu: "8"
    requests.memory: "16Gi"
    limits.cpu: "16"
    limits.memory: "32Gi"
```

---

# LimitRange

## Minimal Example
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: limit-range-minimal
  namespace: default
spec:
  limits:
  - type: Container
    default:
      cpu: 200m
      memory: 256Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
```

## Production Example
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: limit-range-production
  namespace: production
spec:
  limits:
  # Enforced bounds configuration for Containers
  - type: Container
    # Implicit assignment if limits are omitted
    default:
      cpu: 500m
      memory: 512Mi
    # Implicit assignment if requests are omitted
    defaultRequest:
      cpu: 250m
      memory: 256Mi
    # Minimum absolute sizing container can request
    min:
      cpu: 100m
      memory: 128Mi
    # Maximum absolute sizing container can request
    max:
      cpu: 2000m
      memory: 2Gi
```

## Advanced Example
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: advanced-comprehensive-limits
  namespace: production
spec:
  limits:
  - type: Container
    default:
      cpu: 1000m
      memory: 1Gi
    defaultRequest:
      cpu: 500m
      memory: 512Mi
    min:
      cpu: 50m
      memory: 64Mi
    max:
      cpu: 4000m
      memory: 8Gi
    # Ratio constraint between limit and request
    maxLimitRequestRatio:
      cpu: 4
      memory: 2
  # Enforced sizing limits for PVC requests
  - type: PersistentVolumeClaim
    min:
      storage: 5Gi
    max:
      storage: 100Gi
```

---

# CustomResourceDefinition

## Minimal Example
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: backuptasks.stable.example.com
spec:
  group: stable.example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                destination:
                  type: string
  scope: Namespaced
  names:
    plural: backuptasks
    singular: backuptask
    kind: BackupTask
    shortNames:
    - bt
```

## Production Example
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: crontabs.stable.example.com
spec:
  group: stable.example.com
  versions:
  - name: v1
    served: true
    storage: true
    # Schema validation engine definition
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            required: ["cronSpec", "image"]
            properties:
              cronSpec:
                type: string
                pattern: '^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/[0-9]+)(\s+(\*|([0-9]|1[0-9]|2[0-3])|\*\/[0-9]+)){4}$'
              image:
                type: string
              replicas:
                type: integer
                minimum: 1
                maximum: 10
  scope: Namespaced
  names:
    plural: crontabs
    singular: crontab
    kind: CronTab
    shortNames:
    - ct
```

## Advanced Example
```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: apps.stable.example.com
spec:
  group: stable.example.com
  versions:
  - name: v1
    served: true
    storage: true
    # Define subresources to enable /status modifications independently
    subresources:
      status: {}
      scale:
        specReplicasPath: .spec.replicas
        statusReplicasPath: .status.replicas
        labelSelectorPath: .status.labelSelector
    # Enable printing additional informational columns inside kubectl get outputs
    additionalPrinterColumns:
    - name: Replicas
      type: integer
      jsonPath: .spec.replicas
    - name: Age
      type: date
      jsonPath: .metadata.creationTimestamp
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              replicas:
                type: integer
              image:
                type: string
          status:
            type: object
            properties:
              replicas:
                type: integer
              labelSelector:
                type: string
  scope: Namespaced
  names:
    plural: apps
    singular: app
    kind: CustomApp
    shortNames:
    - ca
