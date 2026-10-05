<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 039 · The build cache · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The same code change with `Dockerfile.slow`, which copies everything before installing. Build it once, change one line
of `app.py`, and build again:

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

```bash
grep -nE '^(COPY|RUN)' Dockerfile.slow Dockerfile
```

## Fix it

Order the steps from "changes rarely" to "changes often": base image, system packages, dependency manifests
(`requirements.txt`, `package*.json`, `go.mod`/`go.sum`, `pom.xml`), dependency installation, and the code last. That
is exactly `Dockerfile`. The same code change with it:

```bash
docker build -t cache-api:4 . > /dev/null 2>&1
sed -i.bak 's/version 3/version 4/' app.py && rm app.py.bak
docker build -t cache-api:4 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)' | grep -A1 'RUN pip'
```
