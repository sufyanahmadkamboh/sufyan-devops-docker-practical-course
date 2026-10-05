# Module 20 assessment · Docker and Kubernetes

> Lessons [138](138-from-docker-to-kubernetes/README.md)–[140](140-kubernetes-for-docker-users/README.md) · ⏱ 45
> minutes · try every question before opening its answer

## Knowledge check

**1. Does an image built with Docker need to be changed to run on Kubernetes?**

<details><summary>Answer</summary>

No. Docker and containerd (which Kubernetes uses) both run OCI images; the same image runs unchanged (lesson 138).

</details>

**2. Which Pod spec fields correspond to `-e`, `--memory` and `HEALTHCHECK`?**

<details><summary>Answer</summary>

`env`, `resources.limits.memory` and `readinessProbe`/`livenessProbe` (lesson 138).

</details>

**3. What replaces `-p 8080:8080` in Kubernetes?**

<details><summary>Answer</summary>

A Service gives the Pods a stable name and address inside the cluster (and, with type `LoadBalancer` or an Ingress,
outside it). For testing from your computer, `kubectl port-forward` (lessons 138, 139).

</details>

**4. Why does a kind cluster need `kind load docker-image` before it can run your local image?**

<details><summary>Answer</summary>

The nodes are containers with their own containerd image store; they cannot see the Docker engine's images. In a real
cluster, a registry plays that role (lesson 139).

</details>

**5. A Pod using `go-api:latest` is in `ImagePullBackOff` although the image was loaded. Why?**

<details><summary>Answer</summary>

For `:latest` the default `imagePullPolicy` is `Always`: the kubelet pulls from the registry every time, and
`docker.io/library/go-api` does not exist. Use a version tag (lesson 139).

</details>

**6. What happens when you `kubectl delete` a Pod of a Deployment?**

<details><summary>Answer</summary>

The Deployment (through its ReplicaSet) creates a new Pod to keep the desired number of replicas (lesson 140).

</details>

**7. A new Pod is `Running` but `0/1` ready during a rolling update. Is the application down?**

<details><summary>Answer</summary>

No. A Pod that is not ready receives no traffic from the Service, and the rolling update keeps the old Pods until the
new ones are ready. Check `kubectl describe pod` for the probe failure and roll back (lesson 140).

</details>

**8. Which commands replace `docker ps`, `docker logs` and `docker inspect`?**

<details><summary>Answer</summary>

`kubectl get pods`, `kubectl logs`, `kubectl describe pod` / `kubectl get pod -o yaml` (lesson 140).

</details>

## Practical task

On a new kind cluster, deploy `examples/go-api` as version `2.0` with **one** replica and a Service, without writing
YAML files (use `kubectl create`), and prove from another Pod that `http://go-api/health` answers.

<details><summary>Solution</summary>

<!-- test: timeout=420; contains=successfully rolled out -->
```bash
bash scripts/lab.sh assessment-20 examples/go-api > /dev/null
cp 20-kubernetes/139-deploy-an-image-to-kind/examples/Dockerfile ~/docker-practice/assessment-20/
cd ~/docker-practice/assessment-20
kind create cluster --name docker-course --wait 120s > /dev/null 2>&1
docker build -q -t go-api:2.0 . > /dev/null
echo 'FROM busybox:1.37' | docker build -q -t toolbox:1.0 - > /dev/null
kind load docker-image go-api:2.0 toolbox:1.0 --name docker-course > /dev/null 2>&1
kubectl create deployment go-api --image=go-api:2.0 --port=8080
kubectl expose deployment go-api --port=80 --target-port=8080
kubectl rollout status deployment/go-api --timeout=120s
```

<!-- test: retry=5; contains="status":"ok"; output -->
```bash
kubectl run check --rm -i --restart=Never --image=toolbox:1.0 -- sh -c 'sleep 2; wget -qO- http://go-api/health' 2>/dev/null
```

```text
{"status":"ok"}
pod "check" deleted from default namespace
```

`kubectl expose` creates a Service with the Deployment's labels as its selector.

</details>

## Troubleshooting task

A second application is deployed from an image that was built but never loaded into the cluster:

<!-- test: contains=report-api -->
```bash
cd ~/docker-practice/assessment-20
docker tag go-api:2.0 report-api:1.0
kubectl create deployment report-api --image=report-api:1.0 --port=8080
```

Find out why it does not start, and fix it without changing the Deployment.

<details><summary>Solution</summary>

<!-- test: retry=30; anyof=ErrImagePull||ImagePullBackOff; output -->
```bash
kubectl get pods -l app=report-api --no-headers -o custom-columns=POD:.metadata.name,STATUS:.status.containerStatuses[0].state.waiting.reason
```

```text
report-api-546fdb768c-b8v6x   ErrImagePull
```

<!-- test: retry=10; anyof=pull access denied||failed to pull||Failed to pull -->
```bash
kubectl describe pod -l app=report-api | grep "Failed to pull" | tail -1
```

The kubelet cannot find `report-api:1.0` on the node and cannot pull it from Docker Hub. The policy is `IfNotPresent`
(a version tag), so loading the image is enough: the kubelet retries on its own (with a growing back-off) and starts
the Pod.

<!-- test: timeout=400; contains=successfully rolled out -->
```bash
kind load docker-image report-api:1.0 --name docker-course > /dev/null 2>&1
kubectl rollout status deployment/report-api --timeout=360s
```

</details>

## Real-world scenario

Your team moves a Docker Compose application (an API with a healthcheck, `environment:` values, a password and a
database volume) to Kubernetes. A colleague asks what has to change in the images. What do you answer, and what does
change?

<details><summary>Model answer</summary>

Nothing in the images: the same images, from the same CI pipeline and registry, run on Kubernetes (lesson 138). What
changes is the description: each service becomes a Deployment (or a StatefulSet for the database) and a Service;
`environment:` becomes `env` or a ConfigMap; the password becomes a Secret mounted as a file; the volume becomes a
PersistentVolumeClaim; the healthcheck becomes readiness and liveness probes; `--memory`/`--cpus` become resource
limits. The images must use version tags (not `latest`) and run as non-root, which they already should (module 18).

</details>

## Cleanup

<!-- test: timeout=180 -->
```bash
kind delete cluster --name docker-course
docker image rm -f go-api:2.0 report-api:1.0 toolbox:1.0 > /dev/null
rm -rf ~/docker-practice/assessment-20
```
