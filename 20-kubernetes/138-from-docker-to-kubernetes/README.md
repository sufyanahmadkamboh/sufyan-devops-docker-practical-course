# Lesson 138 · From Docker to Kubernetes

> Level 21 · Docker and Kubernetes · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

Docker runs containers on one machine, when you tell it to. **Kubernetes** runs the same images on a cluster of
machines and keeps them running: you describe the desired state in YAML ("two copies of `go-api:1.0`, 64 MiB each,
reachable as `go-api`"), and Kubernetes creates, restarts, replaces and spreads the containers to match. Almost every
`docker run` option you learned has a direct equivalent in a Kubernetes manifest. This lesson maps them, and creates a
local cluster with **kind** (Kubernetes in Docker), whose "machines" are Docker containers.

## Visual

```text
 docker run -d --name go-api -p 8080:8080 -e PORT=8080 --memory 64m --cpus 0.25 --restart always go-api:1.0

 Deployment "go-api"                  ← --name (and how many copies: replicas)
 └─ Pod template
    └─ container
       ├─ image: go-api:1.0           ← the image, unchanged
       ├─ env: PORT=8080              ← -e
       ├─ ports: containerPort 8080   ← EXPOSE (documentation, like in Docker)
       ├─ resources.limits            ← --memory, --cpus
       └─ readinessProbe              ← HEALTHCHECK
 Service "go-api" port 80 → 8080      ← a user-defined network alias + load balancing (not -p)
 restartPolicy: Always (default)      ← --restart always

 kind cluster: each Kubernetes "node" is a Docker container running kubelet + containerd
 ┌──────────────── Docker ────────────────┐
 │ container docker-course-control-plane  │──▶ Pods (run by containerd inside it)
 └────────────────────────────────────────┘
```

| `docker run` | Kubernetes (Pod spec) |
|---|---|
| image `go-api:1.0` | `containers[].image` |
| `--name` | `metadata.name` (Pods get generated names) |
| `-e NAME=value`, `--env-file` | `env`, `envFrom` (ConfigMap, Secret) |
| `-p 8080:8080` | a `Service` (and `kubectl port-forward` for testing) |
| `-v volume:/path` | `volumes` + `volumeMounts` (PersistentVolumeClaim) |
| `--memory`, `--cpus` | `resources.limits.memory`, `resources.limits.cpu` |
| `HEALTHCHECK` | `readinessProbe`, `livenessProbe` |
| `--user`, `--read-only`, `--cap-drop` | `securityContext` |
| `--restart` | `restartPolicy` (Deployments: always) |

## Lab setup

`kind` and `kubectl` must be installed: see <https://kind.sigs.k8s.io/docs/user/quick-start/#installation> and
<https://kubernetes.io/docs/tasks/tools/>. Check them:

<!-- test: contains=kind v; contains=Client Version -->
```bash
kind version
kubectl version --client
```

## Demonstration

`kubectl` can write a manifest for you without a cluster (`--dry-run=client`). Ask for the Kubernetes version of a
`docker run` of the Go API:

<!-- test: contains=image: go-api:1.0; output -->
```bash
kubectl create deployment go-api --image=go-api:1.0 --port=8080 --replicas=2 --dry-run=client -o yaml
```

```text
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: go-api
  name: go-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: go-api
  strategy: {}
  template:
    metadata:
      labels:
        app: go-api
    spec:
      containers:
      - image: go-api:1.0
        name: go-api
        ports:
        - containerPort: 8080
        resources: {}
status: {}
```

Read it against the table above: `replicas: 2` (two containers, where Docker would need two `docker run`),
`image: go-api:1.0`, `containerPort: 8080`. The `selector` and `labels` connect the Deployment to its Pods; a Service
uses the same labels to find them.

## Command breakdown

| Command | What it does |
|---|---|
| `kubectl create deployment … --dry-run=client -o yaml` | print a manifest instead of creating anything |
| `kind create cluster --name NAME` | start a local cluster in Docker containers, and write its kubeconfig |
| `kubectl get nodes` | the cluster's machines and whether they are `Ready` |
| `kind delete cluster --name NAME` | remove the cluster and its containers |

## Hands-on lab

**Instructions.** Generate the manifest of a **Service** that gives the Pods of `go-api` one stable address on port
80, forwarding to the container port 8080 (the Kubernetes equivalent of a network alias, lesson 050).

**Expected result.** A `kind: Service` with `port: 80` and `targetPort: 8080`.

**Verification.**

<!-- test: contains=kind: Service; contains=targetPort: 8080 -->
```bash
kubectl create service clusterip go-api --tcp=80:8080 --dry-run=client -o yaml
```

## Break it

There is no cluster yet. Ask for its nodes:

<!-- test: fail; anyof=connection to the server||Unable to connect to the server||no configuration has been provided; output -->
```bash
kubectl get nodes 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
Unable to connect to the server: dial tcp [::1]:8080: connectex: No connection could be made because the target machine actively refused it.
```

(`tail -1` keeps the summary: depending on the version, `kubectl` first repeats the same error a few times.)

## Troubleshoot it

`kubectl` is only a client, like `docker` (lesson 004). It reads the cluster address and credentials from its
**kubeconfig** (`~/.kube/config`, or the file in `KUBECONFIG`). With no cluster configured, it falls back to
`localhost:8080`, where nothing listens. Check which contexts (cluster + user) exist:

<!-- test: contains=CURRENT; output -->
```bash
kubectl config get-contexts
```

```text
CURRENT   NAME   CLUSTER   AUTHINFO   NAMESPACE
```

None: the same situation as `docker` with a wrong `DOCKER_HOST`.

## Fix it

Create a cluster. kind starts a Docker container that runs a complete Kubernetes node, then writes a context
`kind-docker-course` into the kubeconfig (this takes about a minute the first time):

<!-- test: timeout=300; contains=Ready -->
```bash
kind create cluster --name docker-course --wait 120s
kubectl get nodes
```

The node is a container like any other:

<!-- test: contains=docker-course-control-plane; output -->
```bash
docker ps --filter name=docker-course --format '{{.Names}}  {{.Image}}  {{.Status}}'
kubectl config current-context
```

```text
docker-course-control-plane  kindest/node:v1.37.0  Up 33 seconds
kind-docker-course
```

## Practice challenge

Inside the kind node, Kubernetes uses **containerd** (lesson 004), not the Docker engine. List the containers
running inside the node with containerd's client `crictl`, and find the Kubernetes API server among them.

<details>
<summary>Solution</summary>

<!-- test: contains=kube-apiserver; output=head:4 -->
```bash
docker exec docker-course-control-plane crictl ps --name kube --output table
```

```text
CONTAINER           IMAGE               CREATED             STATE               NAME                      ATTEMPT             POD ID              POD                                                   NAMESPACE
bad6fa29d1eec       d6a28daf3e6b0       15 seconds ago      Running             kube-proxy                0                   252da07842f5e       kube-proxy-srl4x                                      kube-system
e660a01d6a13a       1fabf80a1273a       29 seconds ago      Running             kube-scheduler            0                   90059583573aa       kube-scheduler-docker-course-control-plane            kube-system
d2dd0863757ad       364b3c3d9ec19       29 seconds ago      Running             kube-controller-manager   0                   cebac243bf845       kube-controller-manager-docker-course-control-plane   kube-system
...
```

The images you build with Docker run unchanged on containerd because both follow the OCI image format. Kubernetes
dropped its built-in Docker support in 2022 (v1.24), and Docker-built images kept working everywhere.

</details>

## Real-world example

A team runs its services with Docker Compose on one server. When they move to a managed Kubernetes cluster (EKS, GKE,
AKS), the images stay exactly the same: the same CI pipeline pushes them to the same registry. What changes is the
description: each Compose service becomes a Deployment and a Service, `environment:` becomes a ConfigMap and Secrets,
volumes become PersistentVolumeClaims, and the healthchecks become probes. Developers keep using Docker and kind
locally to test the manifests before they reach the real cluster.

## Recap

- Kubernetes runs the same OCI images as Docker, on many machines, and keeps the desired state.
- `docker run` options map to Pod spec fields: image, env, ports, resources, probes, securityContext.
- `-p` has no direct equivalent: Services give Pods a stable address; `port-forward` is for testing.
- kind runs a whole cluster as Docker containers; `kubectl` reads its target from the kubeconfig.

## Cleanup

<!-- test: timeout=180 -->
```bash
kind delete cluster --name docker-course
```

Next: [Lesson 139 · Deploy an image to kind](../139-deploy-an-image-to-kind/README.md)
