# Lesson 039 · The build cache

> Level 6 · Docker builds · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

BuildKit remembers every layer it built. Before running a step, it checks whether it has already built **the same
instruction, on the same parent layer, with the same input files**; if so, it reuses the stored layer (`CACHED`) in
milliseconds. As soon as one step changes, that step **and every step after it** must run again. The order of the
Dockerfile therefore decides whether a one-line code change rebuilds in one second or reinstalls all dependencies.

## Visual

```text
  Dockerfile.slow (code before dependencies)        Dockerfile (dependencies before code)

  FROM python:3.14-slim        CACHED               FROM python:3.14-slim          CACHED
  WORKDIR /app                 CACHED               WORKDIR /app                   CACHED
  COPY . .                     ✗ app.py changed     COPY requirements.txt .        CACHED  (unchanged)
  RUN pip install …            ✗ runs again         RUN pip install …              CACHED
  CMD …                                             COPY . .                       ✗ app.py changed
                                                    CMD …
  edit app.py → reinstall every package             edit app.py → copy one file again

  cache key of a step = parent layer + instruction text + checksum of the files it copies
  a miss invalidates every step below it
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-039 examples/python-api
cp 05-builds/039-build-cache/examples/Dockerfile* ~/docker-practice/lesson-039/
cd ~/docker-practice/lesson-039
ls
```

The Flask API from lesson 002 and two Dockerfiles with the same instructions in a different order.

## Demonstration

First build of the well-ordered `Dockerfile`: every step runs. The `grep` keeps the step lines and the `CACHED`
markers of the plain build output:

<!-- test: contains=RUN pip install; output -->
```bash
docker build -t cache-api:1 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)'
```

```text
#5 [1/5] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7a682e7e18676771cb80c6b75b8699af886b2d554ce40151
#6 [2/5] WORKDIR /app
#7 [3/5] COPY requirements.txt .
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#9 [5/5] COPY . .
```

Build again without changing anything:

<!-- test: contains=CACHED; output -->
```bash
docker build -t cache-api:1 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)'
```

```text
#5 [1/5] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7a682e7e18676771cb80c6b75b8699af886b2d554ce40151
#6 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#6 CACHED
#7 [2/5] WORKDIR /app
#7 CACHED
#8 [3/5] COPY requirements.txt .
#8 CACHED
#9 [5/5] COPY . .
#9 CACHED
```

Every step is `CACHED`: nothing ran. Now change the application code, as every commit does:

<!-- test: contains=CACHED; output -->
```bash
sed -i.bak 's/Hello from Python/Hello from Python, version 2/' app.py && rm app.py.bak
docker build -t cache-api:2 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)'
```

```text
#5 [1/5] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7a682e7e18676771cb80c6b75b8699af886b2d554ce40151
#6 [2/5] WORKDIR /app
#6 CACHED
#7 [3/5] COPY requirements.txt .
#7 CACHED
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 CACHED
#9 [5/5] COPY . .
```

The dependencies stayed cached; only the last `COPY` ran. (`sed -i.bak … && rm *.bak` edits a file in place on both
GNU/Linux and macOS.)

## Command breakdown

| Command / output | Meaning |
|---|---|
| `#N CACHED` | step N was reused from the cache |
| a step without `CACHED` | it ran; so does every later step |
| `docker build --no-cache` | ignore the cache for every step |
| `docker build --no-cache-filter STAGE` | ignore it for one stage only (multi-stage, lesson 087) |
| `docker builder du` / `docker builder prune` | how much disk the cache uses / delete it |

## Hands-on lab

**Instructions.** With the well-ordered `Dockerfile`, add a new dependency line to `requirements.txt`
(`itsdangerous==2.2.0`, which Flask already uses) and rebuild. Which steps run?

**Expected result.** `COPY requirements.txt`, `RUN pip install` and `COPY . .` run again (the input of step 3 changed,
so everything after it is invalid); `WORKDIR` stays cached. The second `grep -A1` shows the `pip` step and the line
after it: no `CACHED`.

