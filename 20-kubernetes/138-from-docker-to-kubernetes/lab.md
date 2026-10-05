<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 138 · From Docker to Kubernetes · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Generate the manifest of a **Service** that gives the Pods of `go-api` one stable address on port
80, forwarding to the container port 8080 (the Kubernetes equivalent of a network alias, lesson 050).

**Expected result.** A `kind: Service` with `port: 80` and `targetPort: 8080`.

**Verification.**

```bash
kubectl create service clusterip go-api --tcp=80:8080 --dry-run=client -o yaml
```
