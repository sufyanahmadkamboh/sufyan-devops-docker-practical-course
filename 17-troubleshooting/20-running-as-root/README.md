# Troubleshooting problem 20 · Running as root

> ⏱ 20 minutes · run every command from the course folder · related lessons: 033, 080, 081, 085

## Problem

A penetration test of the opening-hours website reports: "a vulnerability in the web server gives an attacker a shell,
and that shell is root". Nothing is broken functionally; the finding is that a compromise would be total inside the
container. Verify the finding, and fix it.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-20 17-troubleshooting/20-running-as-root/examples
cd ~/docker-practice/trouble-20
docker build -q -t hours:broken broken > /dev/null
docker run -d --name hours -p 8080:8080 hours:broken > /dev/null
```

<!-- test: retry=10; contains=Opening hours -->
```bash
curl -s http://localhost:8080
```

`docker exec` runs with the container's user, so it shows what an attacker's shell would get:

<!-- test: contains=uid=0(root); output -->
```bash
docker exec hours id
```

```text
uid=0(root) gid=0(root) groups=0(root)
```

## Investigation

**1. Who runs the server process?**

<!-- test: contains=root; output -->
```bash
docker image inspect --format 'image user: "{{.Config.User}}" (empty = root)' hours:broken
docker top hours -o user,pid,args
```

```text
image user: "" (empty = root)
USER                PID                 COMMAND
root                2445224             python -m http.server 8080 --directory public
```

**2. What can root do inside the container?** Everything the attacker wants: change the website, read password
hashes, install tools:

<!-- test: contains=defaced; contains=root:; output -->
```bash
docker exec hours sh -c 'echo "<h1>defaced</h1>" > /app/public/index.html'
curl -s http://localhost:8080
docker exec hours head -1 /etc/shadow | cut -c1-5
docker exec hours sh -c 'command -v apt-get'
```

```text
<h1>defaced</h1>
root:
/usr/bin/apt-get
```

**3. Root in a container is root on the kernel.** Without user namespaces, uid 0 inside is uid 0 on the host: a
container escape (a kernel bug, a mounted Docker socket, `--privileged`) gives root on the server (lesson 080).

## Commands

| Command | What it tells you |
|---|---|
| `docker image inspect --format '{{.Config.User}}' IMAGE` | the image's user; empty means root |
| `docker exec NAME id` | the identity a process in the container has |
| `docker top NAME -o user,pid,args` | the user of each process, seen from the engine |
| `docker inspect --format '{{.HostConfig.Privileged}} {{.HostConfig.CapAdd}}' NAME` | extra powers on top of root |

## Output interpretation

`uid=0(root)` and an empty `Config.User` mean the image never switched user. Root inside the container may write to
every file of the image, read `/etc/shadow` and use the package manager. Docker limits it (capabilities, seccomp,
namespaces) but the container is still the attacker's.

## Root cause

The Dockerfile has no `USER` instruction, so the server runs as root, the default.

## Fix

Create an unprivileged user and switch to it; keep the content owned by root so the server can read it but not change
it:

<!-- test: contains=USER 10001; output -->
```bash
grep -n 'useradd\|USER\|COPY' fixed/Dockerfile
```

```text
2:RUN groupadd --system --gid 10001 web && useradd --system --uid 10001 --gid web --no-create-home web
5:COPY public/ public/
7:USER 10001:10001
```

<!-- test -->
```bash
docker rm -f hours > /dev/null
docker build -q -t hours:fixed fixed > /dev/null
docker run -d --name hours -p 8080:8080 --cap-drop ALL --security-opt no-new-privileges hours:fixed > /dev/null
```

## Verification

<!-- test: retry=10; contains=Opening hours; contains=uid=10001; output -->
```bash
curl -s http://localhost:8080
docker exec hours id
```

```text
<h1>Opening hours: 8:00 to 18:00</h1>
uid=10001(web) gid=10001(web) groups=10001(web)
```

The same attack steps now fail:

<!-- test: contains=Permission denied; output -->
```bash
docker exec hours sh -c 'echo "<h1>defaced</h1>" > /app/public/index.html' 2>&1 || true
docker exec hours head -1 /etc/shadow 2>&1 || true
```

```text
sh: 1: cannot create /app/public/index.html: Permission denied
head: cannot open '/etc/shadow' for reading: Permission denied
```

## Prevention

- Every image ends with `USER` (a numeric uid works everywhere, including Kubernetes `runAsNonRoot`, lesson 081).
- Application files owned by root and read-only for the app; only data paths writable
  ([problem 13](../13-cannot-write-files/README.md)).
- Run with `--cap-drop ALL` and `--security-opt no-new-privileges`; never `--privileged` or a mounted Docker socket
  for applications (lesson 085).
- Check it in CI: fail the build when `docker image inspect --format '{{.Config.User}}'` is empty or `root`.

## Cleanup

<!-- test -->
```bash
docker rm -f hours > /dev/null
docker image rm hours:broken hours:fixed > /dev/null
rm -rf ~/docker-practice/trouble-20
```

Next: [Problem 21 · Healthcheck failure](../21-healthcheck-failure/README.md)