**Verification.**

<!-- test: contains=RUN pip; absent=CACHED -->
```bash
cd ~/docker-practice/lesson-039
echo "itsdangerous==2.2.0" >> requirements.txt
docker build -t cache-api:3 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)' | grep -A1 'RUN pip'
```

## Break it

The same code change with `Dockerfile.slow`, which copies everything before installing. Build it once, change one line
of `app.py`, and build again:

<!-- test: contains=RUN pip; output -->
```bash
docker build -f Dockerfile.slow -t cache-api:slow . > /dev/null 2>&1
sed -i.bak 's/version 2/version 3/' app.py && rm app.py.bak
docker build -f Dockerfile.slow -t cache-api:slow . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)'
```

```text
#4 [1/4] FROM docker.io/library/python:3.14-slim@sha256:c3e521df8b2b498a7a682e7e18676771cb80c6b75b8699af886b2d554ce40151
#6 [2/4] WORKDIR /app
#6 CACHED
#7 [3/4] COPY . .
#8 [4/4] RUN pip install --no-cache-dir -r requirements.txt
```

## Troubleshoot it

A one-line code change reinstalled every Python package. Read the steps top-down and find the **first** one that is
not `CACHED`: `[3/4] COPY . .`. Its input (the whole folder) changed because `app.py` changed, so its cache key
changed, and from that point on nothing can be reused, including `pip install`, whose own input did not change at all.
Compare the two orders:

<!-- test: contains=COPY -->
```bash
grep -nE '^(COPY|RUN)' Dockerfile.slow Dockerfile
```

## Fix it

Order the steps from "changes rarely" to "changes often": base image, system packages, dependency manifests
(`requirements.txt`, `package*.json`, `go.mod`/`go.sum`, `pom.xml`), dependency installation, and the code last. That
is exactly `Dockerfile`. The same code change with it:

<!-- test: contains=CACHED -->
```bash
docker build -t cache-api:4 . > /dev/null 2>&1
sed -i.bak 's/version 3/version 4/' app.py && rm app.py.bak
docker build -t cache-api:4 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)' | grep -A1 'RUN pip'
```

## Practice challenge

The cache key includes the files' **content**, not their timestamps. Prove it: `touch app.py` (new modification time,
same content) and rebuild `cache-api:4`. Is `COPY . .` cached?

<details>
<summary>Solution</summary>

<!-- test: contains=CACHED; output -->
```bash
cd ~/docker-practice/lesson-039
touch app.py
docker build -t cache-api:4 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)' | grep -A1 'COPY \. \.'
```

```text
#9 [5/5] COPY . .
#9 CACHED
```

Cached: BuildKit checksums the files' content and metadata it cares about, not the modification time. A `git checkout`
of the same commit on a CI machine therefore reuses the cache, as long as the cache is available there (lesson 105).

</details>

## Real-world example

A team's pipeline takes 9 minutes per commit, almost all of it in `RUN npm ci`. The Dockerfile starts with
`COPY . .`. Moving `COPY package.json package-lock.json ./` and `RUN npm ci` above `COPY . .` turns most builds into a
cached dependency layer plus a few seconds of copying. The pipeline also needs a cache that survives between jobs
(a registry cache or the CI provider's cache: lessons 105, 136); the right order is what makes that cache useful.

## Recap

- A step is reused when its parent layer, instruction and input files are unchanged.
- The first cache miss invalidates every later step.
- Order Dockerfiles from rarely-changing to often-changing: dependencies before code.
- `--no-cache` forces a full rebuild; `docker builder prune` frees the cache's disk space.

## Cleanup

<!-- test -->
```bash
docker image rm -f cache-api:1 cache-api:2 cache-api:3 cache-api:4 cache-api:slow > /dev/null
rm -rf ~/docker-practice/lesson-039
```

Next: [Lesson 040 · Containerizing a Node.js application](../../06-application-containerization/040-containerize-node/README.md)
