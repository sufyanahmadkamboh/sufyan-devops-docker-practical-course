# Lesson 087 · Why multi-stage builds?

> Level 14 · Multi-stage builds · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Building an application needs compilers, package managers and source code; **running** it usually needs only the
result. A single-stage image ships both (lesson 045 measured the waste). A **multi-stage** Dockerfile has several
`FROM` instructions: each starts a new **stage**, and a later stage copies only the files it needs from an earlier one
with `COPY --from=STAGE`. Only the last stage becomes the image. Smaller images pull faster, start faster and contain
far fewer programs an attacker could use or a scanner could flag.

## Visual

```text
  Dockerfile.single                              Dockerfile (multi-stage)

  FROM golang:1.26-alpine                        FROM golang:1.26-alpine AS build   ─┐ stage "build"
  COPY go.mod / main.go                          COPY go.mod / main.go               │ (thrown away,
  RUN go build -o /usr/local/bin/go-api          RUN go build -o /out/go-api         │  stays in the
  CMD ["go-api"]                                                                     ─┘  build cache)
                                                 FROM alpine:3.23                   ─┐ final stage
                                                 COPY --from=build /out/go-api …     │ = the image
                                                 CMD ["go-api"]                     ─┘

  image = toolchain + Alpine + binary            image = Alpine + binary
          (≈ 490 MB)                                     (≈ 26 MB)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-087 examples/go-api
cp 13-multistage/087-why-multistage/examples/Dockerfile* ~/docker-practice/lesson-087/
cd ~/docker-practice/lesson-087
ls
cat Dockerfile
```

## Demonstration

Build the single-stage and the multi-stage version of the same program:

<!-- test: contains=go-multi; output -->
```bash
docker build -q -f Dockerfile.single -t go-single:1.0 . > /dev/null
docker build -q -t go-multi:1.0 . > /dev/null
docker image ls --filter 'reference=go-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

```text
go-multi:1.0	26.4MB
go-single:1.0	492MB
```

The same binary, a fraction of the size. It works the same:

<!-- test: contains=Up -->
```bash
docker run -d --name go-multi -p 8089:8080 go-multi:1.0 > /dev/null
docker ps --filter name=go-multi --format '{{.Names}}: {{.Status}}'
```

<!-- test: retry=10; contains=Hello from Go; output -->
```bash
curl -s http://localhost:8089/
```

```text
{"hostname":"173067a013d5","message":"Hello from Go"}
```

But the Go toolchain is gone from the image:

<!-- test: contains=go: not found; output -->
```bash
docker run --rm go-single:1.0 go version
docker run --rm go-multi:1.0 sh -c 'go version' 2>&1 || true
```

```text
go version go1.26.8 linux/amd64
sh: go: not found
```

## Command breakdown

| Instruction / flag | Meaning |
|---|---|
| `FROM IMAGE AS NAME` | start a new stage and give it a name |
| `COPY --from=NAME SRC DEST` | copy files from an earlier stage (or `--from=IMAGE` from any image) |
| the last `FROM` | the final stage: the only one that becomes the image |
| `docker build --target NAME` | build only up to stage NAME and make that the image |
| stages not needed by the target | skipped entirely by BuildKit |

## Hands-on lab

**Instructions.** Use `--target build` to build only the first stage as `go-multi:build`, and show that the binary is
in it at `/out/go-api`, next to the source code.

**Expected result.** `go-multi:build` is about as big as the single-stage image (it is the toolchain stage) and
`/out/go-api` exists in it.

**Verification.**

<!-- test: contains=/out/go-api; contains=go-multi:build -->
```bash
docker build -q --target build -t go-multi:build . > /dev/null
docker run --rm go-multi:build ls -l /out/go-api /src
docker image ls --filter 'reference=go-multi' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

## Break it

`Dockerfile.broken` copies the binary from the path where a developer *thinks* it is:

<!-- test: fail; contains=not found; output -->
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

<!-- test: contains=/out/go-api; output -->
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

<!-- test: contains=COPY --from=build /out/go-api -->
```bash
diff Dockerfile.broken Dockerfile || true
docker build -q -t go-multi:fixed . > /dev/null && grep 'COPY --from' Dockerfile
```

## Practice challenge

Stages are also useful for **tests**. Without changing the final image, add a stage `test` (based on `build`) that runs
`go vet ./...`, and build only that stage with `--target test`. Write the new Dockerfile to `Dockerfile.test`.

<details>
<summary>Solution</summary>

<!-- test: contains=vet passed; output -->
```bash
cd ~/docker-practice/lesson-087
{ sed -n '1,/^RUN CGO_ENABLED/p' Dockerfile
  printf '\n# a test stage: never shipped, built only with --target test\nFROM build AS test\nRUN go vet ./... && echo "vet passed"\n'
  sed -n '/^# stage 2/,$p' Dockerfile
} > Dockerfile.test
grep -E '^FROM' Dockerfile.test
docker build --progress=plain --no-cache-filter test --target test -f Dockerfile.test -t go-multi:test . 2>&1 | grep -o 'vet passed' | head -1
```

```text
FROM golang:1.26-alpine AS build
FROM build AS test
FROM alpine:3.23
vet passed
```

`FROM build AS test` starts from the build stage's result. A normal `docker build` (no `--target`) skips the test stage,
because the final stage does not depend on it; CI runs `--target test` first, then the full build.
`--no-cache-filter test` makes the test run even when it is cached.

</details>

## Real-world example

A team's Node.js frontend image was 1.2 GB: it contained `node_modules` with webpack, test runners and linters, all
the source maps and the source code. With a build stage (`npm ci && npm run build`) and an `nginx:alpine` final stage
that copies only `dist/`, the image is the web server plus the static files. The build stays the same; only what is
shipped changes. Measure before and after (lesson 091).

## Recap

- Several `FROM`s = several stages; only the last one is the image.
- `COPY --from=STAGE` copies files from a stage's file system: build tools never reach the final image.
- `--target STAGE` builds up to a stage: for debugging, tests or a development image.
- `"…": not found` in `COPY --from`: inspect the stage with `--target` to find the real path.

## Cleanup

<!-- test -->
```bash
docker rm -f go-multi > /dev/null
docker image rm -f go-single:1.0 go-multi:1.0 go-multi:build go-multi:debug go-multi:fixed go-multi:test > /dev/null 2>&1 || true
rm -rf ~/docker-practice/lesson-087
```

Next: [Lesson 088 · Multi-stage builds for Node.js](../088-multistage-node/README.md)
