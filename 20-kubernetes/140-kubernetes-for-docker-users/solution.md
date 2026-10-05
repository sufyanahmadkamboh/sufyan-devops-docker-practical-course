<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 140 · Kubernetes for Docker users · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

`docker run --memory 64m` sets a limit the container runtime enforces. Show the memory limit of a `go-api` Pod twice:
as written in the Pod spec, and in bytes as the container runtime (containerd in the kind node) applied it.

## Solution

```bash
kubectl get pods -l app=go-api -o jsonpath='{.items[0].spec.containers[0].resources.limits.memory}' && echo
id=$(docker exec docker-course-control-plane crictl ps --name go-api -q | head -1)
docker exec docker-course-control-plane crictl inspect "$id" | grep -i '"memory_limit_in_bytes"\|"memoryLimitInBytes"' | head -1
```

```text
64Mi
          "memory_limit_in_bytes": 67108864,
```

`64Mi` = 64 × 1024 × 1024 = 67108864 bytes: the same cgroup memory limit Docker sets for `--memory 64m` (lesson 098).
Exceeding it gets the container killed with `OOMKilled`, in Kubernetes as in Docker.
