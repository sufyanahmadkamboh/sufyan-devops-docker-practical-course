# Troubleshooting problem 04 · Port already in use

> ⏱ 10 minutes · run every command from the course folder · related lessons: 012, 013

## Problem

A developer starts the new version of the website next to the old one, and `docker run` refuses with
`port is already allocated`. The new container exists but is not running.

## Symptoms

Reproduce it: an older container already publishes host port 8080.

<!-- test: contains=web-old -->
```bash
docker run -d --name web-old -p 8080:80 nginx:1.29-alpine > /dev/null
docker ps --format '{{.Names}}'
```

<!-- test: fail; contains=port is already allocated; output -->
```bash
docker run -d --name web-new -p 8080:80 nginx:1.30-alpine 2>&1
```

```text
ea78f356ea99c21bad4712704aa0bba1f4d2b0010083e8cbf3d244223ab9775d
docker: Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint web-new (a5670b5b69f0998cc11e899958c5e946bb4c91116de8c821ae2bdb111f9d7e66): Bind for 0.0.0.0:8080 failed: port is already allocated

Run 'docker run --help' for more information
```

<!-- test: contains=Created; output -->
```bash
docker ps -a --filter name=web-new --format '{{.Names}}: {{.Status}}'
```

```text
web-new: Created
```

## Investigation

**1. Which container holds the port?** Filter running containers by published port:

<!-- test: contains=web-old; output -->
```bash
docker ps --filter publish=8080 --format '{{.Names}}  {{.Image}}  {{.Ports}}'
```

```text
web-old  nginx:1.29-alpine  0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

**2. What does that container publish exactly?**

<!-- test: contains=8080; output -->
```bash
docker port web-old
```

```text
80/tcp -> 0.0.0.0:8080
80/tcp -> [::]:8080
```

If **no** container shows up, another program on your computer uses the port (a local web server, another tool).
Find it with the operating system: `ss -ltnp | grep :8080` (Linux), `lsof -i :8080` (macOS) or
`netstat -ano | findstr :8080` (Windows). The error is then different: `bind: address already in use` or
`ports are not available`.

## Commands

| Command | What it tells you |
|---|---|
| `docker ps --filter publish=PORT` | the running container that publishes that host port |
| `docker port NAME` | all port mappings of a container |
| `ss -ltnp` / `lsof -i :PORT` / `netstat -ano` | a non-Docker process listening on the port |

## Output interpretation

`Bind for 0.0.0.0:8080 failed: port is already allocated`: Docker itself already gave host port 8080 (on every
address, `0.0.0.0`) to another container. Only one listener can own a host port; the **container** port (80) can be the
same in any number of containers, because each container has its own network namespace (lesson 013). The failed
container was created but never started (`Created`).

## Root cause

Two containers asked for the same **host** port 8080. The old one still runs and owns it.

## Fix

Pick one: stop the old container first, or give the new one another host port. Here both run side by side:

<!-- test -->
```bash
docker rm web-new > /dev/null
docker run -d --name web-new -p 8081:80 nginx:1.30-alpine > /dev/null
```

## Verification

<!-- test: retry=10; contains=nginx/1.30; contains=nginx/1.29; output -->
```bash
curl -sI http://localhost:8080 | grep -i '^server'
curl -sI http://localhost:8081 | grep -i '^server'
```

```text
Server: nginx/1.29.8
Server: nginx/1.30.5
```

## Prevention

- Keep a port plan for local development (for example 8080 web, 8081 API, 5432 database) and write it into the
  Compose file (lesson 064).
- Remove containers you no longer need (`docker rm -f`, `docker compose down`) instead of leaving them running.
- Publish to `127.0.0.1:PORT:…` for local tools so you do not also expose them to your network (lesson 051).
- In scripts, let Docker pick a free host port with `-p 80` and read it back with `docker port NAME 80`.

## Cleanup

<!-- test -->
```bash
docker rm -f web-old web-new > /dev/null
```

Next: [Problem 05 · Application not reachable](../05-application-not-reachable/README.md)
