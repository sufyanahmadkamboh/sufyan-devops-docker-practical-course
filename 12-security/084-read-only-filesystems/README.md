# Lesson 084 · Read-only file systems

> Level 13 · Container security · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

By default every container has a **writable layer**: a process can change any file it has permission to, including
the application's own code, configuration and binaries. An attacker who gets in can therefore install tools or plant a
backdoor that survives until the container is removed. `--read-only` makes the container's whole file system read-only.
The few places the application really writes to become **tmpfs** mounts (in memory, empty at every start) or volumes.

## Visual

```text
  Default                                        --read-only  --tmpfs /var/cache/nginx  --tmpfs /run

  ┌───────────────────────────────┐              ┌───────────────────────────────┐
  │ writable layer  (anything)    │              │ /var/cache/nginx  tmpfs (RAM) │ ← writable, empty at start
  ├───────────────────────────────┤              │ /run              tmpfs (RAM) │ ← writable, empty at start
  │ image layers (read-only)      │              ├───────────────────────────────┤
  └───────────────────────────────┘              │ everything else   READ-ONLY   │ ← code, config, binaries
   attacker can change code, add tools           └───────────────────────────────┘
                                                  attacker cannot change the application
```

## Lab setup

No files are needed: this lesson uses the official `nginx` and `alpine` images.

## Demonstration

A normal container may write anywhere it has permission:

<!-- test: contains=written; output -->
```bash
docker run --rm alpine:3.23 sh -c 'echo "attacker was here" > /etc/motd && echo "written to /etc/motd"'
```

```text
written to /etc/motd
```

With `--read-only`, it may not:

<!-- test: fail; contains=Read-only file system; output -->
```bash
docker run --rm --read-only alpine:3.23 sh -c 'echo "attacker was here" > /etc/motd'
```

```text
sh: can't create /etc/motd: Read-only file system
```

A **tmpfs** mount gives back exactly one writable folder, in memory:

<!-- test: contains=tmpfs; contains=scratch ok; output -->
```bash
docker run --rm --read-only --tmpfs /tmp alpine:3.23 sh -c 'echo data > /tmp/scratch && echo "scratch ok"; grep " /tmp " /proc/mounts'
```

```text
scratch ok
tmpfs /tmp tmpfs rw,nosuid,nodev,noexec,relatime 0 0
```

## Command breakdown

| Flag | What it does |
|---|---|
| `--read-only` | mount the container's root file system read-only |
| `--tmpfs /path` | an empty, writable, in-memory folder at `/path` (lost when the container stops) |
| `--tmpfs /path:size=16m` | the same, limited to 16 MB |
| `-v NAME:/path` | a writable volume, for data that must be kept (lesson 055) |
| `docker diff NAME` | the files a container changed in its writable layer (A added, C changed, D deleted) |

## Hands-on lab

**Instructions.** Start an nginx container normally, request its page once, and use `docker diff` to list the files
and folders nginx changed in the container's writable layer. These are the places a read-only nginx will need.

**Expected result.** Entries under `/var/cache/nginx` and `/run` (plus configuration files the entrypoint script
adjusts in `/etc/nginx`).

**Verification.**

<!-- test: contains=/var/cache/nginx -->
```bash
docker run -d --name web-rw nginx:1.30-alpine > /dev/null
sleep 2
docker diff web-rw
docker rm -f web-rw > /dev/null
```

## Break it

Start nginx read-only:

<!-- test: contains=web-ro -->
```bash
docker run -d --name web-ro --read-only -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web-ro"
```

<!-- test: retry=5; contains=Exited (1) -->
```bash
docker ps -a --filter name=web-ro --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

The container stopped almost immediately. The last log lines explain it:

<!-- test: contains=Read-only file system; output -->
```bash
docker logs web-ro 2>&1 | tail -2
```

```text
2026/10/05 16:57:12 [emerg] 1#1: mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)
nginx: [emerg] mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)
```

`mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)`: nginx needs a few writable folders for
temporary files and its PID file. `docker diff` in the lab showed which. This is the normal process for any image: run
it once writable, list what it writes, and decide for each folder: tmpfs (scratch) or a volume (data to keep).

## Fix it

Give nginx the two writable folders it needs as tmpfs mounts; everything else stays read-only:

<!-- test: contains=web-ro -->
```bash
docker rm -f web-ro > /dev/null
docker run -d --name web-ro --read-only --tmpfs /var/cache/nginx --tmpfs /run -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web-ro"
```

<!-- test: retry=10; contains=Welcome to nginx -->
```bash
curl -s http://localhost:8080/ | grep -o '<title>.*</title>'
```

<!-- test: contains=Read-only file system; output -->
```bash
docker exec web-ro sh -c 'echo hacked > /usr/share/nginx/html/index.html' 2>&1 || true
```

```text
sh: can't create /usr/share/nginx/html/index.html: Read-only file system
```

nginx serves its page, and the page cannot be replaced from inside the container.

## Practice challenge

Run the Python built-in web server (`python -m http.server 8081`) from `python:3.14-alpine` with a read-only root
file system, serving files from a tmpfs at `/srv`. Write a file into `/srv` with `docker exec`, then fetch it with
`curl`.

<details>
<summary>Solution</summary>

<!-- test: contains=py-ro -->
```bash
docker run -d --name py-ro --read-only --tmpfs /srv -w /srv -p 8081:8081 python:3.14-alpine python -m http.server 8081 > /dev/null && echo "started py-ro"
```

<!-- test: retry=10; contains=hello from tmpfs; output -->
```bash
docker exec py-ro sh -c 'echo "hello from tmpfs" > /srv/hello.txt'
curl -s http://localhost:8081/hello.txt
```

```text
hello from tmpfs
```

Python does not need to write anywhere else, so `/srv` is the only writable folder. Anything written there disappears
when the container stops: that is what you want for scratch data.

</details>

## Real-world example

Kubernetes has the same switch: `securityContext.readOnlyRootFilesystem: true`, with `emptyDir` volumes for the folders
the application writes to. Many security baselines (for example the CIS benchmarks) require it. When an attacker
exploits a web application in such a container, they cannot drop a web shell into the application's folder or replace
its binaries.

## Recap

- `--read-only` prevents any change to the container's file system: code, configuration and binaries stay intact.
- Find what an application writes with `docker diff`; give it `--tmpfs` (scratch) or volumes (data).
- `Read-only file system` errors name the exact path that needs to be writable.

## Cleanup

<!-- test -->
```bash
docker rm -f web-rw web-ro py-ro > /dev/null 2>&1 || true
```

Next: [Lesson 085 · Linux capabilities](../085-linux-capabilities/README.md)
