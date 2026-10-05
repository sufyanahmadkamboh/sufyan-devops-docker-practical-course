# Lesson 139 · Deploy an image to kind

> Level 21 · Docker and Kubernetes · ⏱ 40 minutes · run every command from the course folder

## What are we learning?

The complete path from source code to a running Kubernetes workload: **build** the Go API's image with Docker (the
multi-stage Dockerfile of lesson 089), **load** it into a kind cluster (in place of pushing it to a registry the
cluster can pull from), **deploy** it with a Deployment and a Service, and **reach** it with `kubectl port-forward`.
Then the most common first failure: a Pod stuck in `ImagePullBackOff` because of the `latest` tag.

## Visual

```text
 examples/go-api ──docker build──▶ go-api:1.0 (local Docker engine)
                                        │ kind load docker-image go-api:1.0
                                        ▼
 ┌────────────── kind node (a Docker container) ──────────────────────────────┐
 │ containerd image store: go-api:1.0                                         │
 │                                                                            │
 │ Deployment go-api ──▶ ReplicaSet ──▶ Pod go-api-…-abcde   (8080)           │
 │                                  └─▶ Pod go-api-…-fghij   (8080)           │
 │ Service go-api :80 ──────── selects app=go-api ──▶ both Pods :8080         │
 └────────────────────────────────────────────────────────────────────────────┘
          ▲ kubectl port-forward service/go-api 8090:80
 curl localhost:8090

 imagePullPolicy:  tag :latest (or none) → Always (must pull from a registry)
                   any other tag          → IfNotPresent (a loaded image is used)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-139 examples/go-api
cp 20-kubernetes/139-deploy-an-image-to-kind/examples/* ~/docker-practice/lesson-139/
cd ~/docker-practice/lesson-139
ls
```

<!-- test: timeout=300; contains=Ready -->
```bash
kind create cluster --name docker-course --wait 120s
kubectl get nodes
```

## Demonstration

**1. Build** the image, exactly as without Kubernetes:

<!-- test: contains=go-api:1.0; output -->
```bash
cd ~/docker-practice/lesson-139
docker build -q -t go-api:1.0 . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' go-api
```

```text
go-api:1.0  14.7MB
```

**2. Load** it into the cluster. The cluster's nodes have their own image store (containerd inside the node
container) and cannot see your Docker engine's images:

<!-- test: contains=go-api:1.0 -->
```bash
kind load docker-image go-api:1.0 --name docker-course
docker exec docker-course-control-plane crictl images | grep go-api
```

**3. Deploy** the manifests ([deployment.yaml](examples/deployment.yaml), [service.yaml](examples/service.yaml)):

<!-- test: timeout=180; contains=successfully rolled out; output -->
```bash
kubectl apply -f deployment.yaml -f service.yaml
kubectl rollout status deployment/go-api --timeout=120s
```

```text
deployment.apps/go-api created
service/go-api created
Waiting for deployment "go-api" rollout to finish: 0 of 2 updated replicas are available...
Waiting for deployment "go-api" rollout to finish: 1 of 2 updated replicas are available...
deployment "go-api" successfully rolled out
```

<!-- test: contains=Running; output -->
```bash
kubectl get pods -l app=go-api -o custom-columns=POD:.metadata.name,STATUS:.status.phase,READY:.status.containerStatuses[0].ready,IMAGE:.spec.containers[0].image
```

```text
POD                       STATUS    READY   IMAGE
go-api-79fcc74d5d-6x8bj   Running   true    go-api:1.0
go-api-79fcc74d5d-k78mt   Running   true    go-api:1.0
```

**4. Reach** it. `kubectl port-forward` opens a tunnel from your computer to the Service, much like `-p` does for a
container:

<!-- test: contains=Hello from Go; output -->
```bash
kubectl port-forward service/go-api 8090:80 > /dev/null 2>&1 &
pf=$!
sleep 3
curl -s http://localhost:8090/ && echo
curl -s http://localhost:8090/health && echo
kill $pf
```

```text
{"hostname":"go-api-79fcc74d5d-6x8bj","message":"Hello from Go"}

{"status":"ok"}
```

The `hostname` in the answer is the Pod's name: the Service sent the request to one of the two Pods.

## Command breakdown

| Command | What it does |
|---|---|
| `kind load docker-image IMAGE --name CLUSTER` | copy an image from the Docker engine into every node of the cluster |
| `kubectl apply -f FILE` | create or update the objects described in the file |
| `kubectl rollout status deployment/NAME` | wait until the new Pods are ready (or time out) |
| `kubectl get pods -l app=go-api` | the Pods with that label |
| `kubectl port-forward service/NAME LOCAL:PORT` | forward a local port to the Service, for testing |
| `kubectl logs deployment/NAME` | the logs of one of the Deployment's Pods (like `docker logs`) |

## Hands-on lab

**Instructions.** Scale the Deployment to three copies (the Kubernetes way of running `docker run` three times) and
check that all three are ready and share the load.

**Expected result.** `deployment.apps/go-api scaled`, then three Pods that are `Running` and ready.

**Verification.**

