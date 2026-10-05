<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 088 · Multi-stage builds for Node.js · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

`Dockerfile.broken` is the multi-stage Dockerfile with one line missing. It builds without any error:

```bash
docker build -q -f Dockerfile.broken -t ts-multi:broken . > /dev/null
docker image ls --filter 'reference=ts-multi' --format '{{.Repository}}:{{.Tag}}'
```

But the container does not stay up:

```bash
docker run -d --name ts-broken ts-multi:broken > /dev/null
sleep 2
docker ps -a --filter name=ts-broken --format '{{.Names}}: {{.Status}}'
```

```text
ts-broken: Exited (1) 2 seconds ago
```

## Troubleshoot it

The build cannot catch a missing file in the final stage: every instruction succeeded. The container's log can:

```bash
docker logs ts-broken 2>&1 | grep -E '^Error'
```

```text
Error: Cannot find module '/app/dist/server.js'
```

`dist/` was built in the build stage and never copied into the final one. Compare the two Dockerfiles:

```bash
diff Dockerfile.broken Dockerfile || true
```

## Fix it

Restore the `COPY --from=build /app/dist ./dist` line (it is in `Dockerfile`) and check that the image really starts.
A quick smoke test after every build catches this class of mistake:

```bash
docker rm -f ts-broken > /dev/null
docker build -q -t ts-multi:fixed . > /dev/null
docker run -d --name ts-fixed ts-multi:fixed > /dev/null
sleep 1
docker logs ts-fixed
docker rm -f ts-fixed > /dev/null
```
