<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 139 · Deploy an image to kind · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Deploy version `1.1` of the API: change its greeting, build `go-api:1.1`, load it, and roll the `go-api` Deployment to
it without downtime. Then roll back.

## Solution

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

```text
{"hostname":"go-api-768d48cc9f-67558","message":"Hello from Go 1.1"}

rolled back
go-api:1.0
```

A rolling update starts new Pods, waits until they are ready, then removes old ones: there is always a ready Pod
behind the Service. `rollout undo` returns to the previous image, `go-api:1.0`, which is why every version must keep
its own tag.
