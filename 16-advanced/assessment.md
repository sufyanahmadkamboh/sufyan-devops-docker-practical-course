# Module 16 assessment · Advanced Docker

> Lessons [100](100-metadata-and-inspect/README.md)–[105](105-cache-optimization/README.md) · ⏱ 45 minutes · try every
> question before opening its answer

## Knowledge check

**1. Which `docker inspect` template prints the host port mapped to a container's port `80/tcp`?**

<details><summary>Answer</summary>

`{{(index (index .NetworkSettings.Ports "80/tcp") 0).HostPort}}`: `index` because the key contains a slash
(lesson 100).

</details>

**2. Why does `docker inspect --format '{{.State.Status}}' nginx:1.30-alpine` fail?**

<details><summary>Answer</summary>

`nginx:1.30-alpine` is an image; only containers have `State`. Use `docker container inspect` / `docker image inspect`
to make the type explicit (lesson 100).

</details>

**3. Which label keys record an image's source repository and Git commit?**

<details><summary>Answer</summary>

`org.opencontainers.image.source` and `org.opencontainers.image.revision` (lesson 101).

</details>

**4. `docker ps --filter label=Team=payments` returns nothing, although the containers have a team label. Why?**

<details><summary>Answer</summary>

Filters match keys and values exactly; the key is `team`, not `Team` (lesson 101).

</details>

**5. What is the risk of the default `json-file` logging driver without options?**

<details><summary>Answer</summary>

The log files are never rotated: a chatty or crash-looping container can fill the host's disk. Use `max-size` and
`max-file`, or the `local` driver (lesson 102).

</details>

**6. How do you get a compiled binary out of a Dockerfile build without creating an image?**

<details><summary>Answer</summary>

`docker buildx build --target STAGE --output type=local,dest=DIR .` (lesson 103).

</details>

**7. What does `FROM --platform=$BUILDPLATFORM golang …` achieve in a multi-platform build?**

<details><summary>Answer</summary>

The build stage runs natively on the build machine for every target; `TARGETOS`/`TARGETARCH` make Go cross-compile, so
no emulation is needed (lesson 104).

</details>

**8. Why should `COPY requirements.txt .` and `RUN pip install` come before `COPY . .`?**

<details><summary>Answer</summary>

Code changes on every commit; dependencies rarely. With the dependency steps first, a code change invalidates only the
final `COPY . .` and the expensive install stays cached (lesson 105).

</details>

**9. Every build re-runs almost all steps although nothing changed. What do you look for?**

<details><summary>Answer</summary>

The first step that ran (with `--progress plain`): typically an `ARG` with a value that changes on every build (time,
commit) declared early, an early `COPY . .`, or a changing file in the build context (lesson 105).

</details>

## Practical task

Build the Go API in `examples/go-api` for `linux/amd64` and `linux/arm64` as `cafe-go:multi`, with the labels
`org.opencontainers.image.version=2.0.0` and `team=platform` (use `docker buildx build --label`), and prove both
variants and both labels exist.

<details><summary>Solution</summary>

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh assessment-16 examples/go-api
cd ~/docker-practice/assessment-16
cat > Dockerfile <<'EOF'
FROM --platform=$BUILDPLATFORM golang:1.26-alpine AS build
ARG TARGETOS TARGETARCH
WORKDIR /src
COPY go.mod main.go ./
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /out/go-api .
FROM scratch
COPY --from=build /out/go-api /go-api
USER 65534:65534
ENTRYPOINT ["/go-api"]
EOF
echo "lab ready"
```

<!-- test: contains=linux/arm64; contains=2.0.0 platform; output -->
```bash
docker buildx build -q --platform linux/amd64,linux/arm64 --label org.opencontainers.image.version=2.0.0 \
  --label team=platform -t cafe-go:multi --load . > /dev/null
docker image ls --tree cafe-go:multi | grep -o 'linux/[a-z0-9]*'
docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.version"}} {{.Config.Labels.team}}' cafe-go:multi
```

```text
linux/amd64
linux/arm64
2.0.0 platform
```

</details>

## Troubleshooting task

A container's logs cannot be read. Reproduce it:

<!-- test: contains=started audit -->
```bash
docker run -d --name audit --log-driver none --label team=platform alpine:3.23 sh -c 'echo "audit started"; sleep 300' > /dev/null && echo "started audit"
```

<!-- test: fail; contains=does not support reading -->
```bash
docker logs audit 2>&1
```

Find the cause with `docker inspect`, fix it so the logs can be read and are rotated at 5 MB with 2 files, and prove
the fix.

<details><summary>Solution</summary>

<!-- test: contains=none; output -->
```bash
docker inspect --format '{{.HostConfig.LogConfig.Type}}' audit
```

```text
none
```

The logging driver is `none`: the output was discarded. The driver cannot be changed on an existing container;
recreate it with the same labels and a rotated driver:

<!-- test: retry=5; contains=audit started; contains={"max-file":"2","max-size":"5m"}; output -->
```bash
docker rm -f audit > /dev/null
docker run -d --name audit --log-driver local --log-opt max-size=5m --log-opt max-file=2 --label team=platform \
  alpine:3.23 sh -c 'echo "audit started"; sleep 300' > /dev/null
sleep 1
docker logs audit
docker inspect --format '{{json .HostConfig.LogConfig.Config}}' audit
```

```text
audit started
{"max-file":"2","max-size":"5m"}
```

</details>

## Real-world scenario

Your team's CI builds a Node.js service image for every commit. The Dockerfile starts with `COPY . .`, then `npm ci`,
and ends with `LABEL` lines. Builds take long, the images are only for `amd64` although half of the new servers are
ARM, and nobody can tell which commit a running container was built from. What do you change?

<details><summary>Model answer</summary>

Reorder for the cache: `COPY package.json package-lock.json ./`, then
`RUN --mount=type=cache,target=/root/.npm npm ci`, then `COPY . .`, with a `.dockerignore` for `node_modules`, `.git`
and logs; share the cache between CI runs with `--cache-from`/`--cache-to` (lesson 105). Build with
`--platform linux/amd64,linux/arm64 --push`, so one tag serves both kinds of server (lesson 104). Add
`org.opencontainers.image.revision` and `…source` labels from the CI's commit variables, declared at the end of the
Dockerfile or with `--label` so they do not invalidate the cache (lessons 101, 105). Then
`docker inspect --format '{{index .Config.Labels "org.opencontainers.image.revision"}}'` on the image of a running
container names its commit.

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f audit > /dev/null 2>&1 || true
docker image rm -f cafe-go:multi > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/assessment-16
```
