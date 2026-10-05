# Lesson 130 · Production Dockerfile

> Level 19 · Production · ⏱ 35 minutes · run every command from the course folder

## What are we learning?

A Dockerfile that builds and runs is a starting point. A **production** Dockerfile also makes the image small, safe,
fast to rebuild, easy to operate and predictable: a pinned base image, dependencies installed from the lock file in
their own layer, only the files the application needs, a non-root user, a healthcheck, metadata labels, and an
exec-form command so the application receives the stop signal. This lesson puts the principles of modules 04–14
together in one file and shows what each one changes.

## Visual

```text
 before/Dockerfile                    final/Dockerfile                          principle
 ────────────────────────────         ──────────────────────────────────────    ───────────────────────────
 FROM node:24-alpine                  FROM node:24-alpine                       pinned, official, minimal base
                                      ENV NODE_ENV=production                   fixed runtime settings
                                      WORKDIR /app                              a home for the app, not /
 COPY . .                             COPY package.json package-lock.json ./    dependencies first: cached layer
 RUN npm install                      RUN npm ci --omit=dev && npm cache …      reproducible, no dev deps
                                      COPY server.js ./                         only the files needed (+ .dockerignore)
                                      USER node                                 never root
                                      EXPOSE 3000                               documented port
                                      HEALTHCHECK … /health                     "running" means "working"
                                      LABEL org.opencontainers.image.…          who, what, where from
 CMD sh start.sh                      CMD ["node", "server.js"]                 exec form: PID 1 gets SIGTERM
   (start.sh: echo …; node server.js)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-130 examples/node-api
cp 18-production/130-production-dockerfile/examples/before/Dockerfile ~/docker-practice/lesson-130/Dockerfile.before
cp 18-production/130-production-dockerfile/examples/before/start.sh ~/docker-practice/lesson-130/
cp 18-production/130-production-dockerfile/examples/final/Dockerfile 18-production/130-production-dockerfile/examples/final/.dockerignore ~/docker-practice/lesson-130/
cd ~/docker-practice/lesson-130
ls -A
```

The Node.js API of `examples/node-api`, with two Dockerfiles: `Dockerfile.before` (it works, and starts the API with the
script `start.sh`) and `Dockerfile` (production).

## Demonstration

Build both:

<!-- test: contains=api:final; output -->
```bash
docker build -q -f Dockerfile.before -t api:before . > /dev/null
docker build -q -t api:final . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' api
```

```text
api:final  245MB
api:before  245MB
```

Same base, same size: this application has no dependencies, so the differences are not in the size. They are in how
the image behaves. Compare the user, the working directory and the command:

<!-- test: contains=user=node; output -->
```bash
for image in api:before api:final; do
  docker image inspect "$image" --format "$image: user={{.Config.User}} workdir={{.Config.WorkingDir}} cmd={{json .Config.Cmd}}"
done
```

```text
api:before: user= workdir=/ cmd=["/bin/sh","-c","sh start.sh"]
api:final: user=node workdir=/app cmd=["node","server.js"]
```

`api:before` runs as root (an empty user), from `/`, and its command is `/bin/sh -c "sh start.sh"`: a shell, which runs
a script, which runs Node.js. `api:final` runs Node.js directly, as the user `node`, from `/app`. The healthcheck and the
labels are there too:

<!-- test: contains=org.opencontainers.image.title; output -->
```bash
docker image inspect api:final --format '{{json .Config.Labels}}'
docker run -d --name api-final api:final > /dev/null
```

```text
{"org.opencontainers.image.description":"Small HTTP API of the Docker Practical Course","org.opencontainers.image.licenses":"MIT","org.opencontainers.image.title":"node-api"}
```

<!-- test: retry=15; contains=healthy; output -->
```bash
docker inspect api-final --format '{{.State.Health.Status}}'
```

```text
healthy
```

## Command breakdown

| Instruction | Production rule |
|---|---|
| `FROM node:24-alpine` | official image, pinned major version, small variant (lesson 023); digest pin: lesson 134 |
| `COPY package.json package-lock.json ./` then `RUN npm ci` | dependencies in their own cached layer, exactly as locked (lesson 039) |
| `--omit=dev`, `npm cache clean --force` | no development tools or caches in the image |
| `.dockerignore` | `node_modules`, `.git`, `.env` and build files never enter the build context (lesson 037) |
| `USER node` | the application cannot modify its own code or the system (lesson 081) |
| `HEALTHCHECK` | Docker knows whether the application answers (lesson 092) |
| `LABEL org.opencontainers.image.*` | standard metadata that registries and scanners show (lesson 101) |
| `CMD ["node", "server.js"]` | exec form: Node.js is PID 1 and receives `SIGTERM` (lesson 029) |

## Hands-on lab

**Instructions.** Prove that the production container cannot change its own application code, and that the
"before" container can.

**Expected result.** `Permission denied` for `api:final` (user `node`, files owned by root); no error for
`api:before` (root).

**Verification.**

