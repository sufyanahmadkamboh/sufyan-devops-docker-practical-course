<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 138 · From Docker to Kubernetes · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Inside the kind node, Kubernetes uses **containerd** (lesson 004), not the Docker engine. List the containers
running inside the node with containerd's client `crictl`, and find the Kubernetes API server among them.

## Solution

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
