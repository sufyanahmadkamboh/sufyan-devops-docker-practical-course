# Troubleshooting problem 12 · Permission denied

> ⏱ 15 minutes · run every command from the course folder · related lessons: 033, 081

## Problem

A security review asked the team to run the reports service as a non-root user and to "make the settings file
private". After the change, the container stops at once with `PermissionError: [Errno 13] Permission denied`.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-12 17-troubleshooting/12-permission-denied/examples
cd ~/docker-practice/trouble-12
docker build -q -t reports:broken broken > /dev/null
docker run -d --name reports -p 8080:8080 reports:broken > /dev/null
```

<!-- test: contains=Permission denied; output -->
```bash
sleep 2
docker ps -a --filter name=reports --format '{{.Names}}: {{.Status}}'
docker logs reports 2>&1 | tail -1
```

```text
reports: Exited (1) 2 seconds ago
PermissionError: [Errno 13] Permission denied: 'settings.ini'
```

## Investigation

**1. Who runs the process?**

<!-- test: contains=app; output -->
```bash
docker image inspect --format 'User: {{.Config.User}}' reports:broken
docker run --rm reports:broken id
```

```text
User: app
uid=10001(app) gid=999(app) groups=999(app)
```

**2. Who owns the file, with which permissions?** Run `ls` in the same image (a new container, same files):

<!-- test: contains=-rw-------; output -->
```bash
docker run --rm reports:broken ls -l /app
```

```text
total 8
-rwxr-xr-x 1 root root 661 Oct  5 10:54 app.py
-rw------- 1 root root  40 Oct  5 10:54 settings.ini
```

**3. Confirm it as that user, and as root:**

<!-- test: contains=Permission denied; contains=Monthly sales reports; output -->
```bash
docker run --rm reports:broken cat settings.ini 2>&1 || true
docker run --rm --user root reports:broken cat settings.ini
```

```text
cat: settings.ini: Permission denied
[reports]
title = Monthly sales reports
```

## Commands

| Command | What it tells you |
|---|---|
| `docker run --rm IMAGE id` | the user and groups the image's processes run as |
| `docker run --rm IMAGE ls -l PATH` | owner, group and mode of the files in the image |
| `docker run --rm --user root IMAGE …` | the same check as root, to confirm it is a permission problem (debugging only) |
| `docker exec NAME id` | the same for a running container |

## Output interpretation

`-rw------- 1 root root … settings.ini`: read and write for the owner `root`, nothing for the group or others. The
process runs as `app` (uid 10001), which is neither: the kernel refuses the `open()`, Python raises
`PermissionError`, the app exits with code 1. As root it works, which proves the file is fine and the permissions
are the problem. `COPY` creates files owned by root unless told otherwise.

## Root cause

`chmod 600` made the file readable by root only, while the container runs as the non-root user `app`.

## Fix

Give the application user exactly the access it needs, no more: owned by root (the app cannot change it), readable by
the `app` group, with `COPY --chown` and `--chmod` (no extra `RUN` layer):

<!-- test: contains=--chmod=640; output -->
```bash
grep -n 'COPY\|chmod' broken/Dockerfile fixed/Dockerfile
```

```text
broken/Dockerfile:4:COPY app.py settings.ini ./
broken/Dockerfile:6:RUN chmod 600 settings.ini
fixed/Dockerfile:4:COPY app.py ./
fixed/Dockerfile:6:COPY --chown=root:app --chmod=640 settings.ini ./
```

<!-- test -->
```bash
docker rm -f reports > /dev/null
docker build -q -t reports:fixed fixed > /dev/null
docker run -d --name reports -p 8080:8080 reports:fixed > /dev/null
```

## Verification

<!-- test: retry=10; contains=Monthly sales reports: ok; output -->
```bash
curl -s http://localhost:8080
docker exec reports ls -l settings.ini
docker exec reports id
```

```text
Monthly sales reports: ok
-rw-r----- 1 root app 40 Oct  5 10:54 settings.ini
uid=10001(app) gid=999(app) groups=999(app)
```

## Prevention

- Decide ownership in the Dockerfile: `COPY --chown=USER:GROUP --chmod=MODE`. Code and configuration owned by root and
  read-only for the app; only data directories writable ([problem 13](../13-cannot-write-files/README.md)).
- Test the image as it will run: `docker run --rm IMAGE id` and `ls -l` in CI catch this before deployment.
- Never "fix" it by going back to root (`USER root`): that reopens the risk the change was meant to close
  ([problem 20](../20-running-as-root/README.md)).
- With bind mounts on Linux, the host file's numeric uid/gid apply: match the container user's uid, or use a volume.

## Cleanup

<!-- test -->
```bash
docker rm -f reports > /dev/null
docker image rm reports:broken reports:fixed > /dev/null
rm -rf ~/docker-practice/trouble-12
```

Next: [Problem 13 · Cannot write files](../13-cannot-write-files/README.md)
