# Troubleshooting problem 16 · Build failure

> ⏱ 15 minutes · run every command from the course folder · related lessons: 025, 035, 036, 037

## Problem

Someone added a `.dockerignore` to keep a notes file out of the image. Since then, the inventory image does not build:
`requirements.txt: not found`, although the file is right there in the folder.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-16 17-troubleshooting/16-build-failure/examples
cd ~/docker-practice/trouble-16/broken
ls
```

<!-- test: fail; contains=not found; output=tail:8 -->
```bash
docker build -t inventory:broken . 2>&1
```

```text
...
   2 |     WORKDIR /app
   3 | >>> COPY requirements.txt .
   4 |     RUN pip install --no-cache-dir -r requirements.txt
   5 |     COPY app.py .
--------------------
ERROR: failed to build: failed to solve: failed to compute cache key: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::n29kgvywostgjnnm5n99idtwp: "/requirements.txt": not found

View build details: docker-desktop://dashboard/build/default/default/rztbssxpyk8731ygjime52d1h
```

## Investigation

**1. Read the build output from the bottom up.** BuildKit prints the failing step (`[3/5] COPY requirements.txt .`),
the Dockerfile line (`Dockerfile:3`) and the reason: `failed to compute cache key: … "/requirements.txt": not found`.
"Not found" in a `COPY` means: not in the **build context**, the set of files the client sent to the builder
(lesson 036). That is not the same as "not in the folder".

**2. Which files reach the context?** Build a throw-away image that copies the whole context and lists it:

<!-- test: absent=requirements.txt; output -->
```bash
printf 'FROM busybox:1.37\nCOPY . /context\nCMD ["find", "/context", "-type", "f"]\n' > ../context.Dockerfile
docker build -q -f ../context.Dockerfile -t context-check . > /dev/null
docker run --rm context-check
```

```text
/context/Dockerfile
/context/.dockerignore
/context/app.py
```

`Dockerfile`, `app.py` and `.dockerignore` arrive; `requirements.txt` and `notes.txt` do not.

**3. Why?**

<!-- test: contains=*.txt; output -->
```bash
cat .dockerignore
```

```text
# keep notes, logs and local secrets out of the build context
*.txt
*.log
.env
__pycache__/
```

## Commands

| Command | What it tells you |
|---|---|
| `docker build . 2>&1 \| tail` | the failing step, its Dockerfile line and the error |
| `docker build --progress=plain .` | the full output of every step (`RUN` errors, test failures) |
| a `COPY . /context` + `find` image | exactly which files are in the build context |
| `cat .dockerignore` | the patterns that remove files from the context |

## Output interpretation

| Error | Cause |
|---|---|
| `"/FILE": not found` at a `COPY` | the file is not in the context: wrong path, outside the context, or excluded by `.dockerignore` |
| `process "/bin/sh -c …" did not complete successfully: exit code: N` | a `RUN` command failed: read the lines above it |
| `failed to solve: … not found` at `FROM` | the base image or tag does not exist ([problem 25](../25-image-pull-failure/README.md)) |
| `failed to read dockerfile` | wrong `-f` path or build directory |

## Root cause

`.dockerignore` contains `*.txt`, which excludes `requirements.txt` together with `notes.txt`. The Dockerfile's
`COPY requirements.txt .` then finds nothing.

## Fix

Exclude exactly what should not be shipped (or use an exception, `!requirements.txt`, after the pattern):

<!-- test: contains=notes.txt; output -->
```bash
cd ~/docker-practice/trouble-16
grep -v '^#' broken/.dockerignore > /tmp/broken.ignore
grep -v '^#' fixed/.dockerignore | diff /tmp/broken.ignore - || true
```

```text
1c1
< *.txt
---
> notes.txt
```

<!-- test -->
```bash
docker build -q -t inventory:fixed fixed > /dev/null
```

## Verification

The image builds, runs, and still does not contain the notes:

<!-- test: contains=Flask 3.1.3; contains=no notes in the image; output -->
```bash
docker run --rm inventory:fixed
docker run --rm inventory:fixed sh -c 'ls /app; test ! -e /app/notes.txt && echo "no notes in the image"'
```

```text
inventory: ready, Flask 3.1.3
app.py
requirements.txt
no notes in the image
```

## Prevention

- Review `.dockerignore` like code: broad patterns (`*.txt`, `*.json`, `*`) need explicit exceptions.
- An allow-list style is safest for small apps: `*` first, then `!app.py`, `!requirements.txt`, `!src/`.
- Build the image in CI on every pull request, so a broken build is found before merging (lesson 135).

## Cleanup

<!-- test -->
```bash
docker image rm context-check inventory:fixed > /dev/null
rm -f /tmp/broken.ignore
rm -rf ~/docker-practice/trouble-16
```

Next: [Problem 17 · Unexpected cache](../17-unexpected-cache/README.md)
