# Lesson 026 · RUN

> Level 5 · Dockerfiles · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`RUN` executes a command **while the image is built**, in a temporary container of the image so far, and saves the
changed files as a new layer: installing packages, creating users, compiling code. If the command fails (exits with a
status other than 0), the build stops. How you write `RUN` steps decides how big, how reproducible and how debuggable
the image is.

## Visual

```text
  RUN apk add --no-cache curl
        │
        ▼
  temporary container from the image so far ──▶ /bin/sh -c "apk add --no-cache curl"
        │                                                │
        │  exit status 0 ──▶ changed files saved as a new layer, build continues
        │  exit status ≠ 0 ──▶ build stops: "did not complete successfully: exit code: N"

  shell form:  RUN apk add --no-cache curl              runs through /bin/sh -c (variables, &&, pipes work)
  exec form:   RUN ["apk", "add", "--no-cache", "curl"] runs the program directly, no shell

  one step, cleaned up in the same step:
  RUN apk add --no-cache curl \
   && curl --version
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-026
cd ~/docker-practice/lesson-026
```

An empty folder: the Dockerfiles are written in the lesson. The steps download Alpine packages, so they need internet
access.

## Demonstration

Install a tool at build time and check it in the image:

<!-- test: contains=curl 8; output -->
```bash
cat > Dockerfile <<'EOF'
FROM alpine:3.23
RUN apk add --no-cache curl \
 && curl --version | head -1
CMD ["curl", "--version"]
EOF
docker build --progress=plain -t run-demo . 2>&1 | grep -E 'RUN|curl 8'
docker run --rm run-demo | head -1
```

```text
#5 [2/2] RUN apk add --no-cache curl  && curl --version | head -1
#5 1.020 curl 8.22.0 (x86_64-alpine-linux-musl) libcurl/8.22.0 OpenSSL/3.5.8 zlib/1.3.2 brotli/1.2.0 zstd/1.5.7 c-ares/1.34.8 libidn2/2.3.8 libpsl/0.21.5 nghttp2/1.69.0
curl 8.22.0 (x86_64-alpine-linux-musl) libcurl/8.22.0 OpenSSL/3.5.8 zlib/1.3.2 brotli/1.2.0 zstd/1.5.7 c-ares/1.34.8 libidn2/2.3.8 libpsl/0.21.5 nghttp2/1.69.0
```

The first `curl` line comes from the build (`#5 0.786` is the step and the time), the second from a container of the
finished image. `--no-cache` tells `apk` not to keep its package index in the image; on Debian and Ubuntu the same idea
is `apt-get update && apt-get install -y --no-install-recommends … && rm -rf /var/lib/apt/lists/*`, **in one `RUN`**
(lesson 017 explains why a later `rm` would not help).

## Command breakdown

| Form / option | Meaning |
|---|---|
| `RUN command args` | shell form: `/bin/sh -c "command args"`, so `&&`, `\|`, `$VAR` work |
| `RUN ["prog", "arg"]` | exec form: runs `prog` directly; no shell, no variable expansion |
| `&&` | run the next command only if the previous one succeeded |
| `\` at the end of a line | continue the instruction on the next line |
| `set -eux` | in a long script: stop on errors (`e`), on unset variables (`u`), print each command (`x`) |
| `docker build --progress=plain` | show the full output of each step |

## Hands-on lab

**Instructions.** Build `run-demo:tools` from `alpine:3.23` with `curl` **and** `jq` installed in a single `RUN` step,
then run `jq --version` in it.

**Expected result.** `jq-1.` followed by the version.

**Verification.**

<!-- test: contains=jq-1. -->
```bash
cd ~/docker-practice/lesson-026
printf 'FROM alpine:3.23\nRUN apk add --no-cache curl jq\n' > Dockerfile.tools
docker build -q -f Dockerfile.tools -t run-demo:tools . > /dev/null
docker run --rm run-demo:tools jq --version
```

## Break it

A typing error in a package name:

<!-- test: contains=no such package; output -->
```bash
printf 'FROM alpine:3.23\nRUN apk add --no-cache curll\n' > Dockerfile.broken
docker build --progress=plain -f Dockerfile.broken -t run-demo:broken . 2>&1 | grep -E 'ERROR|curll'
```

```text
#5 [2/2] RUN apk add --no-cache curll
#5 0.630 ERROR: unable to select packages:
#5 0.630   curll (no such package):
#5 0.630     required by: world[curll]
#5 ERROR: process "/bin/sh -c apk add --no-cache curll" did not complete successfully: exit code: 1
 > [2/2] RUN apk add --no-cache curll:
