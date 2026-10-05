<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 140 · Kubernetes for Docker users · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** The Go image is distroless: it has no shell, so `kubectl exec … -- sh` fails exactly like
`docker exec … sh` would (lesson 089). Prove it, then inspect the running container's environment variables from the
Pod specification instead.

**Expected result.** An error containing `executable file not found` (or `no such file`), then `PORT=8080`.

**Verification.**

```bash
kubectl exec deployment/go-api -- sh -c 'echo hi' 2>&1 || true
kubectl get deployment go-api -o jsonpath='{range .spec.template.spec.containers[0].env[*]}{.name}={.value}{"\n"}{end}'
```
