<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 087 · Why multi-stage builds? · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

`Dockerfile.broken` copies the binary from the path where a developer *thinks* it is:

```bash
grep 'COPY --from' Dockerfile.broken
docker build -f Dockerfile.broken -t go-multi:broken . 2>&1 | grep ERROR | head -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
COPY --from=build /src/go-api /usr/local/bin/go-api
#13 ERROR: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::aa389znbe09rrbo7vh25216f8: "/src/go-api": not found
```

## Troubleshoot it

`"/src/go-api": not found`: the build stage succeeded, but there is no file at that path **in the build stage**.
`COPY --from` paths are paths inside that stage's file system, not on your computer and not in the build context.
Build the stage on its own and look:

```bash
docker build -q -f Dockerfile.broken --target build -t go-multi:debug . > /dev/null
docker run --rm go-multi:debug sh -c 'ls /src; find / -name go-api -type f 2>/dev/null'
```

```text
go.mod
main.go
/out/go-api
```

The `go build -o /out/go-api` line decides the path; the `COPY --from` must use the same one.

## Fix it

```bash
diff Dockerfile.broken Dockerfile || true
docker build -q -t go-multi:fixed . > /dev/null && grep 'COPY --from' Dockerfile
```
