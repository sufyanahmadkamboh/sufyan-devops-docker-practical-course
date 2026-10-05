# Project 02 · Production Node.js API

> ⏱ 1 hour · run every command from the course folder

## Goal

Package the Node.js API ([examples/node-api](../../examples/node-api)) the way a team would run it in production:
dependencies installed exactly as locked, a multi-stage build, a non-root user, a healthcheck, and a container that
shuts down **gracefully** when Docker (or Kubernetes) stops it.

## Requirements

- [ ] Dependencies come from `package-lock.json` with `npm ci --omit=dev`, in a separate build stage
- [ ] The application runs as the `node` user, with `NODE_ENV=production`
- [ ] A healthcheck calls `/health`; Docker reports the container **healthy**
- [ ] `docker stop` ends the container in well under a second with exit code 0 (SIGTERM is handled)
- [ ] Configuration (`GREETING`, `APP_VERSION`) comes from environment variables, not from the image

## Architecture

```text
 Dockerfile                                         container node-api
 ┌──────────────────────────────┐                   ┌──────────────────────────────────┐
 │ stage deps   node:24-alpine  │                   │ PID 1: node server.js (user node)│
 │   npm ci --omit=dev          │──node_modules──┐  │   :3000  /  /health              │
 └──────────────────────────────┘                ▼  │                                  │
 ┌──────────────────────────────┐   image        │  │ docker stop ──SIGTERM──▶ node    │
 │ final        node:24-alpine  │──────────────────▶│   server.close() → exit 0        │
 │   node_modules + server.js   │                   └──────────────────────────────────┘
 └──────────────────────────────┘
```

## Build it

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh project-02 examples/node-api
cp -r 21-projects/02-node-api/solution/. ~/docker-practice/project-02/
cd ~/docker-practice/project-02
ls -A
```

<!-- test: contains=npm ci; output -->
```bash
cat Dockerfile
```

```text
# syntax=docker/dockerfile:1
# Stage 1: install the production dependencies exactly as locked (npm ci). npm and its cache stay in this stage.
FROM node:24-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
# (mkdir: this API has no dependencies yet, and npm ci creates no node_modules folder then)
RUN npm ci --omit=dev && mkdir -p node_modules

# Stage 2: the runtime: Node.js, the dependencies and the code, as the unprivileged "node" user.
FROM node:24-alpine
ENV NODE_ENV=production PORT=3000
WORKDIR /app
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
COPY --chown=node:node package.json server.js ./
USER node
EXPOSE 3000
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:3000/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"]
# exec form: node is process 1 and receives SIGTERM from docker stop directly
CMD ["node", "server.js"]
```

Two details matter most. `CMD ["node", "server.js"]` is the **exec form**: Node.js is process 1 and receives signals
itself (`npm start` or a shell in between would receive them instead). And `.dockerignore` keeps a local
`node_modules` out of the build context, so the image always gets the locked dependencies.

<!-- test: contains=node-api -->
```bash
docker build -q -t node-api:1.0 . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}} {{.Size}}' node-api
```

<!-- test -->
```bash
docker run -d --name node-api -p 8082:3000 -e GREETING="Hello from production" -e APP_VERSION=1.0.0 node-api:1.0 > /dev/null
```

## Verify

<!-- test: contains=Hello from production; retry=10; output -->
```bash
curl -s http://localhost:8082/
```

```text
{"message":"Hello from production","hostname":"466e0f6f7f6e","version":"1.0.0"}
```

<!-- test: contains=node production; output -->
```bash
docker exec node-api sh -c 'echo "$(id -un) $NODE_ENV"'
docker exec node-api ps -o pid,user,args
```

```text
node production
PID   USER     COMMAND
    1 node     {MainThread} node server.js
   21 node     ps -o pid,user,args
```

Process 1 is `node server.js`, as user `node`. Health:

<!-- test: contains=healthy; retry=15 -->
```bash
docker inspect --format '{{.State.Health.Status}}' node-api
```

Graceful shutdown: `docker stop` sends SIGTERM, the server's handler closes it, and Node.js exits with 0:

<!-- test: contains=exit code 0; output -->
```bash
start=$(date +%s)
docker stop node-api > /dev/null
echo "stopped after $(( $(date +%s) - start )) s, exit code $(docker inspect --format '{{.State.ExitCode}}' node-api)"
```

```text
stopped after 0 s, exit code 0
```

## Break it and fix it

[solution/Dockerfile.broken](solution/Dockerfile.broken) changes only the start command, to run through a shell (a
common way to log a crash):

<!-- test: contains=node-api crashed -->
```bash
grep CMD Dockerfile.broken
docker build -q -t node-api:broken -f Dockerfile.broken . > /dev/null
docker run -d --name node-api-broken node-api:broken > /dev/null
sleep 2
```

<!-- test: contains=exit code 137; output -->
```bash
start=$(date +%s)
docker stop node-api-broken > /dev/null
echo "stopped after $(( $(date +%s) - start )) s, exit code $(docker inspect --format '{{.State.ExitCode}}' node-api-broken)"
```

```text
stopped after 2 s, exit code 137
```

Exit code **137** (128 + 9): the container was killed with SIGKILL instead of ending by itself. Process 1 is now
`sh`, and a shell that runs as process 1 does not forward SIGTERM to its child: Node.js never heard it, so it could
not close its connections. Docker waits for the stop timeout (10 seconds unless the engine or `docker stop -t` sets
another), then kills everything, mid-request. Show it:

<!-- test: contains=sh -c; output -->
```bash
docker start node-api-broken > /dev/null
docker exec node-api-broken ps -o pid,args
docker rm -f node-api-broken > /dev/null
```

```text
PID   COMMAND
    1 sh -c node server.js || echo node-api crashed
    8 {MainThread} node server.js
   15 ps -o pid,args
```

The fix is the exec form, `CMD ["node", "server.js"]`, as in the solution (or `exec node server.js` at the end of a
start script). In Kubernetes the same bug turns every rolling update into dropped connections.

## Stretch goals

- Add a dependency (for example `npm install --save-exact express@5`), commit the lock file, and rebuild: only the
  `deps` stage is rebuilt when `package-lock.json` changes (lesson 039).
- Run with `--read-only --cap-drop ALL` and prove the API still works.
- Use `docker run --init` with `Dockerfile.broken` and measure `docker stop` again.

## Cleanup

<!-- test -->
```bash
docker rm -f node-api node-api-broken > /dev/null 2>&1 || true
docker image rm -f node-api:1.0 node-api:broken > /dev/null
cd ~ && rm -rf ~/docker-practice/project-02
```

Next: [Project 03 · Python API with Redis](../03-python-api/README.md)
