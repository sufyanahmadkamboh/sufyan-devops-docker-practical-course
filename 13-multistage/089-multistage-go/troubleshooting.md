<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 089 · Multi-stage builds for Go · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

`Dockerfile.broken` writes the entrypoint in **shell form** (`ENTRYPOINT /go-api`), as many Dockerfiles do:

```bash
docker build -q -f Dockerfile.broken -t go-distroless:broken . > /dev/null 2>&1
docker run -d --name go-broken go-distroless:broken 2>&1
```

```text
1c81475136461650e092b8d08f6447a8a9ea86dce09cefb9762121b4a7c927cd
docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "/bin/sh": stat /bin/sh: no such file or directory

Run 'docker run --help' for more information
```

## Troubleshoot it

`exec: "/bin/sh": stat /bin/sh: no such file or directory`: Docker tried to start `/bin/sh`, not `/go-api`. The shell
form `ENTRYPOINT /go-api` means "run `/bin/sh -c "/go-api"`", and distroless has no `/bin/sh`. The image configuration
shows it:

```bash
docker image inspect --format '{{json .Config.Entrypoint}}' go-distroless:broken
```

```text
["/bin/sh","-c","/go-api"]
```

The build even warned about it (`JSONArgsRecommended`), but warnings scroll past easily.

## Fix it

Use the exec form, a JSON array, as `Dockerfile` does:

```bash
docker rm -f go-broken > /dev/null 2>&1 || true
docker build -q -t go-distroless:fixed . > /dev/null
docker image inspect --format '{{json .Config.Entrypoint}}' go-distroless:fixed
```
