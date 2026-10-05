<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 138 · From Docker to Kubernetes · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
kind version
kubectl version --client
```

## Demonstration

```bash
kubectl create deployment go-api --image=go-api:1.0 --port=8080 --replicas=2 --dry-run=client -o yaml
```

## Hands-on lab

```bash
kubectl create service clusterip go-api --tcp=80:8080 --dry-run=client -o yaml
```

## Break it

```bash
kubectl get nodes 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
kubectl config get-contexts
```

## Fix it

```bash
kind create cluster --name docker-course --wait 120s
kubectl get nodes
```

```bash
docker ps --filter name=docker-course --format '{{.Names}}  {{.Image}}  {{.Status}}'
kubectl config current-context
```

## Practice challenge

```bash
docker exec docker-course-control-plane crictl ps --name kube --output table
```

## Cleanup

```bash
kind delete cluster --name docker-course
```
