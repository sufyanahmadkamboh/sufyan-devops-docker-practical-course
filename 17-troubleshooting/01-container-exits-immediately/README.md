# Troubleshooting problem 01 · Container exits immediately

> ⏱ 15 minutes · run every command from the course folder · related lessons: 009, 014, 027

## Problem

A team packages its static site with Nginx. `docker run -d` prints a container ID, so everything looks fine, but the
site is not reachable and the container is gone from `docker ps` a second later.

## Symptoms

Reproduce it:

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-01 17-troubleshooting/01-container-exits-immediately/examples
cd ~/docker-practice/trouble-01/broken
docker build -q -t menu-site:broken . > /dev/null
docker run -d --name menu -p 8080:80 menu-site:broken
```

<!-- test: contains=Exited (0); output -->
```bash
sleep 2
docker ps --filter name=menu --format '{{.Names}}: {{.Status}}'
docker ps -a --filter name=menu --format '{{.Names}}: {{.Status}}'
```

```text
menu: Exited (0) 2 seconds ago
```

`docker ps` (running containers only) prints nothing; `docker ps -a` (all containers) shows it **exited**, with code 0.

## Investigation

**1. What did the container print before it stopped?** The logs survive the exit:

<!-- test: contains=start worker processes; output -->
```bash
docker logs menu 2>&1 | grep -E 'Configuration complete|nginx/|start worker processes'
```

```text
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/10/05 10:22:53 [notice] 1#1: nginx/1.30.5
2026/10/05 10:22:53 [notice] 30#30: start worker processes
```

No error at all: Nginx started successfully.

**2. How did it exit?**

<!-- test: contains=exit code 0; output -->
```bash
docker inspect --format 'exit code {{.State.ExitCode}}, OOM killed: {{.State.OOMKilled}}, error: "{{.State.Error}}"' menu
```

```text
exit code 0, OOM killed: false, error: ""
```

Exit code 0 is a *successful* end, not a crash. Something finished normally.

**3. Which command did the container run?**

<!-- test: contains=[nginx]; output -->
```bash
docker inspect --format 'Cmd: {{.Config.Cmd}}  Entrypoint: {{.Config.Entrypoint}}' menu
```

```text
Cmd: [nginx]  Entrypoint: [/docker-entrypoint.sh]
```

## Commands

| Command | What it tells you |
|---|---|
| `docker ps -a` | stopped containers too, with `Exited (CODE)` |
| `docker logs NAME` | everything process 1 printed, even after the container stopped |
| `docker inspect --format '{{.State.ExitCode}}'` | how it ended: 0 success, 1 app error, 125–127 Docker/command errors, 137 killed |
| `docker inspect --format '{{.Config.Cmd}}'` | the command the container actually ran (lessons 027–029) |

## Output interpretation

- `Exited (0)` plus logs that end normally means **the main process finished on purpose**. A container lives exactly
  as long as its process 1 (lesson 009).
- `nginx` without options starts a master process that forks into the **background** (daemon mode) and then exits. On
  a server, systemd follows the daemon; in a container, process 1 ending ends the container.
- Other codes point elsewhere: 1 = the application failed (read the logs), 127 = command not found
  ([problem 02](../02-wrong-command/README.md)), 137 = killed ([problem 22](../22-memory-limit-exceeded/README.md)).

## Root cause

`CMD ["nginx"]` starts Nginx as a daemon. The foreground process returns as soon as Nginx has gone to the background,
so the container's main process ends with status 0 and Docker stops the container.

## Fix

Run the server in the **foreground**. The fixed Dockerfile keeps Nginx as process 1:

<!-- test: contains=daemon off; output -->
```bash
cd ~/docker-practice/trouble-01
grep CMD broken/Dockerfile fixed/Dockerfile
```

```text
broken/Dockerfile:CMD ["nginx"]
fixed/Dockerfile:CMD ["nginx", "-g", "daemon off;"]
```

<!-- test -->
```bash
docker rm menu > /dev/null
docker build -q -t menu-site:fixed fixed > /dev/null
docker run -d --name menu -p 8080:80 menu-site:fixed
```

## Verification

<!-- test: contains=Up; output -->
```bash
sleep 2
docker ps --filter name=menu --format '{{.Names}}: {{.Status}}'
```

```text
menu: Up 2 seconds
```

<!-- test: retry=10; contains=Cafe menu; output -->
```bash
curl -s http://localhost:8080
```

```text
<h1>Cafe menu</h1>
```

## Prevention

- Every container's main command must run in the foreground: `nginx -g 'daemon off;'`, `gunicorn` without
  `--daemon`, `node server.js`, never `service x start` or a script that starts something with `&` and returns.
- Start from the official image's default `CMD` unless you have a reason not to (the `nginx` image already sets
  `daemon off;`).
- After `docker run -d`, check `docker ps` (not just the printed ID), and add a `HEALTHCHECK` (lesson 092).

## Cleanup

<!-- test -->
```bash
docker rm -f menu > /dev/null
docker image rm menu-site:broken menu-site:fixed > /dev/null
rm -rf ~/docker-practice/trouble-01
```

Next: [Problem 02 · Wrong command](../02-wrong-command/README.md)
