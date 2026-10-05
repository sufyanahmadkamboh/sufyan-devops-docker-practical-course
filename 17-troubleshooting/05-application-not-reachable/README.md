# Troubleshooting problem 05 · Application not reachable

> ⏱ 10 minutes · run every command from the course folder · related lessons: 012, 032, 051

## Problem

The container is `Up`, the logs show the server started, but the browser and `curl` cannot connect to
`http://localhost:8080`.

## Symptoms

<!-- test -->
```bash
docker run -d --name shop nginx:1.30-alpine > /dev/null
```

<!-- test: fail; contains=curl: (7); output -->
```bash
sleep 1
curl -sS http://localhost:8080 2>&1
```

```text
curl: (7) Failed to connect to localhost port 8080 after 2235 ms: Could not connect to server
```

## Investigation

Work from the inside out: is the application running, does it answer inside the container, is a port published?

**1. Is it running?**

<!-- test: contains=Up; output -->
```bash
docker ps --filter name=shop --format '{{.Names}}: {{.Status}}  ports: [{{.Ports}}]'
```

```text
shop: Up 3 seconds  ports: [80/tcp]
```

`Up`, but the port list shows only `80/tcp`: the port the image *declares*, with no host side.

**2. Does it answer inside the container?** `docker exec` runs a command next to the server (lesson 015):

<!-- test: contains=Welcome to nginx; output -->
```bash
docker exec shop wget -qO- http://localhost:80 | grep -o '<title>.*</title>'
```

```text
<title>Welcome to nginx!</title>
```

The application works. The problem is between your computer and the container.

**3. Is any port published to the host?**

<!-- test: absent=0.0.0.0; output -->
```bash
docker port shop
echo "port mappings: $(docker port shop | wc -l)"
```

```text
port mappings: 0
```

## Commands

| Command | What it tells you |
|---|---|
| `docker ps --format '{{.Ports}}'` | `80/tcp` = declared only; `0.0.0.0:8080->80/tcp` = published |
| `docker exec NAME wget -qO- http://localhost:PORT` | whether the app answers inside its container |
| `docker port NAME` | the host ↔ container port mappings (empty: none) |

## Output interpretation

`curl: (7) Failed to connect … Could not connect to server` means nothing listens on host port 8080 at all: the
connection is refused before any application is involved. `EXPOSE 80` in the image only documents the port; it does
not publish it (lesson 051). Without `-p`, the container is reachable only from other containers on its network.

Compare with the other "not reachable" problems:

| Symptom | Likely cause |
|---|---|
| `curl: (7)` connection refused / could not connect | no port published, or wrong host port: this problem |
| `curl: (52) Empty reply` or `(56) Connection reset` | port published, but nothing listens behind it: [problem 06](../06-listening-on-localhost/README.md), [problem 07](../07-wrong-container-port/README.md) |
| the container is not `Up` | [problem 01](../01-container-exits-immediately/README.md) |

## Root cause

The container was started without `-p`: no host port forwards to container port 80.

## Fix

Port mappings are set when a container is created; they cannot be added later. Recreate it with `-p`:

<!-- test -->
```bash
docker rm -f shop > /dev/null
docker run -d --name shop -p 8080:80 nginx:1.30-alpine > /dev/null
```

## Verification

<!-- test: retry=10; contains=Welcome to nginx; output -->
```bash
docker port shop
curl -s http://localhost:8080 | grep -o '<title>.*</title>'
```

```text
80/tcp -> 0.0.0.0:8080
80/tcp -> [::]:8080
<title>Welcome to nginx!</title>
```

## Prevention

- Define published ports in a Compose file instead of remembering `-p` flags (lesson 064).
- After starting a service, check `docker ps` for the `0.0.0.0:…->…` mapping, not only for `Up`.
- On a server, also check the firewall and the cloud security group: they block published ports the same way.

## Cleanup

<!-- test -->
```bash
docker rm -f shop > /dev/null
```

Next: [Problem 06 · Listening on localhost](../06-listening-on-localhost/README.md)
