# Lesson 030 · ENV

> Level 5 · Dockerfiles · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`ENV NAME=value` sets an environment variable in the image: it is available to the following build steps **and** to
every container of the image, as a default that `docker run -e NAME=other` can override. Applications read their
configuration from environment variables (ports, URLs, feature flags), so `ENV` is how an image ships sensible
defaults. Everything set with `ENV` is visible in the image: never put secrets there.

## Visual

```text
  Dockerfile                          image config                     container
  ENV PORT=3000          ──────────▶  Env: PORT=3000          ──────▶  PORT=3000          (default)
  ENV GREETING="Hello"                    GREETING=Hello                GREETING=Hi       ← docker run -e GREETING=Hi
  RUN echo "$PORT"       uses it at build time too

  RUN export APP_VERSION=1.4.0   ✗  lives only in that step's shell: not in the image, not in containers
  ENV API_KEY=…                  ✗  stored in the image: anyone with the image can read it (lesson 083)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-030 examples/node-api
cd ~/docker-practice/lesson-030
ls
grep -n "process.env" server.js
```

The Node.js API reads three environment variables: `PORT`, `GREETING` and `APP_VERSION`.

## Demonstration

Set defaults in the image:

<!-- test: contains=building version 1.0.0 -->
```bash
cat > Dockerfile <<'EOF'
FROM node:24-alpine
WORKDIR /app
COPY . .
ENV PORT=3000 \
    GREETING="Hello from the cafe" \
    APP_VERSION=1.0.0
RUN echo "building version $APP_VERSION for port $PORT"
CMD ["node", "server.js"]
EOF
docker build --progress=plain -t cafe-api:env . 2>&1 | grep "building version"
docker run -d --name cafe-api -p 8080:3000 cafe-api:env > /dev/null
```

<!-- test: retry=10; contains=Hello from the cafe; output -->
```bash
docker logs cafe-api
curl -s http://localhost:8080
```

```text
node-api listening on port 3000
{"message":"Hello from the cafe","hostname":"24b07bfda817","version":"1.0.0"}
```

The `RUN` step saw the variables during the build, and the application reads them at run time. Override one for a
single container, without rebuilding:

<!-- test: contains=lab ready -->
```bash
docker run -d --name cafe-api-de -p 8081:3000 -e GREETING="Hallo aus dem Café" cafe-api:env > /dev/null && echo "lab ready"
```

<!-- test: retry=10; contains=Hallo aus dem; output -->
```bash
curl -s http://localhost:8081
```

```text
{"message":"Hallo aus dem Café","hostname":"c80a39b66057","version":"1.0.0"}
```

## Command breakdown

