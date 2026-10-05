<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 140 · Kubernetes for Docker users · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A colleague changes the readiness probe to port 9090 (the application listens on 8080) and applies it:

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

```bash
kubectl get pods -l app=go-api
```

```text
NAME                      READY   STATUS    RESTARTS   AGE
go-api-6b44c6f98-fx79l    0/1     Running   0          41s
go-api-79fcc74d5d-dfzxr   1/1     Running   0          44s
go-api-79fcc74d5d-vdhkk   1/1     Running   0          44s
```

The new Pod is `Running` but `0/1` ready, and the old Pods are still there. The cluster's events say why (the kubelet
records one each time the probe fails; `kubectl describe pod` shows the same events per Pod):

```bash
kubectl get events --field-selector reason=Unhealthy -o custom-columns=MESSAGE:.message --no-headers | grep 9090 | tail -1
```

```text
Readiness probe failed: Get "http://10.244.0.10:9090/health": dial tcp 10.244.0.10:9090: connect: connection refused
```

`connection refused` on port 9090: nothing listens there. Kubernetes behaves very differently from a Docker
`HEALTHCHECK` here: a Pod that is not ready receives **no traffic** from the Service, and the rolling update does not
remove old Pods until new ones are ready. The application is still served by the old version:

```bash
kubectl run probe --rm -i --restart=Never --image=toolbox:1.0 -- sh -c 'sleep 2; wget -qO- http://go-api/health' 2>/dev/null
```

## Fix it

Roll back to the last working version, then fix the manifest in Git (`deployment.yaml` still says 8080, which is
right):

```bash
kubectl rollout undo deployment/go-api
kubectl rollout status deployment/go-api --timeout=120s
```

```bash
kubectl get deployment go-api -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.port}' && echo
```
