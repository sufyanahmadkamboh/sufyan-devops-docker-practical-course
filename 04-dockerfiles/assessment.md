# Module 04 assessment · Dockerfiles

> Lessons [022](022-first-dockerfile/README.md)–[034](034-dockerfile-best-practices/README.md) · ⏱ 45 minutes · try
> every question before opening its answer

## Knowledge check

**1. What is the build context, and why can `COPY ../file .` not work?**

<details><summary>Answer</summary>

The folder passed to `docker build` (the `.`): only its files are sent to the builder, and `COPY` paths are relative
to it. `..` cannot leave it. Choose a larger context and select the Dockerfile with `-f` (lessons 022, 025).

</details>

**2. Why does `RUN cd /app` followed by `RUN touch notes.txt` not create `/app/notes.txt`?**

<details><summary>Answer</summary>

Each `RUN` starts a new shell in the working directory; the `cd` ended with its step. `WORKDIR /app` sets the directory
for all later steps and the container (lesson 024).

</details>

**3. When should you use `ADD` instead of `COPY`?**

<details><summary>Answer</summary>

Only to unpack a local tar archive into the image or to download a URL (with `--checksum`). For plain files, `COPY`
(lesson 025).

</details>

**4. A `RUN wget -O- URL | tar -xz` step "succeeds" although the download failed. Why, and what fixes it?**

<details><summary>Answer</summary>

`/bin/sh -c` returns the exit status of the last command of the pipeline (`tar`). `set -o pipefail` makes the whole
pipeline fail (lesson 026).

</details>

**5. `CMD ['npm', 'start']` makes the container fail with `not found`. What happened?**

<details><summary>Answer</summary>

Single quotes are not JSON, so Docker treated the line as shell form: `/bin/sh -c "['npm', 'start']"`. Use double
quotes (lesson 027).

</details>

**6. An image has `ENTRYPOINT ["price"]` and `CMD ["espresso"]`. What runs for `docker run IMAGE`,
`docker run IMAGE latte` and `docker run --entrypoint sh IMAGE`?**

<details><summary>Answer</summary>

