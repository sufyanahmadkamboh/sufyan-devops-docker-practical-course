# Lesson 012 · Port mapping

> Level 3 · Working with containers · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`-p HOST_PORT:CONTAINER_PORT` publishes a container's port: Docker listens on `HOST_PORT` of your computer and forwards
every connection to `CONTAINER_PORT` inside the container. The two numbers are independent, so ten Nginx containers can
all listen on port 80 inside while each one gets a different port outside. A host port, however, can belong to only one
container at a time.

## Visual

```text
  Your computer                                            Containers
  ┌───────────────────────────────────┐
  │ 0.0.0.0:8080  ────────────────────┼───────────────▶  web-a   nginx :80
  │ 0.0.0.0:8081  ────────────────────┼───────────────▶  web-b   nginx :80
  │ 127.0.0.1:8082 ───────────────────┼───────────────▶  admin   nginx :80   (only from this computer)
  │ 0.0.0.0:NNNNN (random) ───────────┼───────────────▶  temp    nginx :80   (-p 80: Docker picks a port)
  └───────────────────────────────────┘
   -p 8080:80              host port 8080 → container port 80, on every network interface
   -p 127.0.0.1:8082:80    only on the loopback interface: not reachable from other machines
   -p 80                   a random free host port → container port 80
```

## Lab setup

No files are needed.

## Demonstration

Two containers, the same container port, different host ports:

<!-- test: contains=0.0.0.0:8081->80/tcp; output -->
```bash
docker run -d --name web-a -p 8080:80 nginx:1.30-alpine > /dev/null
docker run -d --name web-b -p 8081:80 nginx:1.29-alpine > /dev/null
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
```

```text
NAMES     IMAGE               PORTS
web-b     nginx:1.29-alpine   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp
web-a     nginx:1.30-alpine   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

Each host port reaches its own container (the `Server` header shows which Nginx version answered):

<!-- test: contains=nginx/1.30; contains=nginx/1.29; retry=10; output -->
```bash
curl -sI http://localhost:8080 | grep -i '^server'
curl -sI http://localhost:8081 | grep -i '^server'
```

```text
Server: nginx/1.30.5
Server: nginx/1.29.8
```

`docker port` lists a container's published ports:

<!-- test: contains=80/tcp -> 0.0.0.0:8080; output -->
```bash
docker port web-a
```

```text
80/tcp -> 0.0.0.0:8080
80/tcp -> [::]:8080
```

Publish on the loopback interface only, so that other machines on your network cannot connect:

<!-- test: contains=127.0.0.1:8082; output -->
```bash
docker run -d --name admin -p 127.0.0.1:8082:80 nginx:1.30-alpine > /dev/null
docker port admin
```

```text
80/tcp -> 127.0.0.1:8082
```

## Command breakdown

| Option | Meaning |
|---|---|
| `-p 8080:80` | host port 8080 (all interfaces) → container port 80 |
| `-p 127.0.0.1:8082:80` | only on 127.0.0.1 of the host |
| `-p 80` | a random free host port → container port 80 |
| `-p 5353:53/udp` | UDP instead of TCP |
| `-P` (capital) | publish every port the image declares (`EXPOSE`) on random host ports |
| `docker port NAME [PORT]` | show the published ports |

Ports are fixed when the container is created: to change them, create a new container.

## Hands-on lab

**Instructions.** Start `redis:8-alpine` named `cache` and publish its port 6379 on the host port 6380, on the loopback
interface only. Then check the mapping.

**Expected result.** `6379/tcp -> 127.0.0.1:6380`.

**Verification.**

<!-- test: contains=6379/tcp -> 127.0.0.1:6380 -->
```bash
docker run -d --name cache -p 127.0.0.1:6380:6379 redis:8-alpine > /dev/null
docker port cache
```

## Break it

A third website should also use port 8080:

<!-- test: fail; anyof=port is already allocated||address already in use||ports are not available; output -->
```bash
docker run -d --name web-c -p 8080:80 nginx:1.30-alpine 2>&1
```

```text
0cf65dc51777bdd456a73b98f7ba33bd57b3cb74e3c1c96dfa377239ab3316f9
docker: Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint web-c (f42c29704b02595cd49c52f5b25cb7fab4e474d7a349f92ec0001287c4201e70): Bind for 0.0.0.0:8080 failed: port is already allocated

Run 'docker run --help' for more information
```

## Troubleshoot it

`Bind for 0.0.0.0:8080 failed: port is already allocated`: one host port, one listener. Docker created the container
(it is in `docker ps -a` as `Created`) but could not start it. Find out who owns the port. If it is another container,
`docker ps` shows it:

<!-- test: contains=web-a; output -->
```bash
docker ps --filter publish=8080 --format '{{.Names}} owns {{.Ports}}'
```

```text
web-a owns 0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

If no container owns it, another program on your computer does: `ss -ltnp | grep 8080` on Linux, `lsof -i :8080` on
macOS, `netstat -ano | findstr 8080` on Windows. Then the error reads `address already in use` (troubleshooting
problem 04).

## Fix it

Remove the half-created container and use a free host port:

<!-- test: contains=80/tcp -> 0.0.0.0:8083 -->
```bash
docker rm web-c > /dev/null
docker run -d --name web-c -p 8083:80 nginx:1.30-alpine > /dev/null
docker port web-c
```

## Practice challenge

Start an Nginx container with `-p 80` (no host port), find out which host port Docker chose, and fetch the page through
it.

<details>
<summary>Solution</summary>

<!-- test -->
```bash
docker run -d --name temp -p 80 nginx:1.30-alpine
```

<!-- test: contains=Welcome to nginx!; retry=10; output -->
```bash
port=$(docker port temp 80/tcp | head -1 | sed 's/.*://')
echo "Docker chose host port $port"
curl -s "http://localhost:$port" | grep '<title>'
```

```text
Docker chose host port 63718
<title>Welcome to nginx!</title>
```

`docker port temp 80/tcp` prints `0.0.0.0:PORT` (and an IPv6 line): everything after the last `:` is the port. Random
ports avoid conflicts in tests and CI, where many copies of the same service run side by side.

</details>

## Real-world example

On a server, the reverse proxy is often the only container with published ports (`-p 80:80 -p 443:443`); the
application and database containers publish nothing and are reached only over a Docker network (lesson 048). Ports for
admin tools are published on `127.0.0.1` and reached through an SSH tunnel. Publishing a database on `0.0.0.0` is a
classic security mistake: it opens it to the whole network, and Docker's port rules can bypass a host firewall.

## Recap

- `-p HOST:CONTAINER` forwards a host port to a container port; the numbers are independent.
- One host port belongs to one container (or program) at a time: `port is already allocated`.
- `-p 127.0.0.1:…` restricts access to the local machine; `-p PORT` picks a random host port.
- Ports are fixed at creation; `docker port` shows them.

## Cleanup

<!-- test -->
```bash
docker rm -f web-a web-b web-c admin cache temp > /dev/null
```

Next: [Lesson 013 · Running multiple containers](../013-multiple-containers/README.md)
