<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 139 · Deploy an image to kind · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Scale the Deployment to three copies (the Kubernetes way of running `docker run` three times) and
check that all three are ready and share the load.

**Expected result.** `deployment.apps/go-api scaled`, then three Pods that are `Running` and ready.

**Verification.**

```bash
kubectl scale deployment/go-api --replicas=3
kubectl rollout status deployment/go-api --timeout=120s > /dev/null
kubectl get deployment go-api -o custom-columns=NAME:.metadata.name,READY:.status.readyReplicas,WANTED:.spec.replicas --no-headers | awk '{print $1, $2 "/" $3}'
```