`price espresso`; `price latte`; `sh` (the new entrypoint, with the image's `CMD` cleared) (lessons 028, 029).

</details>

**7. What is the difference between `ARG` and `ENV`, and can either hold a password?**

<details><summary>Answer</summary>

`ARG` exists only during the build (`--build-arg`); `ENV` is stored in the image and set in every container (overridable
with `-e`). Neither may hold secrets: `ENV` is in the image configuration, and `ARG` values used by `RUN` are in the
history. Use build secrets (`--secret`) and run-time secret stores (lessons 030, 031).

</details>

**8. Does `EXPOSE 8080` make the application reachable from your computer?**

<details><summary>Answer</summary>

No. It documents the port. Publishing needs `-p HOST:CONTAINER` (or `-P`, which uses the exposed ports) (lesson 032).

</details>

**9. After adding `USER appuser`, the application fails with `Permission denied` when writing its data. What is the right
fix?**

<details><summary>Answer</summary>

Give the user a writable data folder (`RUN mkdir /app/data && chown appuser /app/data`, or `COPY --chown`), keep the
code owned by root; never switch back to root (lesson 033).

</details>

**10. Why copy `package.json` and the lock file before the rest of the code?**

<details><summary>Answer</summary>

The dependency installation layer then only depends on those files: a code change reuses it from the cache instead of
re-installing every dependency (lesson 034, in depth in lesson 039).

</details>

## Practical task

Containerise the Python API of `examples/python-api` (Flask, `app.py`, `requirements.txt`) following the module's
practices: pinned `python:3.14-slim` base, `WORKDIR`, dependencies before code, no pip cache, a non-root user with a
numeric ID, `EXPOSE`, and an exec-form `CMD` that runs `gunicorn --bind 0.0.0.0:8000 app:app`. Run it on port 8090 and
fetch `/health`.

<details><summary>Solution</summary>

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh assessment-04 examples/python-api
cd ~/docker-practice/assessment-04
cat > Dockerfile <<'EOF'
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN useradd --system --uid 10001 appuser
USER 10001
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
EOF
docker build -q -t cafe-py:1.0 . > /dev/null
docker run -d --name cafe-py -p 8090:8000 cafe-py:1.0 > /dev/null
```

<!-- test: retry=15; contains="status":"ok"; contains=uid=10001; output -->
```bash
curl -s http://localhost:8090/health
docker exec cafe-py id
```

```text
{"status":"ok"}
uid=10001(appuser) gid=999(appuser) groups=999(appuser)
```

<!-- test: contains=no warnings -->
```bash
docker build --check . 2>&1 | tail -1
```

</details>

## Troubleshooting task

This Dockerfile builds, but the container does not do what it should. Build it, find **all three** problems, and fix
them so that `docker run --rm IMAGE cappuccino` prints `order: cappuccino` as the user `nobody`.

<!-- test: contains=lab ready -->
```bash
mkdir -p ~/docker-practice/assessment-04-broken && cd ~/docker-practice/assessment-04-broken
cat > Dockerfile <<'EOF'
FROM alpine:3.23
ARG GREETING=order
RUN mkdir /app && cd /app
RUN printf '#!/bin/sh\necho "$GREETING: $1"\n' > order.sh && chmod +x order.sh
ENTRYPOINT ./order.sh
EOF
docker build -q -t orders:broken . > /dev/null && echo "lab ready"
docker run --rm orders:broken cappuccino || true
```

<details><summary>Solution</summary>

1. `RUN cd /app` does not persist: `order.sh` was written to `/`, and the relative `./order.sh` only works by
   accident. Use `WORKDIR /app`.
2. `ENTRYPOINT ./order.sh` is shell form: the argument `cappuccino` is lost. Use the exec form.
3. `GREETING` is an `ARG`: it does not exist when the container runs, so the script prints `: `. Use `ENV` (here from
   the argument). And the image runs as root: add `USER nobody`.

<!-- test: contains=order: cappuccino; contains=nobody; output -->
```bash
cd ~/docker-practice/assessment-04-broken
cat > Dockerfile <<'EOF'
FROM alpine:3.23
ARG GREETING=order
ENV GREETING=$GREETING
WORKDIR /app
RUN printf '#!/bin/sh\necho "$GREETING: $1"\n' > order.sh && chmod +x order.sh
USER nobody
ENTRYPOINT ["./order.sh"]
EOF
docker build -q -t orders:fixed . > /dev/null
docker run --rm orders:fixed cappuccino
docker run --rm --entrypoint whoami orders:fixed
```

```text
order: cappuccino
nobody
```

</details>

## Real-world scenario

A new service's Dockerfile, written quickly, is `FROM node`, `COPY . .`, `RUN npm install`, `CMD npm start`. It runs
as root, the image is 1.2 GB, every code change takes four minutes to build, and the CI log shows
`SecretsUsedInArgOrEnv` because the npm registry token is passed with `--build-arg`. Write the review comments you would
leave on this pull request.

<details><summary>Model answer</summary>

- `FROM node` is `node:latest`: pin a version and a small variant (`node:24-alpine` or `-slim`) (lessons 021, 023).
- `COPY . .` before `npm install` re-installs all dependencies on every code change: copy `package.json` and the lock
  file first, run `npm ci`, then copy the code (lesson 034); add a `.dockerignore` for `node_modules`, `.git` and local
  files (lesson 037).
- The npm token is visible in the image history: pass it as a build secret (`RUN --mount=type=secret,id=npmrc …`,
  `docker build --secret`) (lesson 031).
- Add `USER node` (or a numeric non-root user) and make only the data folder writable (lesson 033).
- `CMD npm start` is shell form and adds npm as an extra process between Docker and the application: use
  `CMD ["node", "server.js"]` (lesson 027).
- Run `docker build --check` in CI so these regressions are caught automatically; consider a multi-stage build to
  remove build tools from the final image (lesson 087).

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f cafe-py > /dev/null
docker image rm -f cafe-py:1.0 orders:broken orders:fixed > /dev/null
rm -rf ~/docker-practice/assessment-04 ~/docker-practice/assessment-04-broken
```
