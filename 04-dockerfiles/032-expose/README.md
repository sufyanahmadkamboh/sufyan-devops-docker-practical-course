# Lesson 032 · EXPOSE

> Level 5 · Dockerfiles · ⏱ 15 minutes · run every command from the course folder

## What are we learning?

`EXPOSE 3000` **documents** the port the application in the image listens on. It does not open, publish or forward
anything: a container is reachable from your computer only through `-p HOST:CONTAINER` (lesson 012). `EXPOSE` is used by
people reading the image, by tools, and by `docker run -P`, which publishes every exposed port to a random free port.
It must match the port the application really listens on.

## Visual

```text
  Dockerfile: EXPOSE 3000                image config: ExposedPorts {"3000/tcp"}   (metadata only)

  docker run IMAGE               ──▶ app listens on 3000 inside; nothing reachable from your computer
  docker run -p 8080:3000 IMAGE  ──▶ localhost:8080 → container:3000      (EXPOSE not needed for this)
  docker run -P IMAGE            ──▶ localhost:<random> → container:3000  (uses the EXPOSE list)

  EXPOSE 80, app listens on 3000 ──▶ -P publishes port 80, where nothing listens → no response
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-032 examples/node-api
cd ~/docker-practice/lesson-032
grep -n "listen" server.js
```

The Node.js API listens on `PORT`, 3000 by default.

## Demonstration

<!-- test: contains={"3000/tcp":{}}; output -->
```bash
cat > Dockerfile <<'EOF'
FROM node:24-alpine
WORKDIR /app
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
EOF
docker build -q -t cafe-api:expose . > /dev/null
docker image inspect --format '{{json .Config.ExposedPorts}}' cafe-api:expose
```

```text
{"3000/tcp":{}}
```

Run it with `-P` (capital P) and ask Docker which host port it chose:

<!-- test: contains=3000/tcp; output -->
```bash
docker run -d --name cafe-api -P cafe-api:expose > /dev/null
docker port cafe-api
```

```text
3000/tcp -> 0.0.0.0:32784
```

<!-- test: retry=10; contains=Hello from Node.js; output -->
```bash
port=$(docker port cafe-api 3000/tcp | head -1 | sed 's/.*://')
curl -s "http://localhost:$port"
```

```text
{"message":"Hello from Node.js","hostname":"35d3cf1311f8","version":"dev"}
```

## Command breakdown

| Instruction / option | Meaning |
|---|---|
| `EXPOSE 3000` | document a TCP port (`EXPOSE 3000/tcp`); `EXPOSE 5353/udp` for UDP |
| `docker run -P` | publish every exposed port to a random free host port |
| `docker run -p 8080:3000` | publish container port 3000 on host port 8080; works with or without `EXPOSE` |
| `docker port CONTAINER [PORT]` | show which host ports a container's ports are published on |

## Hands-on lab

**Instructions.** Start a second container of `cafe-api:expose` without any `-p` or `-P` option, and show with
`docker port` that nothing is published, although the image exposes 3000.

**Expected result.** `docker port` prints nothing for that container; `docker container ls` shows `3000/tcp` without
a host address.

**Verification.**

<!-- test: contains=unpublished: 3000/tcp -->
```bash
docker run -d --name cafe-api-internal cafe-api:expose > /dev/null
echo "published: [$(docker port cafe-api-internal)]"
docker container ls --filter name=cafe-api-internal --format 'unpublished: {{.Ports}}'
```

## Break it

The image is rebuilt from a copied Nginx Dockerfile, still saying `EXPOSE 80`:

<!-- test: anyof=no response||Empty reply; output -->
```bash
sed 's/^EXPOSE 3000$/EXPOSE 80/' Dockerfile > Dockerfile.wrong
docker build -q -f Dockerfile.wrong -t cafe-api:wrong-port . > /dev/null
docker run -d --name cafe-api-wrong -P cafe-api:wrong-port > /dev/null
sleep 2
port=$(docker port cafe-api-wrong 80/tcp | head -1 | sed 's/.*://')
curl -sS "http://localhost:$port" 2>&1 || echo "no response from the application"
```

