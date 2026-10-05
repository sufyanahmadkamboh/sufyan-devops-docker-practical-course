# Module 13 assessment · Multi-stage builds

> Lessons [087](087-why-multistage/README.md)–[091](091-measuring-image-size/README.md) · ⏱ 40 minutes · try every
> question before opening its answer

## Knowledge check

**1. Which stage of a multi-stage Dockerfile becomes the image?**

<details><summary>Answer</summary>

The last one, unless `docker build --target STAGE` selects another (lesson 087).

</details>

**2. What does `COPY --from=build /out/app /app` read: the build context, your computer or something else?**

<details><summary>Answer</summary>

The file system of the stage named `build`, as it is after that stage's last instruction (lesson 087).

</details>

**3. A multi-stage build fails with `"/src/app": not found` in `COPY --from`. How do you find the right path?**

<details><summary>Answer</summary>

Build the stage alone with `--target build`, run a container from it and look (`ls`, `find / -name app`), then use
the path the build command really wrote to (lesson 087).

</details>

**4. Why does the final stage of a Node.js multi-stage build run `npm ci --omit=dev` instead of copying
`node_modules` from the build stage?**

<details><summary>Answer</summary>

The build stage's `node_modules` contains development dependencies (compilers, test tools). Installing production
dependencies fresh keeps them out of the image (lessons 088, 091).

</details>

**5. Why must the entrypoint of a distroless image use the exec form?**

<details><summary>Answer</summary>

The shell form runs `/bin/sh -c …`, and distroless images have no shell: the container fails to start with
`exec: "/bin/sh": … no such file or directory` (lesson 089).

</details>

**6. How do you debug the network of a container that has no shell?**

<details><summary>Answer</summary>

Start a tool container in its network namespace: `docker run --rm --network container:NAME busybox:1.37 wget -qO-
http://localhost:PORT/` (lesson 089).

</details>

**7. What are `jdeps` and `jlink` used for in a Java image?**

<details><summary>Answer</summary>

`jdeps` lists the JDK modules the application needs; `jlink` builds a Java runtime containing only those modules, which
can replace the full JRE (lesson 090).

</details>

**8. What is the difference between DISK USAGE and CONTENT SIZE in `docker image ls`?**

<details><summary>Answer</summary>

Disk usage is the unpacked size on the engine's disk; content size is the compressed size that registries store and
pulls download (lesson 091).

</details>

## Practical task

Build the course's Go API (`examples/go-api`) as `assess-ms:1.0` with a multi-stage Dockerfile whose final stage is
`gcr.io/distroless/static-debian12:nonroot`. Prove that the image is smaller than 20 MB (content size), that it does
not run as root, and that `/health` answers on port 8096.

<details><summary>Solution</summary>

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh assessment-13 examples/go-api
cd ~/docker-practice/assessment-13
cat > Dockerfile <<'EOF'
FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY main.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/go-api .

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/go-api /go-api
EXPOSE 8080
ENTRYPOINT ["/go-api"]
EOF
docker build -q -t assess-ms:1.0 . > /dev/null
docker run -d --name assess-ms -p 8096:8080 assess-ms:1.0 > /dev/null
```

<!-- test: retry=10; contains=under 20 MB; contains=user 65532; contains="status":"ok" -->
```bash
size=$(docker image inspect --format '{{.Size}}' assess-ms:1.0)
[ "$size" -lt 20000000 ] && echo "under 20 MB ($size bytes)"
echo "user $(docker image inspect --format '{{.Config.User}}' assess-ms:1.0)"
curl -s http://localhost:8096/health
```

</details>

## Troubleshooting task

The CI pipeline runs the tests of a multi-stage Dockerfile with `--target test` and has started failing. Reproduce it:

<!-- test: fail; contains=could not be found; output -->
```bash
cd ~/docker-practice/assessment-13
{ sed -n '1,/^RUN CGO_ENABLED/p' Dockerfile
  printf '\nFROM build AS tests\nRUN go vet ./...\n\n'
  sed -n '/^FROM gcr.io/,$p' Dockerfile
} > Dockerfile.ci
docker build --target test -f Dockerfile.ci -t assess-ms:test . 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

```text
ERROR: failed to build: failed to solve: target stage "test" could not be found (did you mean tests?)
```

Find the cause and make the pipeline's command work.

<details><summary>Solution</summary>

`target stage "test" could not be found`: no stage has that name. List the stage names:

<!-- test: contains=AS tests -->
```bash
grep -n '^FROM' Dockerfile.ci
```

Someone renamed the stage to `tests`. Use one name in both places, either in the Dockerfile or in the pipeline:

<!-- test: contains=assess-ms:test -->
```bash
sed -i.bak 's/AS tests$/AS test/' Dockerfile.ci && rm Dockerfile.ci.bak
docker build -q --target test -f Dockerfile.ci -t assess-ms:test . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' assess-ms
```

</details>

## Real-world scenario

A security review finds 140 known vulnerabilities in your Java service's image, almost all in OS packages and the JDK
tools (compiler, `jshell`), and asks you to "fix all of them". The service is built with Maven in the same image it runs
in. What do you propose?

<details><summary>Model answer</summary>

Most findings are in software the service does not need at run time. Split the Dockerfile into a build stage (JDK +
Maven) and a runtime stage (a JRE image, or a `jlink` runtime on a minimal base), copying only the jar (lesson 090).
Rebuild regularly so base image patches arrive, and re-scan (lesson 082). Measure the result: the image size with
`docker image ls`/`docker history` (lesson 091) and the vulnerability count before and after, and report the remaining
findings that affect the runtime itself.

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f assess-ms > /dev/null 2>&1 || true
docker image rm -f assess-ms:1.0 assess-ms:test > /dev/null 2>&1 || true
rm -rf ~/docker-practice/assessment-13
```
