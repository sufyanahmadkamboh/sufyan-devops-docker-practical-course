<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 139 · Deploy an image to kind · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A colleague deploys the same image, but tagged `latest`, which they also loaded into the cluster:

```bash
docker tag go-api:1.0 go-api:latest
kind load docker-image go-api:latest --name docker-course > /dev/null 2>&1
kubectl create deployment latest-api --image=go-api:latest --port=8080
```

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

```bash
kubectl delete deployment latest-api
kubectl create deployment latest-api --image=go-api:1.0 --port=8080
kubectl rollout status deployment/latest-api --timeout=120s
```

```bash
kubectl get deployment latest-api -o jsonpath='{.spec.template.spec.containers[0].image} {.spec.template.spec.containers[0].imagePullPolicy}' && echo
```
