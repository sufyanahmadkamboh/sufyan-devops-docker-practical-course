# Lesson 105 · Build cache optimization

> Level 17 · Advanced Docker · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

Lesson 039 explained the build cache: a step is reused when it and everything before it are unchanged. This lesson
applies it to make real builds fast:

1. **Order** steps from least to most frequently changed: dependencies before code.
2. Copy **only** what a step needs (`COPY requirements.txt` before `COPY . .`).
3. Use **cache mounts** (`RUN --mount=type=cache`) so package managers keep their downloads between builds.
4. Put values that change on every build (time, commit) **last**.

## Visual

```text
  Before                                   After
  FROM python:3.14-slim        cached      FROM python:3.14-slim                       cached
  COPY . .                     ✗ changed   COPY requirements.txt .                     cached
  RUN pip install …            ✗ re-runs   RUN --mount=type=cache… pip install …       cached
                                 (downloads everything again)
                                           COPY . .                                    ✗ changed (only this)
  one changed line of app.py               one changed line of app.py
  → every step after COPY . . runs again   → only the last, cheap step runs again

  ARG BUILD_TIME at the top  →  every RUN after it re-runs on every build   (put it at the end)
```

## Lab setup

The Flask API from lesson 002, with four Dockerfiles and a helper that reports, for every step, whether the build
took it from the cache:

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-105 examples/python-api
cp 16-advanced/105-cache-optimization/examples/* ~/docker-practice/lesson-105/
bash scripts/lab.sh lesson-105-node examples/node-api
cd ~/docker-practice/lesson-105
ls
```

`lesson-105-node` holds the Node.js API for the practice challenge. `sh build-steps.sh ARGS` runs
`docker build --progress plain ARGS` and prints `cached` or `ran` for every step (`base` for `FROM`).

## Demonstration

Build the `before` version twice. The second time, nothing changed, so everything is cached:

<!-- test: contains=cached; output -->
```bash
sh build-steps.sh -f Dockerfile.before -t cafe-api:before . > /dev/null
sh build-steps.sh -f Dockerfile.before -t cafe-api:before .
```

```text
base   [1/4] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7
cached [2/4] WORKDIR /app
cached [3/4] COPY . .
cached [4/4] RUN pip install --no-cache-dir -r requirements.txt
```

Now change one line of the application code, as every commit does, and build again:

<!-- test: contains=ran    [4/4] RUN pip install; output -->
```bash
echo "# change 1" >> app.py
sh build-steps.sh -f Dockerfile.before -t cafe-api:before .
```

```text
base   [1/4] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7
cached [2/4] WORKDIR /app
ran    [3/4] COPY . .
ran    [4/4] RUN pip install --no-cache-dir -r requirements.txt
```

`COPY . .` changed, so the dependency installation ran again: every package was downloaded and installed for a
change that did not touch the dependencies. Do the same with the `after` version:

<!-- test: contains=cached [4/5] RUN --mount=type=cache; contains=ran    [5/5] COPY . .; output -->
```bash
sh build-steps.sh -f Dockerfile.after -t cafe-api:after . > /dev/null
echo "# change 2" >> app.py
sh build-steps.sh -f Dockerfile.after -t cafe-api:after .
```

```text
base   [1/5] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7
cached [2/5] WORKDIR /app
cached [3/5] COPY requirements.txt .
cached [4/5] RUN --mount=type=cache,target=/root/.cache/pip pip install -r re
ran    [5/5] COPY . .
```

Only the last step ran.

## Command breakdown

| Technique | Dockerfile |
|---|---|
| dependencies first | `COPY requirements.txt .` → `RUN pip install …` → `COPY . .` |
| cache mount | `RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt` |
| changing values last | `ARG BUILD_TIME` + `LABEL …` at the end |
| keep the context small | `.dockerignore` (lesson 037): changes to ignored files never invalidate `COPY . .` |
| share cache in CI | `docker buildx build --cache-to type=registry,… --cache-from type=registry,…` |

The same order works for every stack: `package.json` + `package-lock.json` → `npm ci`; `go.mod` + `go.sum` →
`go mod download`; `pom.xml` → `mvn dependency:go-offline`; `composer.json` + `composer.lock` → `composer install`.

## Hands-on lab

**Instructions.** Change `requirements.txt` by adding a comment line, rebuild the `after` version, and check the output
of the pip step: with the cache mount, pip reuses the packages it downloaded before.

**Expected result.** The pip step runs (its input changed), but pip prints `Using cached` for the packages.

**Verification.**

<!-- test: contains=Using cached -->
```bash
echo "# pinned versions, reviewed" >> requirements.txt
docker build --progress plain -f Dockerfile.after -t cafe-api:after . 2>&1 | grep -m 3 'Using cached'
```

## Break it

A teammate adds the build time to the image, at the top of the Dockerfile where it is easy to find. CI passes the time
on every build:

<!-- test: contains=BUILD_TIME; output -->
```bash
head -4 Dockerfile.broken
```

```text
FROM python:3.14-slim
# build metadata, added "at the top, where it is easy to find"
ARG BUILD_TIME
RUN echo "built at ${BUILD_TIME}" > /build-info.txt
```

<!-- test: contains=ran    [5/6] RUN --mount=type=cache; output -->
```bash
sh build-steps.sh -f Dockerfile.broken --build-arg BUILD_TIME=1001 -t cafe-api:broken . > /dev/null
sh build-steps.sh -f Dockerfile.broken --build-arg BUILD_TIME=1002 -t cafe-api:broken .
```

```text
base   [1/6] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7
ran    [2/6] RUN echo "built at 1002" > /build-info.txt
ran    [3/6] WORKDIR /app
ran    [4/6] COPY requirements.txt .
ran    [5/6] RUN --mount=type=cache,target=/root/.cache/pip pip install -r re
ran    [6/6] COPY . .
```

Nothing changed in the code or the dependencies, but almost every step ran again.

## Troubleshoot it

Find the **first** step that ran; everything after it runs because of it. Here it is step 2: `RUN echo "built at
${BUILD_TIME}"`. An `ARG` value is part of the cache key of every `RUN` step after its declaration, because those steps
can read it as an environment variable. A new value on every build = a cache miss on every build from there on.

The same diagnosis applies to other cache busters: a `COPY . .` early in the file, a file that changes on every build
(a log, a timestamp, `.git/`) in the build context, or `--no-cache` left in a script.

## Fix it

Declare the changing value as late as possible, and use it only where it is needed (a label, see `Dockerfile.fixed`):

<!-- test: contains=cached [4/5] RUN --mount=type=cache; output -->
```bash
sh build-steps.sh -f Dockerfile.fixed --build-arg BUILD_TIME=1001 -t cafe-api:fixed . > /dev/null
sh build-steps.sh -f Dockerfile.fixed --build-arg BUILD_TIME=1002 -t cafe-api:fixed .
docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.created"}}' cafe-api:fixed
```

```text
base   [1/5] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7
cached [2/5] WORKDIR /app
cached [3/5] COPY requirements.txt .
cached [4/5] RUN --mount=type=cache,target=/root/.cache/pip pip install -r re
cached [5/5] COPY . .
1002
```

Every step is cached; only the label (metadata, no layer) changed.

## Practice challenge

Apply the technique to the Node.js API in `~/docker-practice/lesson-105-node`: write a Dockerfile that installs
dependencies with `npm ci` from `package.json` and `package-lock.json` alone, then copies the code, and prove that
changing `server.js` leaves the `npm ci` step cached.

<details>
<summary>Solution</summary>

<!-- test: contains=cached [4/5] RUN --mount=type=cache; output -->
```bash
cd ~/docker-practice/lesson-105-node
cp ~/docker-practice/lesson-105/build-steps.sh .
cat > Dockerfile <<'EOF'
FROM node:24-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev
COPY . .
USER node
CMD ["node", "server.js"]
EOF
sh build-steps.sh -t cafe-node:cache . > /dev/null
echo "// change" >> server.js
sh build-steps.sh -t cafe-node:cache .
```

```text
base   [1/5] FROM docker.io/library/node:24-alpine@sha256:ebfe2f90462722a7a4d
cached [2/5] WORKDIR /app
cached [3/5] COPY package.json package-lock.json ./
cached [4/5] RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev
ran    [5/5] COPY . .
```

`npm ci` (step 4) is cached; only `COPY . .` ran. The `/root/.npm` cache mount keeps npm's downloads for the times
`package-lock.json` does change.

</details>

## Real-world example

A team's CI built a Java service with `COPY . .` as one of the first steps: every commit re-downloaded all Maven
dependencies. Reordering the Dockerfile (`pom.xml` first, `mvn dependency:go-offline`, then the sources) and sharing the
cache between CI runs with `--cache-from`/`--cache-to type=registry` made most builds reuse the dependency layer. How
much that saves depends on the project; measure it with the build times your CI already records, before and after.

## Recap

- One cache miss invalidates every later step: order steps from least to most frequently changed.
- Copy dependency manifests before the code; copy the code last.
- `RUN --mount=type=cache,target=…` keeps package manager caches between builds, outside the image.
- Values that change on every build (`ARG BUILD_TIME`, commit) belong at the end.
- Diagnose with `--progress plain`: the first step that ran is the culprit.

## Cleanup

<!-- test -->
```bash
docker image rm -f cafe-api:before cafe-api:after cafe-api:broken cafe-api:fixed cafe-node:cache > /dev/null 2>&1 || true
docker buildx prune -f > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-105 ~/docker-practice/lesson-105-node
```

Next: [Module 17 · Troubleshooting](../../17-troubleshooting/README.md)
