# Lesson 140 · Kubernetes for Docker users

> Level 21 · Docker and Kubernetes · ⏱ 40 minutes · run every command from the course folder

## What are we learning?

Your Docker troubleshooting habits carry over to Kubernetes almost one to one: `docker ps` becomes `kubectl get pods`,
`docker logs` becomes `kubectl logs`, `docker inspect` becomes `kubectl describe`, a throwaway `docker run --rm` on a
network becomes `kubectl run --rm`. This lesson uses them on a running application, then debugs the most common
Kubernetes-only failure: a **readiness probe** that never succeeds, which Kubernetes handles in a way Docker never
does.

## Visual

```text
 Docker                                          Kubernetes
 ─────────────────────────────────────────       ──────────────────────────────────────────────────
 docker ps                                       kubectl get pods  (-o wide: node, IP)
 docker logs NAME  (-f, --tail)                  kubectl logs POD | deployment/NAME | -l app=NAME --prefix
 docker exec -it NAME sh                         kubectl exec -it POD -- sh
 docker inspect NAME                             kubectl describe pod POD · kubectl get pod POD -o yaml
 docker events                                   kubectl get events --sort-by=.lastTimestamp
 docker run --rm --network net IMG CMD           kubectl run tmp --rm -i --restart=Never --image=IMG -- CMD
 docker rm -f NAME                               kubectl delete pod POD  (the Deployment creates a new one)
 HEALTHCHECK → "unhealthy" (still gets traffic)  readinessProbe fails → Pod removed from the Service
                                                  livenessProbe fails  → container restarted

 rolling update with a broken probe:
   old Pods (ready) ──keep serving──▶ Service       new Pod (0/1 READY) ──never receives traffic
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-140 examples/go-api
cp 20-kubernetes/139-deploy-an-image-to-kind/examples/* ~/docker-practice/lesson-140/
cd ~/docker-practice/lesson-140
```

<!-- test: timeout=420; contains=successfully rolled out -->
```bash
cd ~/docker-practice/lesson-140
kind create cluster --name docker-course --wait 120s > /dev/null 2>&1
docker build -q -t go-api:1.0 . > /dev/null
echo 'FROM busybox:1.37' | docker build -q -t toolbox:1.0 - > /dev/null
kind load docker-image go-api:1.0 toolbox:1.0 --name docker-course > /dev/null 2>&1
kubectl apply -f deployment.yaml -f service.yaml > /dev/null
kubectl rollout status deployment/go-api --timeout=120s
```

The cluster and the Go API of lesson 139, plus a small `toolbox:1.0` image for test commands: a local build of
`busybox:1.37`. `kind load` copies every platform of an image, and a pulled multi-platform image (like the official
`busybox`) only has the content for your own platform locally, so it fails with `content digest … not found`. An
image you build yourself has exactly one platform and loads without problems.

## Demonstration

`docker ps` → `kubectl get pods`, with the node and the Pod's own IP address:

<!-- test: contains=Running; output -->
```bash
kubectl get pods -l app=go-api -o wide
```

```text
NAME                      READY   STATUS    RESTARTS   AGE   IP           NODE                          NOMINATED NODE   READINESS GATES
go-api-79fcc74d5d-cjg2d   1/1     Running   0          1s    10.244.0.5   docker-course-control-plane   <none>           <none>
go-api-79fcc74d5d-jtqt9   1/1     Running   0          1s    10.244.0.6   docker-course-control-plane   <none>           <none>
```

`docker logs` → `kubectl logs`, for every Pod of the application at once:

<!-- test: contains=go-api listening on port 8080; output -->
```bash
kubectl logs -l app=go-api --prefix
```

```text
[pod/go-api-79fcc74d5d-cjg2d/go-api] 2026/10/05 10:03:15 go-api listening on port 8080
[pod/go-api-79fcc74d5d-jtqt9/go-api] 2026/10/05 10:03:15 go-api listening on port 8080
```

`docker run --rm` on the application's network → `kubectl run --rm`. The Service name works as a DNS name, like a
container name on a user-defined network (lesson 050):

<!-- test: retry=5; contains="status":"ok"; output -->
```bash
kubectl run probe --rm -i --restart=Never --image=toolbox:1.0 -- sh -c 'sleep 2; wget -qO- http://go-api/health' 2>/dev/null
```

```text
{"status":"ok"}
pod "probe" deleted from default namespace
```

`sleep 2` gives `kubectl` time to attach to the Pod: a command that finishes faster than that can end before
`kubectl run -i` is connected, and its output is lost.

`docker rm -f` → `kubectl delete pod`, with one big difference: the Deployment immediately replaces the Pod.

<!-- test: timeout=120; contains=2/2 -->
```bash
kubectl delete pod -l app=go-api --wait=false > /dev/null
kubectl rollout status deployment/go-api --timeout=90s > /dev/null
kubectl get deployment go-api --no-headers -o custom-columns=READY:.status.readyReplicas,WANTED:.spec.replicas | awk '{print $1 "/" $2 " ready"}'
```

