<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 138 · From Docker to Kubernetes · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

There is no cluster yet. Ask for its nodes:

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

```bash
kind create cluster --name docker-course --wait 120s
kubectl get nodes
```

The node is a container like any other:

```bash
docker ps --filter name=docker-course --format '{{.Names}}  {{.Image}}  {{.Status}}'
kubectl config current-context
```

```text
docker-course-control-plane  kindest/node:v1.37.0  Up 33 seconds
kind-docker-course
```
