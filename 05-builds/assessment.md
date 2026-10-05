# Module 05 assessment · Docker builds

> Lessons [035](035-docker-build/README.md)–[039](039-build-cache/README.md) · ⏱ 40 minutes · try every question
> before opening its answer

## Knowledge check

**1. What is the build context, and what can `COPY` read?**

<details><summary>Answer</summary>

The folder (or archive, or URL) passed as the last argument of `docker build`. `COPY` and `ADD` can only read files
inside it; `../` cannot leave it (lesson 036).

</details>

**2. You keep a Dockerfile at `docker/api.Dockerfile` and the code at the repository root. Which command builds it?**

<details><summary>Answer</summary>

From the repository root: `docker build -f docker/api.Dockerfile -t api:1.0 .` The context is `.`, the Dockerfile is
chosen with `-f`, and its `COPY` paths are relative to the context (lessons 035, 036).

</details>

**3. Why does `*.log` in `.dockerignore` not exclude `logs/app.log`?**

<details><summary>Answer</summary>

`.dockerignore` patterns are anchored at the context root, unlike `.gitignore`. Use `**/*.log` (lesson 037).

</details>

**4. Name three kinds of files that belong in `.dockerignore`.**

<details><summary>Answer</summary>

Secrets and local configuration (`.env`, `*.pem`), junk (`.git`, logs, editor folders), and things the image builds
itself (`node_modules`, `dist/`, `__pycache__`) (lesson 037).

</details>

**5. A Dockerfile downloads a 200 MB archive in one `RUN` and deletes it in the next. How big is the image's share of it?**

<details><summary>Answer</summary>

The full 200 MB: the archive stays in the first layer; the deletion only adds a whiteout in a later layer. Download,
use and delete in the same `RUN` (lesson 038).

</details>

**6. Which instructions create file system layers?**

<details><summary>Answer</summary>

`RUN`, `COPY` and `ADD` (BuildKit also records a small layer for a `WORKDIR` that creates a folder). `CMD`, `ENV`,
`EXPOSE`, `USER`, `LABEL` only change metadata (lesson 038).

</details>

**7. What makes up the cache key of a step, and what happens after the first cache miss?**

<details><summary>Answer</summary>

The parent layer, the instruction and the checksums of the files it copies. After the first miss, every following
step runs again (lesson 039).

</details>

**8. Why copy `requirements.txt` (or `package*.json`) before the rest of the code?**

<details><summary>Answer</summary>

So the dependency installation is cached until the dependency list changes; code changes then only rerun the final
`COPY` (lesson 039).

</details>

## Practical task

In a lab folder with the course's Python API (`bash scripts/lab.sh assessment-05 examples/python-api`), create a fake
secret `.env`, then write a `Dockerfile` and a `.dockerignore` so that:

1. the image `assess-api:1.0` contains no `.env`,
2. after changing `app.py`, a rebuild reuses the cached `pip install` step.

<details><summary>Solution</summary>

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh assessment-05 examples/python-api
cd ~/docker-practice/assessment-05
printf 'SECRET_KEY=example-secret-change-me\n' > .env
```

<!-- test: contains=no .env; contains=CACHED -->
```bash
cat > Dockerfile <<'EOF'
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
EOF
printf '.env\n__pycache__\nDockerfile\n.dockerignore\n' > .dockerignore
docker build -q -t assess-api:1.0 . > /dev/null
docker run --rm assess-api:1.0 ls -a /app | grep -q '^.env$' && echo ".env leaked" || echo "no .env in the image"
echo "# a code change" >> app.py
docker build -t assess-api:1.0 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)' | grep -A1 'RUN pip'
```

</details>

## Troubleshooting task

A teammate added a `.dockerignore` to keep text files such as notes and logs out of the image. Since then the build
fails. Reproduce it:

<!-- test: fail; contains=requirements.txt; output -->
```bash
cd ~/docker-practice/assessment-05
printf '.env\n*.txt\n' > .dockerignore
docker build -t assess-api:broken . 2>&1 | grep ERROR | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
ERROR: failed to build: failed to solve: failed to compute cache key: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::5vqvh6yn3d7j9r948b03nq0zr: "/requirements.txt": not found
```

Explain the error and fix it without giving up the exclusion of other `.txt` files.

<details><summary>Solution</summary>

`"/requirements.txt": not found` although the file exists: `*.txt` in `.dockerignore` removed it from the context
before `COPY requirements.txt .` ran. Add an exception after the pattern (later lines win):

<!-- test: contains=assess-api:fixed -->
```bash
printf '.env\n*.txt\n!requirements.txt\n' > .dockerignore
docker build -q -t assess-api:fixed . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' assess-api
```

</details>

## Real-world scenario

Every pipeline run of a Node.js service takes 11 minutes, of which 9 are `RUN npm ci`, even for one-line changes. The
Dockerfile begins with `FROM node:24-alpine`, `WORKDIR /app`, `COPY . .`, `RUN npm ci`. The repository also contains
a 600 MB `test-fixtures/` folder. What do you change, and how do you prove the improvement?

<details><summary>Model answer</summary>

1. Reorder: `COPY package.json package-lock.json ./`, `RUN npm ci`, then `COPY . .`, so the install is cached until the
   lockfile changes (lesson 039).
2. Add a `.dockerignore` with `node_modules`, `.git`, `test-fixtures/` and secrets, so `COPY . .` neither transfers
   nor bakes in 600 MB (lessons 036, 037).
3. Make the cache available in CI (a registry or CI cache backend, lesson 105); without it, every CI machine starts cold.

Proof: compare the build logs before and after (`CACHED` on the `npm ci` step, the `transferring context` size) and the
pipeline durations of several runs, not a single one.

</details>

## Cleanup

<!-- test -->
```bash
docker image rm -f assess-api:1.0 assess-api:fixed > /dev/null 2>&1 || true
rm -rf ~/docker-practice/assessment-05
```
