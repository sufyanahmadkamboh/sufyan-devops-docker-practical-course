<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 140 · Kubernetes for Docker users · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-140 examples/go-api
cp 20-kubernetes/139-deploy-an-image-to-kind/examples/* ~/docker-practice/lesson-140/
cd ~/docker-practice/lesson-140
```

```bash
cd ~/docker-practice/lesson-140
kind create cluster --name docker-course --wait 120s > /dev/null 2>&1
docker build -q -t go-api:1.0 . > /dev/null
echo 'FROM busybox:1.37' | docker build -q -t toolbox:1.0 - > /dev/null
kind load docker-image go-api:1.0 toolbox:1.0 --name docker-course > /dev/null 2>&1
kubectl apply -f deployment.yaml -f service.yaml > /dev/null
kubectl rollout status deployment/go-api --timeout=120s
```

## Demonstration

```bash
kubectl get pods -l app=go-api -o wide
```

```bash
kubectl logs -l app=go-api --prefix
```

```bash
kubectl run probe --rm -i --restart=Never --image=toolbox:1.0 -- sh -c 'sleep 2; wget -qO- http://go-api/health' 2>/dev/null
```

```bash
kubectl delete pod -l app=go-api --wait=false > /dev/null
kubectl rollout status deployment/go-api --timeout=90s > /dev/null
kubectl get deployment go-api --no-headers -o custom-columns=READY:.status.readyReplicas,WANTED:.spec.replicas | awk '{print $1 "/" $2 " ready"}'
```

## Hands-on lab

```bash
kubectl exec deployment/go-api -- sh -c 'echo hi' 2>&1 || true
kubectl get deployment go-api -o jsonpath='{range .spec.template.spec.containers[0].env[*]}{.name}={.value}{"\n"}{end}'
```

## Break it

```bash
kubectl patch deployment go-api --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/port","value":9090}]'
kubectl rollout status deployment/go-api --timeout=40s 2>&1
```

## Troubleshoot it

```bash
kubectl get pods -l app=go-api
```

```bash
kubectl describe pod -l app=go-api | grep "Readiness probe failed" | tail -2
```

```bash
kubectl run probe --rm -i --restart=Never --image=toolbox:1.0 -- sh -c 'sleep 2; wget -qO- http://go-api/health' 2>/dev/null
```

## Fix it

```bash
kubectl rollout undo deployment/go-api
kubectl rollout status deployment/go-api --timeout=120s
```

```bash
kubectl get deployment go-api -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.port}' && echo
```

## Practice challenge

```bash
kubectl get pods -l app=go-api -o jsonpath='{.items[0].spec.containers[0].resources.limits.memory}' && echo
id=$(docker exec docker-course-control-plane crictl ps --name go-api -q | head -1)
docker exec docker-course-control-plane crictl inspect "$id" | grep -i '"memory_limit_in_bytes"\|"memoryLimitInBytes"' | head -1
```

## Cleanup

```bash
kind delete cluster --name docker-course
docker image rm -f go-api:1.0 toolbox:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-140
```
