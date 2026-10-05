# Module 18 assessment · Production

> Lessons [130](130-production-dockerfile/README.md)–[134](134-security-review/README.md) · ⏱ 45 minutes · try every
> question before opening its answer

## Knowledge check

**1. A container is started by a script `start.sh` whose last line is `node server.js`. `docker stop` ends it with exit
code 137. Why, and what are the two fixes?**

<details><summary>Answer</summary>

The shell running the script is process 1 and Node.js is its child. `SIGTERM` goes to process 1 only; the shell does
not pass it on, so after the stop timeout Docker kills everything with `SIGKILL` (137 = 128 + 9) and open requests are
cut off. Fixes: start the application directly with an exec-form `CMD ["node", "server.js"]`, or end the script with
`exec node server.js` so that Node.js replaces the shell as process 1 (lesson 130).

</details>

**2. Why copy `package.json` and the lock file before the rest of the code?**

<details><summary>Answer</summary>

The dependency layer is then rebuilt only when the dependencies change; code changes reuse the cached layer and
builds stay fast (lessons 039, 130).

</details>

**3. A container writes its log to `/var/log/app.log`. Name two problems.**

<details><summary>Answer</summary>

`docker logs` and log collectors only read stdout/stderr, so nobody sees the log; and the file grows in the
container's writable layer and disappears with the container (lesson 131).

</details>

**4. What does `docker diff` show, and why is it useful during an incident review?**

<details><summary>Answer</summary>

The files added, changed or deleted in a container since it started from its image. A changed application or
configuration file means someone patched the running container by hand: the container no longer matches its image
(lesson 132).

</details>

**5. How do you roll back an immutable deployment?**

<details><summary>Answer</summary>

Replace the container with one started from the previous image tag. Nothing is rebuilt (lesson 132).

</details>

**6. Why should a password be a mounted file rather than an environment variable?**

<details><summary>Answer</summary>

Environment variables are visible to anyone who can run `docker inspect`, are inherited by every child process and
often end up in logs and crash reports. A read-only file under `/run/secrets` is none of these (lesson 133).

</details>

**7. A configuration file is mounted, the container runs, but the setting has no effect. What do you check?**

<details><summary>Answer</summary>

Where it is mounted (`docker inspect --format '{{json .Mounts}}'`) and which configuration the application actually
loaded (for Nginx, `nginx -T`): the file is probably mounted to a path the application does not read (lesson 133).

</details>

**8. Name four findings of a security review that you can prove with `docker image inspect` or `docker history`.**

<details><summary>Answer</summary>

Root user (`.Config.User` empty), secrets in `ENV` (`.Config.Env`), `ARG` values used in `RUN` (`docker history
--no-trunc`), a missing healthcheck (`.Config.Healthcheck`), shell-form `CMD` (`.Config.Cmd`) (lesson 134).

</details>

**9. Why can `read_only: true` stop a container from starting, and what is the fix?**

<details><summary>Answer</summary>

Many applications write a few files at startup (Nginx: its cache directories and PID file). Give them a `tmpfs`
exactly at those paths and keep the rest read-only (lesson 134).

</details>

## Practical task

Write a production Dockerfile for `examples/python-api`: `python:3.14-slim`, dependencies installed in their own
layer without a cache, a non-root user, a healthcheck on `/health`, Gunicorn as process 1 in exec form on port 5000.
Build it as `python-api:1.0` and prove the user, the command and that the container becomes `healthy`.

<details><summary>Solution</summary>

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh assessment-18 examples/python-api
cd ~/docker-practice/assessment-18
cat > Dockerfile <<'EOF'
FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
RUN useradd --system --uid 10001 appuser
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health')"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
EOF
printf '__pycache__\n*.pyc\n.env\nDockerfile\n' > .dockerignore
docker build -q -t python-api:1.0 . > /dev/null
docker run -d --name python-api python-api:1.0 > /dev/null
```

<!-- test: retry=15; contains=healthy; contains=user=appuser; output -->
```bash
docker image inspect python-api:1.0 --format 'user={{.Config.User}} cmd={{json .Config.Cmd}}'
docker inspect python-api --format '{{.State.Health.Status}}'
```

```text
user=appuser cmd=["gunicorn","--bind","0.0.0.0:5000","--workers","2","app:app"]
healthy
```

`PYTHONUNBUFFERED=1` makes Python write its logs immediately to stdout (lesson 131); Gunicorn in exec form receives
`SIGTERM` and stops its workers gracefully.

</details>

## Troubleshooting task

The operations team hardened a web server with a read-only file system. It does not start:

<!-- test: contains=web-ro -->
```bash
docker run -d --name web-ro --read-only -p 8080:80 nginx:1.30-alpine > /dev/null
sleep 2
docker ps -a --filter name=web-ro --format '{{.Names}}: {{.Status}}'
```

Find the cause and fix it without giving up the read-only file system.

<details><summary>Solution</summary>

<!-- test: contains=Read-only file system; output=tail:1 -->
```bash
docker logs web-ro 2>&1 | grep -i "read-only" | tail -1
```

```text
nginx: [emerg] mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)
```

Nginx cannot create its directories under `/var/cache/nginx` (and its PID file under `/run`). Give it temporary,
in-memory space exactly there:

<!-- test: retry=10; contains=200 -->
```bash
docker rm -f web-ro > /dev/null
docker run -d --name web-ro --read-only --tmpfs /var/cache/nginx --tmpfs /run -p 8080:80 nginx:1.30-alpine > /dev/null
sleep 1
curl -sI http://localhost:8080/ | head -1
```

</details>

## Real-world scenario

At 2 a.m. a production container's configuration is wrong. An engineer fixes it with `docker exec` and `vi`, and
the service recovers. Two days later, after a routine deployment, the same outage happens again. Explain what
happened and what the team should change.

<details><summary>Model answer</summary>

The fix lived only in the old container's writable layer; the deployment replaced the container with a new one from
the image, which still has the wrong configuration (lesson 132). `docker diff` on the old container would have shown
the hand change. The team should make the change in Git (the configuration file or the environment), build and
deploy a new version, and prevent hand edits: read-only containers (`--read-only`, lesson 084), configuration mounted
read-only (lesson 133), and an incident checklist that ends with "the fix is committed and deployed".

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f python-api web-ro > /dev/null
docker image rm -f python-api:1.0 > /dev/null
rm -rf ~/docker-practice/assessment-18
```