0.630 ERROR: unable to select packages:
0.630   curll (no such package):
0.630     required by: world[curll]
   2 | >>> RUN apk add --no-cache curll
ERROR: failed to build: failed to solve: process "/bin/sh -c apk add --no-cache curll" did not complete successfully: exit code: 1
```

## Troubleshoot it

Two kinds of lines: the step's own output (`#5 0.582 ERROR: unable to select packages: curll (no such package)`), and
Docker's summary (`process "/bin/sh -c apk add --no-cache curll" did not complete successfully: exit code: 1`). Docker
only knows the command exited with 1; the reason is always in the step's output just above, which is why
`--progress=plain` matters when a build fails. Reproduce the step interactively in a container of the base image to
investigate:

<!-- test: contains=curl-8; output=head:3 -->
```bash
docker run --rm alpine:3.23 sh -c 'apk update -q && apk search curl | grep "^curl-[0-9]"'
```

```text
curl-8.22.0-r0
```

## Fix it

<!-- test: contains=curl 8 -->
```bash
sed -i.bak 's/curll/curl/' Dockerfile.broken && rm Dockerfile.broken.bak
docker build -q -f Dockerfile.broken -t run-demo:fixed . > /dev/null
docker run --rm run-demo:fixed curl --version | head -1
```

## Practice challenge

`/bin/sh -c` only reports the exit status of the **last** command of a pipeline. Show that this step passes although
its first command fails, then make it fail correctly:

```text
RUN false | echo "pipeline finished"
```

<details>
<summary>Solution</summary>

<!-- test: contains=hidden failure: built; contains=pipefail: build failed; output -->
```bash
cd ~/docker-practice/lesson-026
printf 'FROM alpine:3.23\nRUN false | echo "pipeline finished"\n' > Dockerfile.pipe
docker build -q -f Dockerfile.pipe -t run-demo:pipe . > /dev/null && echo "hidden failure: built"
printf 'FROM alpine:3.23\nRUN set -o pipefail && false | echo "pipeline finished"\n' > Dockerfile.pipefail
docker build -q -f Dockerfile.pipefail -t run-demo:pipefail . > /dev/null 2>&1 || echo "pipefail: build failed"
```

```text
hidden failure: built
pipefail: build failed
```

`set -o pipefail` makes a pipeline fail when any part of it fails. It matters for steps like
`RUN wget -O- https://… | tar -xz`: without it, a failed download can still produce a "successful" layer.

</details>

## Real-world example

Production Dockerfiles group related commands into one `RUN` per concern (system packages, then the application's
dependencies), pin package versions where reproducibility matters (`apk add curl=8.17.0-r1`), and remove caches in the
same step. When a CI build fails, the first thing a reviewer reads is the failing step's own output in the plain build
log, not Docker's one-line summary.

## Recap

- `RUN` executes at build time; each `RUN` adds a layer; a non-zero exit status stops the build.
- Shell form uses `/bin/sh -c`; exec form runs the program directly.
- Chain with `&&` and clean caches in the same step; use `--no-cache` with `apk`.
- The real error is in the step's own output (`--progress=plain`); use `set -o pipefail` with pipes.

## Cleanup

<!-- test -->
```bash
docker image rm -f run-demo run-demo:tools run-demo:fixed run-demo:pipe > /dev/null
rm -rf ~/docker-practice/lesson-026
```

Next: [Lesson 027 · CMD](../027-cmd/README.md)