| Instruction / option | Meaning |
|---|---|
| `ENV NAME=value` | set a variable in the image; several in one instruction with `\` continuation |
| `ENV NAME="two words"` | quote values with spaces |
| `docker run -e NAME=value` | override (or add) a variable for one container |
| `docker image inspect --format '{{json .Config.Env}}'` | the variables an image sets |
| `docker exec CONTAINER env` | the variables a running container really has |

## Hands-on lab

**Instructions.** Show the environment variables stored in `cafe-api:env`, and the ones the container `cafe-api-de`
really has.

**Expected result.** The image has `GREETING=Hello from the cafe`; the container has the German greeting.

**Verification.**

<!-- test: contains=GREETING=Hello from the cafe; contains=GREETING=Hallo aus dem -->
```bash
docker image inspect --format '{{json .Config.Env}}' cafe-api:env
docker exec cafe-api-de env | grep -e GREETING -e PORT -e APP_VERSION
```

## Break it

Version 1.1 should report its version. A colleague sets it in a `RUN` step:

<!-- test: contains=cafe-api:1.1 -->
```bash
cat > Dockerfile.v11 <<'EOF'
FROM node:24-alpine
WORKDIR /app
COPY . .
ENV PORT=3000
RUN export APP_VERSION=1.1.0
CMD ["node", "server.js"]
EOF
docker build -q -f Dockerfile.v11 -t cafe-api:1.1 . > /dev/null
docker run -d --name cafe-api-v11 -p 8082:3000 cafe-api:1.1 > /dev/null
docker container ls --format '{{.Names}} {{.Image}}' --filter name=cafe-api-v11
```

<!-- test: retry=10; contains="version":"dev"; output -->
```bash
curl -s http://localhost:8082
```

```text
{"message":"Hello from Node.js","hostname":"211012de846a","version":"dev"}
```

The API reports `dev`, its fallback when `APP_VERSION` is not set.

## Troubleshoot it

Ask the container for the variable, then the image:

<!-- test: contains=APP_VERSION is not set; absent=APP_VERSION=1.1.0; output -->
```bash
docker exec cafe-api-v11 sh -c 'echo "APP_VERSION=${APP_VERSION:-(not set)}"' | sed 's/=(not set)/ is not set/'
docker image inspect --format '{{json .Config.Env}}' cafe-api:1.1
```

```text
APP_VERSION is not set
["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","NODE_VERSION=24.21.0","YARN_VERSION=1.22.22","PORT=3000"]
```

`RUN export …` set the variable in the shell of that one build step. The shell ended with the step, and only files are
saved in a layer, not a shell's variables. The image's environment comes from `ENV` instructions only (yours and the
base image's: `NODE_VERSION` comes from `node:24-alpine`).

## Fix it

<!-- test: contains=cafe-api-v11 -->
```bash
sed -i.bak 's/^RUN export APP_VERSION=1.1.0$/ENV APP_VERSION=1.1.0/' Dockerfile.v11 && rm Dockerfile.v11.bak
docker build -q -f Dockerfile.v11 -t cafe-api:1.1 . > /dev/null
docker rm -f cafe-api-v11 > /dev/null
docker run -d --name cafe-api-v11 -p 8082:3000 cafe-api:1.1 > /dev/null
docker container ls --format '{{.Names}} {{.Image}}' --filter name=cafe-api-v11
```

<!-- test: retry=10; contains="version":"1.1.0" -->
```bash
curl -s http://localhost:8082
```

## Practice challenge

Run `cafe-api:env` so that the application listens on port **4000** inside the container, reachable on port 8083 of
your computer, without rebuilding the image.

<details>
<summary>Solution</summary>

<!-- test: contains=started -->
```bash
docker run -d --name cafe-api-4000 -e PORT=4000 -p 8083:4000 cafe-api:env > /dev/null && echo "started"
```

<!-- test: retry=10; contains=port 4000; contains=Hello from the cafe; output -->
```bash
curl -s http://localhost:8083 && echo
docker logs cafe-api-4000
```

```text
{"message":"Hello from the cafe","hostname":"30e616f50ecc","version":"1.0.0"}
node-api listening on port 4000
```

`-e PORT=4000` changes where the application listens; `-p 8083:4000` must then publish that port. The image's `ENV`
was only the default.

</details>

## Real-world example

A team builds one image per release and runs it in development, staging and production with different variables
(`DATABASE_HOST`, `LOG_LEVEL`, `FEATURE_NEW_CHECKOUT=true`): the "twelve-factor app" rule of storing configuration in
the environment. The Dockerfile's `ENV` holds only safe defaults (`PORT=3000`, `NODE_ENV=production`); real values come
from `docker run -e`, an env file (lesson 060), Compose (lesson 067) or Kubernetes, and secrets from a secret store
(lesson 061).

## Recap

- `ENV` sets variables for later build steps and for every container, as defaults.
- `docker run -e` overrides them per container, without a rebuild.
- `RUN export` does not persist: use `ENV`.
- `ENV` values are stored in the image and visible to anyone: no secrets.

## Cleanup

<!-- test -->
```bash
docker rm -f cafe-api cafe-api-de cafe-api-v11 cafe-api-4000 > /dev/null
docker image rm -f cafe-api:env cafe-api:1.1 > /dev/null
rm -rf ~/docker-practice/lesson-030
```

Next: [Lesson 031 · ARG](../031-arg/README.md)