## Command breakdown

| Command | What it does |
|---|---|
| `kubectl get pods -o wide` | Pods with their node and IP |
| `kubectl logs -l app=go-api --prefix` | logs of all Pods with that label, each line prefixed with its Pod |
| `kubectl run NAME --rm -i --restart=Never --image=IMG -- CMD` | a one-off Pod that runs a command and is deleted |
| `kubectl describe pod POD` | configuration, state and **events** of a Pod (start here when something fails) |
| `kubectl rollout undo deployment/NAME` | return to the previous version of the Pod template |

## Hands-on lab

**Instructions.** The Go image is distroless: it has no shell, so `kubectl exec … -- sh` fails exactly like
`docker exec … sh` would (lesson 089). Prove it, then inspect the running container's environment variables from the
Pod specification instead.

**Expected result.** An error containing `executable file not found` (or `no such file`), then `PORT=8080`.

**Verification.**

<!-- test: anyof=executable file not found||no such file or directory; contains=PORT=8080 -->
```bash
kubectl exec deployment/go-api -- sh -c 'echo hi' 2>&1 || true
kubectl get deployment go-api -o jsonpath='{range .spec.template.spec.containers[0].env[*]}{.name}={.value}{"\n"}{end}'
```

## Break it

A colleague changes the readiness probe to port 9090 (the application listens on 8080) and applies it:

<!-- test: fail; contains=timed out; output -->
```bash
kubectl patch deployment go-api --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/port","value":9090}]'
kubectl rollout status deployment/go-api --timeout=40s 2>&1
```

```text
deployment.apps/go-api patched
Waiting for deployment "go-api" rollout to finish: 1 out of 2 new replicas have been updated...
error: timed out waiting for the condition
```

## Troubleshoot it

The rollout never finishes. Look at the Pods:

<!-- test: contains=0/1; output -->
```bash
kubectl get pods -l app=go-api
```

```text
NAME                      READY   STATUS    RESTARTS   AGE
go-api-6b44c6f98-2r2z4    0/1     Running   0          40s
go-api-79fcc74d5d-tlvtw   1/1     Running   0          41s
go-api-79fcc74d5d-zwjmq   1/1     Running   0          41s
```

The new Pod is `Running` but `0/1` ready, and the old Pods are still there. Its events say why:

<!-- test: contains=Readiness probe failed; output=tail:2 -->
```bash
kubectl describe pod -l app=go-api | grep "Readiness probe failed" | tail -2
```

```text
  Warning  Unhealthy  4s (x9 over 39s)  kubelet            Readiness probe failed: Get "http://10.244.0.10:9090/health": dial tcp 10.244.0.10:9090: connect: connection refused
```

`connection refused` on port 9090: nothing listens there. Kubernetes behaves very differently from a Docker
`HEALTHCHECK` here: a Pod that is not ready receives **no traffic** from the Service, and the rolling update does not
remove old Pods until new ones are ready. The application is still served by the old version:

<!-- test: retry=5; contains="status":"ok" -->
```bash
kubectl run probe --rm -i --restart=Never --image=toolbox:1.0 -- sh -c 'sleep 2; wget -qO- http://go-api/health' 2>/dev/null
```

## Fix it

Roll back to the last working version, then fix the manifest in Git (`deployment.yaml` still says 8080, which is
right):

<!-- test: timeout=180; contains=successfully rolled out -->
```bash
kubectl rollout undo deployment/go-api
kubectl rollout status deployment/go-api --timeout=120s
```

<!-- test: contains=8080 -->
```bash
kubectl get deployment go-api -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.port}' && echo
```

## Practice challenge

`docker run --memory 64m` sets a limit the container runtime enforces. Show the memory limit of a `go-api` Pod twice:
as written in the Pod spec, and in bytes as the container runtime (containerd in the kind node) applied it.

<details>
<summary>Solution</summary>

<!-- test: contains=64Mi; contains=67108864; output -->
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

</details>

## Real-world example

An on-call engineer who knows Docker well is paged for a service on Kubernetes. They follow the same steps as on a
Docker host: list (`kubectl get pods`), read the state and events (`kubectl describe`), read the logs
(`kubectl logs --previous` for a crashed container), test the network from inside (`kubectl run --rm` with
`busybox`). The new part is the controllers: they do not fix a Pod by hand, they fix the Deployment (or roll it back),
because the Deployment recreates whatever is deleted.

## Recap

- `get pods`, `logs`, `exec`, `describe`, `get events`, `run --rm`: the Docker troubleshooting toolkit, in Kubernetes.
- Deleting a Pod is not like `docker rm`: its Deployment replaces it.
- A failing readiness probe keeps a Pod out of the Service and stops a rolling update: old Pods keep serving.
- `kubectl rollout undo` returns to the previous working version; then fix the manifest.

## Cleanup

<!-- test: timeout=180 -->
```bash
kind delete cluster --name docker-course
docker image rm -f go-api:1.0 toolbox:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-140
```

Next: [Projects](../../21-projects/README.md)
