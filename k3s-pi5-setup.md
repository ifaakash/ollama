# K3s Setup on Raspberry Pi 5 (`moo`)

## Target (Goal)
To document and understand the architecture, networking, and service exposure of a single-node k3s cluster running on a Raspberry Pi 5, paving the way for future expansions (hybrid cloud) and monitoring integrations.

## Summary
This document summarizes observations and learnings from exploring a local k3s cluster named `moo`. It covers cluster node management, the distinction between Node and Pod IPs, Container Network Interface (CNI) operations, Kubernetes Services (specifically NodePort), and internal DNS resolution. 

---

## 1. Cluster Architecture
- **Current Setup:** A single-node cluster running on a Raspberry Pi 5. The hostname is `moo`.
- **Role:** `moo` acts as both the **control-plane** (the brain) and a worker node.
- **Node vs. Cluster:** The cluster is managed via the `~/.kube/config` file. The command `kubectl get nodes` shows physical or virtual machines attached to the cluster.

### Future Expansion (Hybrid Cloud)
- **Adding Nodes:** You can add an external VM (like an AWS EC2 instance) to this local cluster. 
- **Requirement:** Since the Pi 5 is on a local home network and the AWS VM is in the cloud, a mesh VPN (like Tailscale or WireGuard) is required to securely bridge the networks so the AWS VM can join the `moo` control-plane as a worker node.

---

## 2. Networking and CNI (Flannel)
- **Node IP:** The physical IP address of the Pi 5 on the local home network (e.g., `192.168.x.x`).
- **Pod IP:** A virtual, private IP address (e.g., `10.42.x.x`) assigned by the CNI. These are strictly internal to the cluster.
- **The Bridge (`cni0`):** Exploring `ifconfig` reveals the `cni0` interface (e.g., `10.42.0.1`). This acts as the gateway for all pods on the node, routing traffic between the physical network and the virtual pod network.
- **Pod Visibility:** Without a Kubernetes Service, a pod can only be accessed from within the node itself (e.g., curling the Pod IP via SSH directly on the Pi 5). 

---

## 3. Services and DNS (How Pods Communicate)
Because Pod IPs are ephemeral (they change dynamically if a pod crashes/restarts), pods should communicate using **Services**.

### CoreDNS & Internal Resolution
- When a frontend pod needs to reach a backend pod, it calls the backend's Service name (e.g., `http://backend-svc:8080`).
- **CoreDNS** intercepts this internal DNS request. Its configuration (`kubernetes cluster.local` plugin) queries the Kubernetes API in real-time.
- CoreDNS resolves the Service name to a stable, internal `ClusterIP`.
- The node's `iptables` (firewall rules) intercept traffic headed to the `ClusterIP` and rewrite the destination to the current, live Pod IP.

### Exposing Pods via NodePort
To expose an application to the outside local network (e.g., a laptop on the same Wi-Fi), a `NodePort` service is used. 
It defines three distinct ports:
1. **`nodePort` (e.g., `32717`):** The port opened on the Pi 5's physical network interface. Accessed via `http://<PI5_IP>:32717`.
2. **`port` (e.g., `80`):** The internal port used by the Service itself. Other pods use this to communicate internally.
3. **`targetPort` (e.g., `80`):** The actual port the application container is listening on inside the Pod.

---

## 4. Monitoring and Metrics
- **Current State:** The cluster runs `metrics-server`, a lightweight internal tool that allows commands like `kubectl top pods` to function.
- **Next Steps (Visualization):** To visualize cluster health, resource usage, and network traffic, the standard approach is deploying the **kube-prometheus-stack** (via Helm). This installs Prometheus (for scraping metrics) and Grafana (for beautiful dashboards).

---

## 5. Helpful Troubleshooting Commands
When verifying network configurations on the host, standard user permissions often hide system-level container processes. Always use `sudo` to view ports managed by root processes like k3s:

- **List active k3s listening ports:**
  ```bash
  sudo ss -tulnp | grep "k3s"
  ```
- **Verify a specific NodePort is reserved by k3s:**
  ```bash
  sudo ss -tulnp | grep <NODE_PORT>
  ```
- **View actual traffic redirection rules (the CNI magic):**
  ```bash
  sudo iptables-save | grep <SERVICE_NAME_OR_PORT>
  ```
