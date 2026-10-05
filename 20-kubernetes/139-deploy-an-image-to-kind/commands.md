<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 139 · Deploy an image to kind · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-139 examples/go-api
cp 20-kubernetes/139-deploy-an-image-to-kind/examples/* ~/docker-practice/lesson-139/
cd ~/docker-practice/lesson-139
ls
```

```bash
kind create cluster --name docker-course --wait 120s
kubectl get nodes
```

## Demonstration

```bash
cd ~/docker-practice/lesson-139
docker build -q -t go-api:1.0 . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' go-api
```

```bash
kind load docker-image go-api:1.0 --name docker-course
docker exec docker-course-control-plane crictl images | grep go-api
```

```bash
kubectl apply -f deployment.yaml -f service.yaml
kubectl rollout status deployment/go-api --timeout=120s
```

```bash
kubectl get pods -l app=go-api -o custom-columns=POD:.metadata.name,STATUS:.status.phase,READY:.status.containerStatuses[0].ready,IMAGE:.spec.containers[0].image
```

```bash
kubectl port-forward service/go-api 8090:80 > /dev/null 2>&1 &
pf=$!
sleep 3
curl -s http://localhost:8090/ && echo
curl -s http://localhost:8090/health && echo
kill $pf
```

## Hands-on lab

```bash
kubectl scale deployment/go-api --replicas=3
kubectl rollout status deployment/go-api --timeout=120s > /dev/null
kubectl get deployment go-api -o custom-columns=NAME:.metadata.name,READY:.status.readyReplicas,WANTED:.spec.replicas --no-headers | awk '{print $1, $2 "/" $3}'
```

## Break it

```bash
docker tag go-api:1.0 go-api:latest
kind load docker-image go-api:latest --name docker-course > /dev/null 2>&1
kubectl create deployment latest-api --image=go-api:latest --port=8080
```

```bash
kubectl get pods -l app=latest-api
```

## Troubleshoot it

```bash
kubectl describe pod -l app=latest-api | grep -E "Warning|Normal" | tail -6
```

```bash
kubectl get deployment latest-api -o jsonpath='{.spec.template.spec.containers[0].imagePullPolicy}' && echo
kubectl get deployment go-api -o jsonpath='{.spec.template.spec.containers[0].imagePullPolicy}' && echo
```

## Fix it

```bash
kubectl delete deployment latest-api
kubectl create deployment latest-api --image=go-api:1.0 --port=8080
kubectl rollout status deployment/latest-api --timeout=120s
```

```bash
kubectl get deployment latest-api -o jsonpath='{.spec.template.spec.containers[0].image} {.spec.template.spec.containers[0].imagePullPolicy}' && echo
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-139
sed 's|Hello from Go|Hello from Go 1.1|' main.go > main.new && mv main.new main.go
docker build -q -t go-api:1.1 . > /dev/null
kind load docker-image go-api:1.1 --name docker-course > /dev/null 2>&1
kubectl set image deployment/go-api go-api=go-api:1.1 > /dev/null
kubectl rollout status deployment/go-api --timeout=120s > /dev/null
kubectl port-forward service/go-api 8090:80 > /dev/null 2>&1 &
pf=$!
sleep 3
curl -s http://localhost:8090/ && echo
kill $pf
kubectl rollout undo deployment/go-api > /dev/null && echo "rolled back"
kubectl rollout status deployment/go-api --timeout=120s > /dev/null
kubectl get deployment go-api -o jsonpath='{.spec.template.spec.containers[0].image}' && echo
```

## Cleanup

```bash
kind delete cluster --name docker-course
docker image rm -f go-api:1.0 go-api:1.1 go-api:latest > /dev/null
rm -rf ~/docker-practice/lesson-139
```
