<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 140 · Kubernetes for Docker users · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

`docker run --memory 64m` sets a limit the container runtime enforces. Show the memory limit of a `go-api` Pod twice:
as written in the Pod spec, and in bytes as the container runtime (containerd in the kind node) applied it.

The solution is in [solution.md](solution.md).