<!-- test: contains=Permission denied; contains=before: changed -->
```bash
docker run --rm api:final sh -c 'echo hacked >> /app/server.js' 2>&1 || true
docker run --rm api:before sh -c 'echo hacked >> /server.js && echo "before: changed"'
```

## Break it

Production platforms stop containers all the time: every deployment, scale-down and node maintenance sends `SIGTERM`
to the container, waits for it to stop (Docker: up to 10 seconds by default), then kills it with `SIGKILL`. Stop a
container of each image and look at how it ended:

<!-- test: contains=api-before: exit code 137; output -->
```bash
docker run -d --name api-before api:before > /dev/null
sleep 2
docker stop api-before api-final > /dev/null
docker inspect api-before api-final --format '{{.Name}}: exit code {{.State.ExitCode}}' | tr -d /
```

```text
api-before: exit code 137
api-final: exit code 0
```

`api-final` stopped cleanly (`0`). `api-before` was killed: 137 = 128 + 9, the number of `SIGKILL`.

## Troubleshoot it

Look at process 1 in each container (start them again first):

<!-- test: contains=sh start.sh; output -->
```bash
docker start api-before api-final > /dev/null
sleep 2
docker top api-before -o pid,args
docker top api-final -o pid,args
```

```text
PID                 COMMAND
2569042             sh start.sh
2569057             node server.js
PID                 COMMAND
2569096             node server.js
```

`SIGTERM` goes to process 1 only. In `api-final` that is Node.js, whose `SIGTERM` handler closes the server and exits
with code 0. In `api-before` process 1 is the shell running `start.sh`, and Node.js is its child. The shell does not
pass the signal on, so Node.js never runs its handler: it is killed in the middle of whatever it was doing, and open
requests are cut off, on every deployment.

## Fix it

Use the exec form for `CMD` (and `ENTRYPOINT`) so that the application is process 1, as in `Dockerfile`:

<!-- test: contains=CMD ["node", "server.js"] -->
```bash
cd ~/docker-practice/lesson-130
grep '^CMD' Dockerfile
grep SIGTERM server.js
```

When a start script is really needed, end it with `exec`: the shell then **replaces** itself with Node.js, which
becomes process 1. Fix `start.sh`, rebuild, and stop it again:

<!-- test: contains=api-before: exit code 0; output -->
```bash
cd ~/docker-practice/lesson-130
sed 's|^node server.js|exec node server.js|' start.sh > start.new && mv start.new start.sh
docker rm -f api-before > /dev/null
docker build -q -f Dockerfile.before -t api:before . > /dev/null
docker run -d --name api-before api:before > /dev/null
sleep 2
docker top api-before -o pid,args
docker stop api-before > /dev/null
docker inspect api-before --format '{{.Name}}: exit code {{.State.ExitCode}}' | tr -d /
```

```text
PID                 COMMAND
2569297             node server.js
api-before: exit code 0
```

For programs that do not handle `SIGTERM` at all, `docker run --init` adds a tiny init process as PID 1 that forwards
signals.

## Practice challenge

Add the version of the image as a label `org.opencontainers.image.version`, set at build time with
`--build-arg VERSION=1.2.0`, without editing the Dockerfile permanently for every release.

<details>
<summary>Solution</summary>

Declare an `ARG` and use it in a label: build arguments are fine for non-secret values like a version.

<!-- test: contains=1.2.0; output -->
```bash
cd ~/docker-practice/lesson-130
printf 'ARG VERSION=dev\nLABEL org.opencontainers.image.version=$VERSION\n' >> Dockerfile
docker build -q --build-arg VERSION=1.2.0 -t api:1.2.0 . > /dev/null
docker image inspect api:1.2.0 --format '{{index .Config.Labels "org.opencontainers.image.version"}}'
```

```text
1.2.0
```

The two lines are appended after `CMD`, which is fine: `LABEL` and `ARG` can appear anywhere, and only the last `CMD`
counts. In CI, the version comes from the Git tag (lesson 136).

</details>

## Real-world example

A team's deployments always cause a burst of HTTP 502 errors. The investigation finds containers stopped with exit
code 137 after the 10-second timeout: their images start the application from a shell script that does not forward
`SIGTERM`. Switching to `CMD ["node", "server.js"]` with a `SIGTERM` handler that stops accepting connections and finishes the open ones
makes the containers stop in under a second with exit code 0, and the 502s disappear.

## Recap

- Pinned minimal base, dependencies from the lock file in their own layer, only the needed files.
- Non-root `USER`, `HEALTHCHECK`, OCI labels, no secrets.
- Exec-form `CMD`: the application is process 1 and receives `SIGTERM`; handle it and exit cleanly.
- Measure: user, command, health and stop time are all visible with `docker inspect`, `docker top` and `docker stop`.

## Cleanup

<!-- test -->
```bash
docker rm -f api-before api-final > /dev/null
docker image rm -f api:before api:final api:1.2.0 > /dev/null
rm -rf ~/docker-practice/lesson-130
```

Next: [Lesson 131 · Container design](../131-container-design/README.md)