<!-- test: timeout=180; contains=3/3 -->
```bash
kubectl scale deployment/go-api --replicas=3
kubectl rollout status deployment/go-api --timeout=120s > /dev/null
kubectl get deployment go-api -o custom-columns=NAME:.metadata.name,READY:.status.readyReplicas,WANTED:.spec.replicas --no-headers | awk '{print $1, $2 "/" $3}'
```

## Break it

A colleague deploys the same image, but tagged `latest`, which they also loaded into the cluster:

<!-- test: contains=latest-api -->
```bash
docker tag go-api:1.0 go-api:latest
kind load docker-image go-api:latest --name docker-course > /dev/null 2>&1
kubectl create deployment latest-api --image=go-api:latest --port=8080
```

<!-- test: retry=30; anyof=ImagePullBackOff||ErrImagePull; output -->
```bash
kubectl get pods -l app=latest-api
```

```text
NAME                          READY   STATUS         RESTARTS   AGE
latest-api-7bbc49956b-pj7ws   0/1     ErrImagePull   0          3s
```

The image is in the node, yet the Pod never starts.

## Troubleshoot it

`kubectl describe` shows a Pod's events, the Kubernetes equivalent of reading `docker events` and the error of
`docker run` together:

<!-- test: anyof=pull access denied||failed to pull||Failed to pull; output=tail:6 -->
```bash
kubectl describe pod -l app=latest-api | grep -E "Warning|Normal" | tail -6
```

```text
  Normal   Scheduled  3s    default-scheduler  Successfully assigned default/latest-api-7bbc49956b-pj7ws to docker-course-control-plane
  Normal   Pulling    2s    kubelet            Pulling image "go-api:latest"
  Warning  Failed     2s    kubelet            Failed to pull image "go-api:latest": failed to pull and unpack image "docker.io/library/go-api:latest": failed to resolve reference "docker.io/library/go-api:latest": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
  Warning  Failed     2s    kubelet            Error: ErrImagePull
  Normal   BackOff    1s    kubelet            Back-off pulling image "go-api:latest"
  Warning  Failed     1s    kubelet            Error: ImagePullBackOff
```

The kubelet tried to **pull** `docker.io/library/go-api:latest` from Docker Hub, where no such image exists. Why pull
an image the node already has? Because of the pull policy Kubernetes chose:

<!-- test: contains=Always; output -->
```bash
kubectl get deployment latest-api -o jsonpath='{.spec.template.spec.containers[0].imagePullPolicy}' && echo
kubectl get deployment go-api -o jsonpath='{.spec.template.spec.containers[0].imagePullPolicy}' && echo
```

```text
Always
IfNotPresent
```

For the tag `latest` (or no tag), the default is `Always`: "latest" can change at any time, so Kubernetes always
asks the registry. For any other tag the default is `IfNotPresent`, so the loaded `go-api:1.0` is used. In a real
cluster, `latest` also means you cannot tell which version runs, nor roll back to it (lesson 021).

## Fix it

Deploy an immutable version tag (the right fix; forcing `imagePullPolicy: IfNotPresent` on `latest` would only hide
the problem). The pull policy is filled in when the Deployment is **created**, so `kubectl set image` alone would keep
`Always`, and the kubelet would still try Docker Hub. Recreate the Deployment with the version tag:

<!-- test: timeout=180; contains=successfully rolled out -->
```bash
kubectl delete deployment latest-api
kubectl create deployment latest-api --image=go-api:1.0 --port=8080
kubectl rollout status deployment/latest-api --timeout=120s
```

<!-- test: contains=go-api:1.0 IfNotPresent -->
```bash
kubectl get deployment latest-api -o jsonpath='{.spec.template.spec.containers[0].image} {.spec.template.spec.containers[0].imagePullPolicy}' && echo
```

## Practice challenge

Deploy version `1.1` of the API: change its greeting, build `go-api:1.1`, load it, and roll the `go-api` Deployment to
it without downtime. Then roll back.

<details>
<summary>Solution</summary>

<!-- test: timeout=300; contains=Hello from Go 1.1; contains=rolled back; output -->
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

</details>

## Real-world example

In a real cluster the "load" step is a registry: CI pushes `ghcr.io/team/go-api:sha-3f9c2a1` (lesson 136), and the
deployment step runs `kubectl set image` (or updates a Helm value or a GitOps repository) with that tag. Developers use
kind with `kind load docker-image` to try their manifests locally in seconds, without pushing anything.

## Recap

- Build with Docker, load into kind (or push to a registry), deploy with a Deployment and a Service.
- `kubectl port-forward` reaches a Service from your computer for testing.
- `ImagePullBackOff`: the kubelet could not pull; `kubectl describe pod` shows why.
- `:latest` means `imagePullPolicy: Always`: deploy immutable version tags instead.
- Rolling updates and `rollout undo` work because every version has its own tag.

## Cleanup

<!-- test: timeout=180 -->
```bash
kind delete cluster --name docker-course
docker image rm -f go-api:1.0 go-api:1.1 go-api:latest > /dev/null
rm -rf ~/docker-practice/lesson-139
```

Next: [Lesson 140 · Kubernetes for Docker users](../140-kubernetes-for-docker-users/README.md)
