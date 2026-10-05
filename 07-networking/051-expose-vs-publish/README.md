# Lesson 051 · EXPOSE vs publishing ports

> Level 8 · Networking · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`EXPOSE 80` in a Dockerfile is **documentation**: it records which port the application listens on. It opens
nothing. **Publishing** (`-p HOST:CONTAINER` on `docker run`) is what makes a container port reachable from outside
Docker: the engine forwards a port of the host to the port of the container. Containers on a shared network reach each
other's ports directly, exposed or not.

## Visual

```text
  Dockerfile:  EXPOSE 80         → metadata only: "this image listens on 80/tcp"

  docker run nginx               → reachable from other containers on its network on :80
                                   NOT reachable from the host
  docker run -p 8080:80 nginx    → host 0.0.0.0:8080 ──▶ container :80     (every interface of the host)
  docker run -p 127.0.0.1:8080:80 → host 127.0.0.1:8080 ──▶ container :80  (only this computer)
  docker run -P nginx            → host <random>  ──▶ every EXPOSEd port

            ┌──────────── host ────────────────────────────────┐
  browser ──┼─▶ :8080 ── forward ─▶ ┌─ container ─┐            │
            │                       │ nginx  :80  │◀── other containers (no -p needed)
            │                       └─────────────┘            │
            └──────────────────────────────────────────────────┘
```

## Lab setup

No files are needed: `nginx:1.30-alpine` exposes port 80.

## Demonstration

The image documents its port:

<!-- test: contains=80/tcp; output -->
```bash
docker image inspect nginx:1.30-alpine --format '{{json .Config.ExposedPorts}}'
```

```text
{"80/tcp":{}}
```

Start it **without** publishing. Another container reaches it; the host does not:

<!-- test: contains=from a container: ok; output; retry=5 -->
```bash
docker network create port-net > /dev/null
docker run -d --name hidden --network port-net nginx:1.30-alpine > /dev/null
docker run --rm --network port-net busybox:1.37 wget -qO /dev/null http://hidden && echo "from a container: ok"
docker port hidden || true
```

```text
from a container: ok
```

`docker port` prints nothing: no host port is mapped. Publish the port on a second container:

<!-- test: contains=8080; output -->
```bash
docker run -d --name shown --network port-net -p 8080:80 nginx:1.30-alpine > /dev/null
docker port shown
```

```text
80/tcp -> 0.0.0.0:8080
80/tcp -> [::]:8080
```

<!-- test: contains=Welcome to nginx; output; retry=5 -->
```bash
curl -s http://localhost:8080 | grep -o '<title>.*</title>'
```

```text
<title>Welcome to nginx!</title>
```

## Command breakdown

| Form | Meaning |
|---|---|
| `EXPOSE 80` (Dockerfile) | metadata: the application listens on 80/tcp; publishes nothing |
| `-p 8080:80` | host port 8080 on all interfaces → container port 80 |
| `-p 127.0.0.1:8080:80` | the same, but only reachable from this computer |
| `-p 8080:80/udp` | a UDP port (the default is TCP) |
| `-P` | publish every exposed port on a random free host port |
| `docker port C` | the published ports of a container |

## Hands-on lab

**Instructions.** Start nginx with `-P` (capital P), find out which host port Docker chose, and fetch the page through
it.

**Expected result.** `docker port` shows `80/tcp -> 0.0.0.0:NNNNN`; the page answers on that port.

**Verification.**

<!-- test: contains=Welcome to nginx; retry=5 -->
```bash
docker run -d --name random-port -P nginx:1.30-alpine > /dev/null
port=$(docker port random-port 80/tcp | head -1 | sed 's/.*://')
echo "nginx is on host port $port"
curl -s "http://localhost:$port" | grep -o '<title>.*</title>'
```

## Break it

A developer adds `EXPOSE 80` to a Dockerfile and expects the site to be reachable on the host:

<!-- test: fail; contains=curl exit code 7; output -->
```bash
printf 'FROM nginx:1.30-alpine\nEXPOSE 80\n' | docker build -q -t my-site:1.0 - > /dev/null
docker run -d --name my-site my-site:1.0 > /dev/null
code=0; curl -s -m 5 http://localhost:80 > /dev/null || code=$?
echo "curl exit code $code"
[ "$code" -eq 0 ]
```

```text
curl exit code 7
```

## Troubleshoot it

curl exit code 7 means "failed to connect": nothing listens on the host's port 80. Check what is published, and what
the image only exposes:

<!-- test: contains=exposed; output -->
```bash
echo "published: $(docker port my-site)"
echo "exposed:   $(docker inspect my-site --format '{{json .Config.ExposedPorts}}')"
docker ps --filter name=my-site --format 'PORTS column: {{.Ports}}'
```

```text
published: 
exposed:   {"80/tcp":{}}
PORTS column: 80/tcp
```

`published` is empty: `EXPOSE` documented the port, and nobody published it. In `docker ps`, `80/tcp` without an
arrow means "exposed, not published"; a published port looks like `0.0.0.0:8080->80/tcp`.

## Fix it

Publish the port when the container is started. Ports cannot be added to a running container: recreate it.

<!-- test: contains=Welcome to nginx; output; retry=5 -->
```bash
docker rm -f my-site > /dev/null
docker run -d --name my-site -p 127.0.0.1:8081:80 my-site:1.0 > /dev/null
docker port my-site
curl -s http://127.0.0.1:8081 | grep -o '<title>.*</title>'
```

```text
80/tcp -> 127.0.0.1:8081
<title>Welcome to nginx!</title>
```

Publishing on `127.0.0.1` keeps a development server private to your computer. On a server, Docker's published ports
bypass many host firewall rules, so publish only what must be public.

## Practice challenge

Publish one container on **two** host ports: 8082 for everyone and 8083 for this computer only, both to port 80.

<details>
<summary>Solution</summary>

<!-- test: contains=0.0.0.0:8082; contains=127.0.0.1:8083; output -->
```bash
docker run -d --name two-ports -p 8082:80 -p 127.0.0.1:8083:80 nginx:1.30-alpine > /dev/null
docker port two-ports
```

```text
80/tcp -> 0.0.0.0:8082
80/tcp -> 127.0.0.1:8083
80/tcp -> [::]:8082
```

`-p` can be repeated; each one is a separate forwarding rule.

</details>

## Real-world example

A team's Postgres container was started with `-p 5432:5432` "for debugging" on a cloud VM. Published ports listen on
every interface, and Docker inserts its own firewall rules, so the database was reachable from the internet. The fix:
no `-p` at all for the database (the API reaches it over the Docker network), and `-p 127.0.0.1:5432:5432` when a
developer needs to connect from the VM itself.

## Recap

- `EXPOSE` is documentation of the listening port; it never makes anything reachable from the host.
- `-p HOST:CONTAINER` publishes a port; add `127.0.0.1:` to keep it local; `-P` publishes exposed ports randomly.
- Containers on the same network reach each other's ports without `-p`.
- `docker port` and the `PORTS` column of `docker ps` show what is really published.

## Cleanup

<!-- test -->
```bash
docker rm -f hidden shown random-port my-site two-ports > /dev/null
docker network rm port-net > /dev/null
docker image rm -f my-site:1.0 > /dev/null
```

Next: [Lesson 052 · Network troubleshooting](../052-network-troubleshooting/README.md)