```text
curl: (52) Empty reply from server
no response from the application
```

## Troubleshoot it

The container runs and Docker published a port, yet there is no answer. Compare three things: what is published,
where the application listens, and whether it answers *inside* the container:

<!-- test: contains=80/tcp; contains=port 3000; contains=Hello from Node.js; output -->
```bash
docker port cafe-api-wrong
docker logs cafe-api-wrong
docker exec cafe-api-wrong wget -qO- http://127.0.0.1:3000
```

```text
80/tcp -> 0.0.0.0:32785
node-api listening on port 3000
{"message":"Hello from Node.js","hostname":"8522faeb80e2","version":"dev"}
```

The application is healthy on port 3000, but `-P` published port 80, the one `EXPOSE` claimed, where nothing listens.
Docker trusts `EXPOSE`; it does not check what the application does.

## Fix it

Make `EXPOSE` match the application's port, rebuild and restart:

<!-- test: contains=3000/tcp -->
```bash
docker rm -f cafe-api-wrong > /dev/null
sed -i.bak 's/^EXPOSE 80$/EXPOSE 3000/' Dockerfile.wrong && rm Dockerfile.wrong.bak
docker build -q -f Dockerfile.wrong -t cafe-api:wrong-port . > /dev/null
docker run -d --name cafe-api-wrong -P cafe-api:wrong-port > /dev/null
docker port cafe-api-wrong
```

<!-- test: retry=10; contains=Hello from Node.js -->
```bash
curl -s "http://localhost:$(docker port cafe-api-wrong 3000/tcp | head -1 | sed 's/.*://')"
```

## Practice challenge

The application's port is configurable (`PORT`). Build an image where `ENV PORT=8000` and `EXPOSE` stay consistent by
using the same build argument for both, then check with `-P` that it answers.

<details>
<summary>Solution</summary>

<!-- test: contains=8000/tcp; output=head:1 -->
```bash
cd ~/docker-practice/lesson-032
cat > Dockerfile.port <<'EOF'
FROM node:24-alpine
ARG PORT=8000
WORKDIR /app
COPY . .
ENV PORT=$PORT
EXPOSE $PORT
CMD ["node", "server.js"]
EOF
docker build -q -f Dockerfile.port -t cafe-api:8000 . > /dev/null
docker run -d --name cafe-api-8000 -P cafe-api:8000 > /dev/null
docker port cafe-api-8000
```

```text
8000/tcp -> 0.0.0.0:32787
```

<!-- test: retry=10; contains=Hello from Node.js -->
```bash
curl -s "http://localhost:$(docker port cafe-api-8000 8000/tcp | head -1 | sed 's/.*://')"
```

One argument feeds both the application's configuration and the documentation, so they cannot drift apart.

</details>

## Real-world example

Platform tools read the exposed ports of an image: Docker Desktop shows them, some PaaS platforms route traffic to the
first exposed port, and a reviewer sees in `docker image inspect` which ports a third-party image will listen on. In
Compose and Kubernetes, the published ports are still declared separately (`ports:`, a Service), so `EXPOSE` remains
documentation: correct, but not a security control. Lesson 051 compares `EXPOSE` and `-p` in networking terms.

## Recap

- `EXPOSE` documents the application's port; it publishes nothing.
- `-p HOST:CONTAINER` publishes a port, with or without `EXPOSE`; `-P` publishes all exposed ports to random ports.
- `docker port` shows the mapping; a wrong `EXPOSE` makes `-P` publish the wrong port.
- Keep `EXPOSE` consistent with the application's configuration.

## Cleanup

<!-- test -->
```bash
docker rm -f cafe-api cafe-api-internal cafe-api-wrong cafe-api-8000 > /dev/null
docker image rm -f cafe-api:expose cafe-api:wrong-port cafe-api:8000 > /dev/null
rm -rf ~/docker-practice/lesson-032
```

Next: [Lesson 033 · USER](../033-user/README.md)
