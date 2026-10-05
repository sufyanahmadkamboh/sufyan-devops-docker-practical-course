# Troubleshooting problem 13 · Cannot write files

> ⏱ 20 minutes · run every command from the course folder · related lessons: 033, 053, 055, 084

## Problem

The uploads service must write to its `data/` directory. After moving it to a non-root user it fails at start-up, and
after the next hardening step (a read-only root file system) it fails again with a different message.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-13 17-troubleshooting/13-cannot-write-files/examples
cd ~/docker-practice/trouble-13
docker build -q -t uploads:broken broken > /dev/null
docker run -d --name uploads uploads:broken > /dev/null
```

<!-- test: contains=Permission denied; output -->
```bash
sleep 2
docker ps -a --filter name=uploads --format '{{.Names}}: {{.Status}}'
docker logs uploads 2>&1 | tail -1
```

```text
uploads: Exited (1) 1 second ago
PermissionError: [Errno 13] Permission denied: 'data/visits.log'
```

## Investigation

**1. Who runs it, and who owns the directory?**

<!-- test: contains=root root; output -->
```bash
docker run --rm uploads:broken sh -c 'id; ls -ld /app /app/data'
```

```text
uid=10001(app) gid=999(app) groups=999(app)
drwxr-xr-x 1 root root 4096 Oct  5 10:55 /app
drwxr-xr-x 2 root root 4096 Oct  5 10:55 /app/data
```

`data` was created by `RUN mkdir data`, which runs as root during the build: root owns it, mode `drwxr-xr-x` (only the
owner may write). The process runs as `app`.

**2. The second failure.** Fix the ownership (the `fixed/` Dockerfile), then harden the container with a read-only
root file system, as the security review asks (lesson 084):

<!-- test: contains=chown app:app; output -->
```bash
grep -n 'mkdir\|VOLUME' broken/Dockerfile fixed/Dockerfile
```

```text
broken/Dockerfile:5:RUN mkdir data
fixed/Dockerfile:6:RUN mkdir data && chown app:app data
fixed/Dockerfile:7:VOLUME /app/data
```

<!-- test: fail; contains=Read-only file system; output -->
```bash
docker rm uploads > /dev/null
docker build -q -t uploads:fixed fixed > /dev/null
docker run --rm --read-only --volume uploads-data:/app/data --user app uploads:fixed \
  sh -c 'touch /app/data/ok && echo "data: writable" && touch /app/cache.tmp' 2>&1
```

```text
data: writable
touch: cannot touch '/app/cache.tmp': Read-only file system
```

The `data` volume is writable; every other path, such as `/app/cache.tmp`, is now read-only. **3. Which paths does the
application write to besides `data/`?** Python writes nothing else here, but many runtimes write to `/tmp`:

<!-- test: fail; contains=Read-only file system; output -->
```bash
docker run --rm --read-only uploads:fixed sh -c 'touch /tmp/x' 2>&1
```

```text
touch: cannot touch '/tmp/x': Read-only file system
```

## Commands

| Command | What it tells you |
|---|---|
| `docker run --rm IMAGE sh -c 'id; ls -ld DIR'` | the process user and the directory owner and mode |
| `docker inspect --format '{{.HostConfig.ReadonlyRootfs}}' NAME` | whether the root file system is read-only |
| `docker inspect --format '{{json .Mounts}}' NAME` | the writable mounts (volumes, bind mounts, tmpfs) |
| `docker diff NAME` | which files a container changed in its writable layer (lesson 053) |

## Output interpretation

| Message | Meaning | Fix |
|---|---|---|
| `Permission denied` | the path is writable in principle, but not by this user | change ownership in the Dockerfile |
| `Read-only file system` | nobody may write there (`--read-only`, or a `:ro` mount) | mount a volume or `tmpfs` for that path |

## Root cause

1. `data/` was created by root during the build, and the application runs as `app`.
2. With `--read-only`, every path that must be written needs its own writable mount; `/tmp` had none.

## Fix

The fixed image gives `data/` to the `app` user and declares it as a volume. At run time, keep the root file system
read-only and mount exactly the writable paths: a named volume for the data, a `tmpfs` for temporary files:

<!-- test -->
```bash
docker run -d --name uploads -p 8080:8080 --read-only \
  -v uploads-data:/app/data --tmpfs /tmp uploads:fixed > /dev/null
```

## Verification

<!-- test: retry=10; contains=visits recorded; output -->
```bash
curl -s http://localhost:8080
docker logs uploads
```

```text
uploads ok, 2 visits recorded
uploads: data directory is writable
172.17.0.1 - - [05/Oct/2026 10:55:14] "GET / HTTP/1.1" 200 -
```

<!-- test: contains=true; output -->
```bash
docker inspect --format 'read-only root: {{.HostConfig.ReadonlyRootfs}}, tmpfs: {{json .HostConfig.Tmpfs}}' uploads
docker exec uploads touch /tmp/scratch && echo "tmp: writable"
```

```text
read-only root: true, tmpfs: {"/tmp":""}
tmp: writable
```

## Prevention

- In the Dockerfile, create every directory the app writes to and `chown` it to the app user; leave the rest owned
  by root.
- List the writable paths in the image documentation and in Compose (`read_only: true`, `tmpfs: [/tmp]`, `volumes:`).
- Test the hardened run configuration in CI, not only the image.

## Cleanup

<!-- test -->
```bash
docker rm -f uploads > /dev/null
docker volume rm uploads-data > /dev/null
docker image rm uploads:broken uploads:fixed > /dev/null
rm -rf ~/docker-practice/trouble-13
```

Next: [Problem 14 · Volume not mounted](../14-volume-not-mounted/README.md)
