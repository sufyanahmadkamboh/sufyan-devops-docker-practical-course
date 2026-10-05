# Troubleshooting problem 07 · Wrong container port

> ⏱ 10 minutes · run every command from the course folder · related lessons: 012, 032, 051

## Problem

The team's services listen on port 8080, so a developer starts Nginx the same way: `-p 8080:8080`. The container is
`Up`, the port is published, and every request gets an empty reply.

## Symptoms

<!-- test -->
```bash
docker run -d --name proxy -p 8080:8080 nginx:1.30-alpine > /dev/null
```

<!-- test: fail; anyof=curl: (52)||curl: (56); output -->
```bash
sleep 1
curl -sS http://localhost:8080 2>&1
```

```text
curl: (52) Empty reply from server
```

## Investigation

**1. Which port does the image say it uses?** The `EXPOSE` instruction is the image's documentation (lesson 032):

<!-- test: contains=80/tcp; output -->
```bash
docker image inspect --format '{{json .Config.ExposedPorts}}' nginx:1.30-alpine
```

```text
{"80/tcp":{}}
```

**2. What is mapped?**

<!-- test: contains=8080/tcp; output -->
```bash
docker port proxy
```

```text
8080/tcp -> 0.0.0.0:8080
8080/tcp -> [::]:8080
```

**3. Which port does the process really listen on?**

<!-- test: contains=:80; output -->
```bash
docker run --rm --network container:proxy busybox:1.37 netstat -tln
```

```text
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      
tcp        0      0 :::80                   :::*                    LISTEN      
```

## Commands

| Command | What it tells you |
|---|---|
| `docker image inspect --format '{{json .Config.ExposedPorts}}' IMAGE` | the port(s) the image declares |
| `docker port NAME` | `CONTAINER_PORT/tcp -> HOST:PORT` for every mapping |
| `docker run --rm --network container:NAME busybox:1.37 netstat -tln` | the ports the process really listens on |

## Output interpretation

`8080/tcp -> 0.0.0.0:8080` reads "container port 8080 is published on host port 8080". But Nginx listens on port 80
(`:::80` and `0.0.0.0:80`); nothing listens on 8080 inside the container, so the forwarder's connection is closed:
`(52) Empty reply from server`. The order in `-p` is always **host:container**.

## Root cause

`-p 8080:8080` maps to container port 8080; the application listens on container port 80.

## Fix

<!-- test -->
```bash
docker rm -f proxy > /dev/null
docker run -d --name proxy -p 8080:80 nginx:1.30-alpine > /dev/null
```

## Verification

<!-- test: retry=10; contains=Welcome to nginx; output -->
```bash
docker port proxy
curl -s http://localhost:8080 | grep -o '<title>.*</title>'
```

```text
80/tcp -> 0.0.0.0:8080
80/tcp -> [::]:8080
<title>Welcome to nginx!</title>
```

## Prevention

- Read `EXPOSE` (or the image's documentation) before choosing the container side of `-p`.
- Remember the order: `-p HOST:CONTAINER`, as in `-p 8080:80` = "my 8080 → its 80".
- If the application's port is configurable, set it explicitly (`PORT=8080`) and keep `EXPOSE` in sync with it.

## Cleanup

<!-- test -->
```bash
docker rm -f proxy > /dev/null
```

Next: [Problem 08 · Wrong network](../08-wrong-network/README.md)
