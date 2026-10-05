# Lesson 031 · ARG

> Level 5 · Dockerfiles · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`ARG NAME=default` declares a **build-time** variable: `docker build --build-arg NAME=value` sets it, the following
build steps can use it, and it is gone when the container runs. Use it for things that change *how* an image is built:
a version number, a base image tag, a feature switch. Its values are recorded in the image's history, so `ARG` is
**never** for passwords or tokens.

## Visual

```text
  docker build --build-arg VERSION=1.4.0 .

  ARG ALPINE_VERSION=3.23            ← before FROM: only usable in FROM lines
  FROM alpine:${ALPINE_VERSION}
  ARG VERSION=dev                    ← after FROM: usable by the steps below (default "dev")
  RUN echo "$VERSION" > /version     build time: VERSION=1.4.0
  CMD ["cat", "/version"]            run time:   no VERSION variable (only the file written at build time)

                  ARG                              ENV
  set by          --build-arg (build)              ENV in the Dockerfile, -e at run time
  exists          during the build only            in the image and every container
  history         values visible                   values visible          → neither is for secrets
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-031
cd ~/docker-practice/lesson-031
```

## Demonstration

A version that is chosen when building:

<!-- test: contains=version 1.4.0; contains=version dev; output -->
```bash
cat > Dockerfile <<'EOF'
ARG ALPINE_VERSION=3.23
FROM alpine:${ALPINE_VERSION}
ARG VERSION=dev
RUN echo "cafe menu version $VERSION on Alpine $(cat /etc/alpine-release)" > /version
CMD ["cat", "/version"]
EOF
docker build -q --build-arg VERSION=1.4.0 -t menu-arg:1.4.0 . > /dev/null
docker build -q -t menu-arg:dev . > /dev/null
docker run --rm menu-arg:1.4.0
docker run --rm menu-arg:dev
```

```text
cafe menu version 1.4.0 on Alpine 3.23.6
cafe menu version dev on Alpine 3.23.6
```

Without `--build-arg`, the default (`dev`) is used. The variable exists only during the build:

<!-- test: contains=VERSION at run time: []; output -->
```bash
docker run --rm menu-arg:1.4.0 sh -c 'echo "VERSION at run time: [$VERSION]"'
```

```text
VERSION at run time: []
```

## Command breakdown

| Instruction / option | Meaning |
|---|---|
| `ARG NAME` / `ARG NAME=default` | declare a build argument (with a default) |
| `docker build --build-arg NAME=value` | set it for this build |
| `ARG` before `FROM` | usable only in `FROM` lines, e.g. to choose the base image version |
| `ARG NAME` again after `FROM` | makes a pre-`FROM` argument usable in the build steps |
| `ENV NAME=$NAME` | turn a build argument into a run-time variable (lesson 030) |

## Hands-on lab

**Instructions.** Build `menu-arg:1.5.0` with `VERSION=1.5.0` and also set `ENV APP_VERSION=$VERSION` so the version is
available to the running container as an environment variable.

**Expected result.** `docker run --rm menu-arg:1.5.0 sh -c 'echo $APP_VERSION'` prints `1.5.0`.

**Verification.**

<!-- test: contains=1.5.0 -->
```bash
cd ~/docker-practice/lesson-031
printf 'FROM alpine:3.23\nARG VERSION=dev\nENV APP_VERSION=$VERSION\n' > Dockerfile.env
docker build -q -f Dockerfile.env --build-arg VERSION=1.5.0 -t menu-arg:1.5.0 . > /dev/null
docker run --rm menu-arg:1.5.0 sh -c 'echo $APP_VERSION'
```

## Break it

A colleague moves `ARG VERSION` to the top of the file, next to the other argument:

<!-- test: contains=version []; output -->
```bash
cat > Dockerfile.scope <<'EOF'
ARG ALPINE_VERSION=3.23
ARG VERSION=dev
FROM alpine:${ALPINE_VERSION}
RUN echo "version [$VERSION]" > /version
CMD ["cat", "/version"]
EOF
docker build -q -f Dockerfile.scope --build-arg VERSION=1.4.0 -t menu-arg:scope . > /dev/null
docker run --rm menu-arg:scope
```

```text
version []
```

The build succeeded, and the version is empty, although `--build-arg VERSION=1.4.0` was given.

## Troubleshoot it

An `ARG` declared **before** `FROM` belongs to the "global" scope: it can be used in `FROM` lines only. Each `FROM`
starts a new build stage, and inside a stage an argument exists only after an `ARG` line in that stage. The history of
the image shows which arguments the `RUN` step received:

