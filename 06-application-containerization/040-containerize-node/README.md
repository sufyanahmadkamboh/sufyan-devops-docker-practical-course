# Lesson 040 · Containerizing a Node.js application

> Level 7 · Application containerization · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

How to write a proper Dockerfile for a Node.js service, step by step: an official, pinned base image, a reproducible
dependency install from the lockfile (`npm ci`), the cache-friendly order from lesson 039, an unprivileged user, and a
start command that lets Node.js receive the stop signal. The same pattern works for Express, Fastify or NestJS APIs.

## Visual

```text
  node-api/                          Dockerfile                                  image node-api:1.0
  ├── package.json       ─┐   FROM node:24-alpine        runtime + npm          ┌───────────────────────┐
  ├── package-lock.json  ─┴─▶ COPY package*.json ./      manifests first        │ /app/node_modules     │
  ├── server.js          ──┐  RUN npm ci --omit=dev      exact versions, no dev │ /app/server.js        │
  └── .dockerignore        └▶ COPY server.js ./          code last              │ user: node (uid 1000) │
       (node_modules, .env)   USER node                  not root               │ CMD node server.js    │
                              CMD ["node","server.js"]   PID 1 = node           └───────────────────────┘

  docker stop ──SIGTERM──▶ node (PID 1) ──▶ server.close() ──▶ exit 0   (in well under the 10 s grace period)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-040 examples/node-api
cp -r 06-application-containerization/040-containerize-node/examples/. ~/docker-practice/lesson-040/
cd ~/docker-practice/lesson-040
ls -a
cat Dockerfile
```

## Demonstration

Build and run the image:

<!-- test: contains=node-api; output -->
```bash
docker build -q -t node-api:1.0 . > /dev/null
docker image ls node-api
docker run -d --name node-api -p 8080:3000 -e APP_VERSION=1.0 node-api:1.0 > /dev/null
```

```text
IMAGE          ID             DISK USAGE   CONTENT SIZE   EXTRA
node-api:1.0   f78f9873e916        245MB         62.2MB        
```

<!-- test: retry=10; contains="version":"1.0"; output -->
```bash
curl -s http://localhost:8080/
```

```text
{"message":"Hello from Node.js","hostname":"4b73876786e5","version":"1.0"}
```

Check the two properties the Dockerfile promised: the process runs as `node`, not root, and it is PID 1:

<!-- test: contains=node; output -->
```bash
docker exec node-api id
docker exec node-api ps -o pid,user,args
```

```text
uid=1000(node) gid=1000(node) groups=1000(node)
PID   USER     COMMAND
    1 node     {MainThread} node server.js
   20 node     ps -o pid,user,args
```

## Command breakdown

| Instruction | Why |
|---|---|
| `FROM node:24-alpine` | the official image, pinned to a major version (lesson 021); Alpine keeps it small |
| `ENV NODE_ENV=production` | many libraries switch to production behaviour with it |
| `COPY package.json package-lock.json ./` then `RUN npm ci` | install exactly the locked versions; cached until they change |
| `--omit=dev` | skip development dependencies (test tools, linters) in the runtime image |
| `USER node` | the official image's unprivileged user |
| `CMD ["node", "server.js"]` | exec form, not `npm start`: node is PID 1 and gets `SIGTERM` |

## Hands-on lab

**Instructions.** Stop the container and check how long it took and how the process ended.

**Expected result.** `docker stop` returns in about a second (not the 10 s timeout), and the exit code is `0`: the
server handled `SIGTERM` (see the last line of `server.js`) and shut down cleanly.

**Verification.**

<!-- test: contains=exit code 0 -->
```bash
start=$(date +%s)
docker stop node-api > /dev/null
echo "stopped in $(( $(date +%s) - start )) s, exit code $(docker inspect --format '{{.State.ExitCode}}' node-api)"
docker rm node-api > /dev/null
```

## Break it

A teammate deletes `package-lock.json` ("it is generated anyway") and rebuilds:

<!-- test: fail; contains=npm ci; output -->
```bash
cd ~/docker-practice/lesson-040
rm package-lock.json
sed -i.bak 's/package.json package-lock.json/package*.json/' Dockerfile && rm Dockerfile.bak
docker build -t node-api:nolock . 2>&1 | grep -E 'npm (error|ERR)' | head -3
test "${PIPESTATUS[0]}" -eq 0
```

```text
#8 0.555 npm error code EUSAGE
#8 0.561 npm error
#8 0.561 npm error The `npm ci` command can only install with an existing package-lock.json or
```

(The `sed` changes the `COPY` to the wildcard `package*.json` so the build gets as far as `npm ci`; with the explicit
`COPY package-lock.json` it would already fail with `not found`.)

## Troubleshoot it

`npm ci` refuses to run without a lockfile, by design: it installs **exactly** what the lockfile records, so that every
build installs the same versions. `npm install` would silently resolve the newest versions allowed by `package.json`,
and two builds of the same commit could contain different code. The lockfile is part of the source code:

<!-- test: contains=no lockfile -->
```bash
ls package-lock.json 2> /dev/null || echo "no lockfile in the context"
```

## Fix it

Restore the lockfile (in a real project: `git checkout package-lock.json`). If a project really has none, generate it
**once** with Node.js in a container, without installing Node.js locally, and commit it:

<!-- test: contains=lockfileVersion -->
```bash
docker run --rm -v "$(pwd):/app" -w /app node:24-alpine npm install --package-lock-only --silent
grep lockfileVersion package-lock.json
```

<!-- test: contains=node-api:fixed -->
```bash
docker build -q -t node-api:fixed . > /dev/null
docker image ls node-api
```

## Practice challenge

The application reads `PORT` (default 3000) and `GREETING` from the environment. Start the image so that the server
listens on port **4000** inside the container with the greeting `Hallo aus dem Container`, published on port 8081 of
your computer.

<details>
<summary>Solution</summary>

<!-- test: contains=Hallo; output -->
```bash
docker run -d --name node-api-4000 -p 8081:4000 -e PORT=4000 -e GREETING="Hallo aus dem Container" node-api:fixed > /dev/null
sleep 1
curl -s http://localhost:8081/
```

```text
{"message":"Hallo aus dem Container","hostname":"185f5796615e","version":"dev"}
```

`-p HOST:CONTAINER` must use the port the application really listens on (`4000`), not the one in `EXPOSE`; `EXPOSE` is
documentation (lesson 051).

</details>

## Real-world example

A typical production Node.js Dockerfile adds two things to this one: a build stage for TypeScript or a frontend bundle
(multi-stage, lesson 088) and a `HEALTHCHECK` (lesson 092). Teams also run `npm ci` with `--ignore-scripts` when no
dependency needs install scripts, so that a compromised package cannot run code during the build.

## Recap

- Base image pinned, manifests copied first, `npm ci --omit=dev` from the lockfile, code last.
- Run as the image's `node` user, with an exec-form `CMD` so Node.js receives `SIGTERM`.
- Commit `package-lock.json`: without it `npm ci` fails and builds are not reproducible.
- Configure the application with environment variables (`PORT`, `GREETING`), not by rebuilding.

## Cleanup

<!-- test -->
```bash
docker rm -f node-api node-api-4000 > /dev/null 2>&1 || true
docker image rm -f node-api:1.0 node-api:nolock node-api:fixed > /dev/null 2>&1 || true
rm -rf ~/docker-practice/lesson-040
```

Next: [Lesson 041 · Containerizing a Python application](../041-containerize-python/README.md)