<!-- test: contains=RUN /bin/sh -c echo; output=head:1 -->
```bash
docker image history --no-trunc --format '{{.CreatedBy}}' menu-arg:scope | grep '^RUN'
```

```text
RUN /bin/sh -c echo "version [$VERSION]" > /version # buildkit
```

No arguments (compare the fixed version below, which records `RUN |1 VERSION=1.4.0 …`).

## Fix it

Declare it again inside the stage (without a value, it keeps the global default or the `--build-arg` value):

<!-- test: contains=version [1.4.0]; output -->
```bash
awk '{ print } /^FROM / { print "ARG VERSION" }' Dockerfile.scope > Dockerfile.tmp && mv Dockerfile.tmp Dockerfile.scope
cat Dockerfile.scope
docker build -q -f Dockerfile.scope --build-arg VERSION=1.4.0 -t menu-arg:scope . > /dev/null
docker run --rm menu-arg:scope
docker image history --no-trunc --format '{{.CreatedBy}}' menu-arg:scope | grep '^RUN'
```

```text
ARG ALPINE_VERSION=3.23
ARG VERSION=dev
FROM alpine:${ALPINE_VERSION}
ARG VERSION
RUN echo "version [$VERSION]" > /version
CMD ["cat", "/version"]
version [1.4.0]
RUN |1 VERSION=1.4.0 /bin/sh -c echo "version [$VERSION]" > /version # buildkit
```

That last line is why `ARG` is not for secrets: **every value a `RUN` step uses is written into the image's history**.
Anyone who can pull the image can read it with `docker image history --no-trunc`.

## Practice challenge

A build step needs a token to download a private package. Show the leak with `ARG` (use the fake value
`example-token-123`), then pass the token with a **build secret** instead (`RUN --mount=type=secret,…` and
`docker build --secret`), and prove it is not in the history.

<details>
<summary>Solution</summary>

<!-- test: contains=leaked: yes; contains=with a secret: not in the history; output -->
```bash
cd ~/docker-practice/lesson-031
printf 'FROM alpine:3.23\nARG API_TOKEN\nRUN test -n "$API_TOKEN" && echo "downloading with the token"\n' > Dockerfile.leak
docker build -q -f Dockerfile.leak --build-arg API_TOKEN=example-token-123 -t menu-arg:leak . > /dev/null 2>&1
docker image history --no-trunc menu-arg:leak | grep -q example-token-123 && echo "leaked: yes"

printf 'example-token-123' > api_token.txt
cat > Dockerfile.secret <<'EOF'
FROM alpine:3.23
RUN --mount=type=secret,id=api_token \
    test -n "$(cat /run/secrets/api_token)" && echo "downloading with the token"
EOF
docker build -q -f Dockerfile.secret --secret id=api_token,src=api_token.txt -t menu-arg:secret . > /dev/null
docker image history --no-trunc menu-arg:secret | grep -q example-token-123 || echo "with a secret: not in the history"
rm api_token.txt
```

```text
leaked: yes
with a secret: not in the history
```

A secret mount makes the file `/run/secrets/api_token` available to that one `RUN` step only; it is never written to a
layer or to the history. Docker also warns about the first Dockerfile: `SecretsUsedInArgOrEnv: Do not use ARG or ENV
instructions for sensitive data`. Secrets are covered in depth in lesson 083.

</details>

## Real-world example

CI pipelines pass build metadata as arguments: `--build-arg VERSION=$GIT_TAG --build-arg COMMIT=$GIT_SHA`, written into
labels or a version file (lesson 101). Base image versions are often arguments too (`ARG NODE_VERSION=24`), so the same
Dockerfile can be tested against the next runtime version with one flag. Registry tokens and package-manager
credentials go through `--secret`, never `--build-arg`.

## Recap

- `ARG` is a build-time variable set with `--build-arg`; it does not exist in containers.
- An `ARG` before `FROM` is only for `FROM`; declare it again after `FROM` to use it in the steps.
- To keep a value at run time, copy it into `ENV` (or a file, or a label).
- Values used by `RUN` steps are recorded in the history: use build secrets for anything sensitive.

## Cleanup

<!-- test -->
```bash
docker image rm -f menu-arg:1.4.0 menu-arg:dev menu-arg:1.5.0 menu-arg:scope menu-arg:leak menu-arg:secret > /dev/null
rm -rf ~/docker-practice/lesson-031
```

Next: [Lesson 032 · EXPOSE](../032-expose/README.md)
