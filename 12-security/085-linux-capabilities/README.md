# Lesson 085 · Linux capabilities

> Level 13 · Container security · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Linux splits the power of root into about 40 **capabilities**: `CHOWN` (change file owners), `NET_BIND_SERVICE`
(listen on ports below 1024), `SYS_ADMIN` (mount file systems and much more), `SYS_TIME` (set the clock) and so on.
Docker gives containers a reduced default set of 14. Most applications need none of them. The secure pattern is
**drop all, add back only what is needed**:

```text
docker run --cap-drop ALL --cap-add CHOWN …
```

## Visual

```text
  Root on the host            Container (Docker default)              --cap-drop ALL --cap-add CHOWN …
  all ~40 capabilities        14 capabilities                          only the ones the app needs
  ┌─────────────────────┐     ┌───────────────────────────┐            ┌──────────────────────────┐
  │ SYS_ADMIN SYS_TIME  │     │ CHOWN DAC_OVERRIDE FOWNER │            │ CHOWN SETUID SETGID      │
  │ SYS_MODULE NET_ADMIN│     │ FSETID KILL SETGID SETUID │            └──────────────────────────┘
  │ CHOWN SETUID KILL … │     │ SETPCAP NET_BIND_SERVICE  │
  └─────────────────────┘     │ NET_RAW SYS_CHROOT MKNOD  │
                              │ AUDIT_WRITE SETFCAP       │            --privileged = all of them
                              └───────────────────────────┘            (never, lesson 080)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-085 12-security/085-linux-capabilities/examples
cd ~/docker-practice/lesson-085
cat caps.sh | head -2
```

`caps.sh` prints the names of the capabilities the current process has (it decodes the `CapEff` line of
`/proc/self/status`). It is mounted read-only into each container below.

## Demonstration

The default set of a container that runs as root:

<!-- test: contains=CHOWN; contains=NET_BIND_SERVICE; output -->
```bash
docker run --rm -v "$(pwd)/caps.sh:/caps.sh:ro" alpine:3.23 sh /caps.sh
```

```text
CapEff=00000000a80425fb: CHOWN DAC_OVERRIDE FOWNER FSETID KILL SETGID SETUID SETPCAP NET_BIND_SERVICE NET_RAW SYS_CHROOT MKNOD AUDIT_WRITE SETFCAP
```

The same container with every capability dropped:

<!-- test: contains=(none); output -->
```bash
docker run --rm --cap-drop ALL -v "$(pwd)/caps.sh:/caps.sh:ro" alpine:3.23 sh /caps.sh
```

```text
CapEff=0000000000000000: (none)
```

Root without capabilities is a lot less powerful. With the default set, root may give a file away; without
`CHOWN`, it may not:

<!-- test: contains=chown ok; contains=Operation not permitted; output -->
```bash
docker run --rm alpine:3.23 sh -c 'touch /tmp/f && chown nobody /tmp/f && echo "chown ok"'
docker run --rm --cap-drop ALL alpine:3.23 sh -c 'touch /tmp/f && chown nobody /tmp/f' 2>&1 || true
```

```text
chown ok
chown: /tmp/f: Operation not permitted
```

Capabilities outside the default set are refused even to root: setting the clock needs `SYS_TIME`, which no
container has by default (and which would change the **host's** clock if you gave it):

<!-- test: contains=can't set date; output -->
```bash
docker run --rm alpine:3.23 date -s '2030-01-01 00:00' 2>&1 || true
```

```text
Tue Jan  1 00:00:00 UTC 2030
date: can't set date: Operation not permitted
```

## Command breakdown

| Flag | What it does |
|---|---|
| `--cap-drop ALL` | remove every capability |
| `--cap-add NAME` | add one capability (without the `CAP_` prefix), e.g. `NET_BIND_SERVICE` |
| `--cap-drop NAME` | remove one capability from the default set |
| `--security-opt no-new-privileges` | setuid programs cannot gain more privileges than the process already has |
| `docker inspect --format '{{.HostConfig.CapAdd}} {{.HostConfig.CapDrop}}'` | the capability changes of a container |

## Hands-on lab

**Instructions.** Start a container with `--cap-drop ALL --cap-add CHOWN` and show with `caps.sh` that it has exactly
one capability, then show that `chown` works again.

**Expected result.** `CapEff=…: CHOWN` and `chown ok`.

**Verification.**

<!-- test: contains=: CHOWN; contains=chown ok -->
```bash
docker run --rm --cap-drop ALL --cap-add CHOWN -v "$(pwd)/caps.sh:/caps.sh:ro" alpine:3.23 \
  sh -c 'sh /caps.sh; touch /tmp/f && chown nobody /tmp/f && echo "chown ok"'
```

## Break it

Harden an nginx container by dropping every capability:

<!-- test: contains=started web -->
```bash
docker run -d --name web --cap-drop ALL -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web"
```

<!-- test: retry=5; contains=Exited (1) -->
```bash
docker ps -a --filter name=web --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

<!-- test: contains=Operation not permitted; output -->
```bash
docker logs web 2>&1 | tail -1
```

```text
nginx: [emerg] chown("/var/cache/nginx/client_temp", 101) failed (1: Operation not permitted)
```

`chown("/var/cache/nginx/client_temp", 101) failed (1: Operation not permitted)`: the nginx master process starts as
root and prepares folders for its worker processes, which run as the `nginx` user (uid 101). Giving a folder to
another user needs `CHOWN`; switching the workers to that user needs `SETUID` and `SETGID`. Find which capabilities a
program needs by reading its errors one at a time, as here, or from its documentation.

What about port 80? On a normal Linux system, ports below 1024 need `NET_BIND_SERVICE`. Docker sets the kernel option
`net.ipv4.ip_unprivileged_port_start` to `0` inside each container's network namespace, so any port is allowed:

<!-- test: contains=ip_unprivileged_port_start = 0; output -->
```bash
docker run --rm --cap-drop ALL alpine:3.23 sysctl net.ipv4.ip_unprivileged_port_start
```

```text
net.ipv4.ip_unprivileged_port_start = 0
```

## Fix it

Add back exactly those three, and forbid any further privilege gain:

<!-- test: contains=started web -->
```bash
docker rm -f web > /dev/null
docker run -d --name web --cap-drop ALL --cap-add CHOWN --cap-add SETUID --cap-add SETGID \
  --security-opt no-new-privileges -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web"
```

<!-- test: retry=10; contains=Welcome to nginx -->
```bash
curl -s http://localhost:8080/ | grep -o '<title>.*</title>'
```

<!-- test: contains=CHOWN; output -->
```bash
docker inspect --format 'add={{.HostConfig.CapAdd}} drop={{.HostConfig.CapDrop}}' web
```

```text
add=[CAP_CHOWN CAP_SETGID CAP_SETUID] drop=[ALL]
```

Three capabilities instead of fourteen: `KILL`, `MKNOD`, `NET_RAW`, `DAC_OVERRIDE` and the others are gone. An image
built to run as a non-root user on a high port (lesson 081) needs **none**.

## Practice challenge

The Python web server from lesson 084 runs as root on port 8081. Find the smallest set of capabilities it needs: start
it with `--cap-drop ALL` and check that it still answers. Then show which capabilities the server process actually has
while it runs.

<details>
<summary>Solution</summary>

<!-- test: contains=started py -->
```bash
docker run -d --name py --cap-drop ALL -p 8081:8081 python:3.14-alpine python -m http.server 8081 > /dev/null && echo "started py"
```

<!-- test: retry=10; contains=Directory listing; output -->
```bash
curl -s http://localhost:8081/ | grep -o '<title>.*</title>'
```

```text
<title>Directory listing for /</title>
```

<!-- test: contains=0000000000000000; output -->
```bash
docker exec py grep CapEff /proc/1/status
```

```text
CapEff:	0000000000000000
```

The web server runs as root, yet with **no** capability at all, and it still works: most applications need none. As
root without capabilities it cannot change file owners, kill other users' processes, or bypass file permissions.

</details>

## Real-world example

Kubernetes security contexts use the same names: `capabilities: { drop: ["ALL"], add: ["NET_BIND_SERVICE"] }` and
`allowPrivilegeEscalation: false` (the equivalent of `no-new-privileges`). The `restricted` Pod Security Standard
requires dropping `ALL` and allows adding back only `NET_BIND_SERVICE`. Not every container runtime sets
`ip_unprivileged_port_start` like Docker does, which is one more reason production images listen on high ports and
run as non-root users.

## Recap

- Capabilities split root's power into pieces; containers get 14 of about 40 by default.
- `--cap-drop ALL`, then `--cap-add` only what the application proves it needs (read its `Operation not permitted`
  errors).
- `--security-opt no-new-privileges` stops setuid programs from gaining privileges.
- Docker allows every port without `NET_BIND_SERVICE` (`ip_unprivileged_port_start = 0`); most applications need no
  capabilities at all.

## Cleanup

<!-- test -->
```bash
docker rm -f web py > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-085
```

Next: [Lesson 086 · Resource limits for security](../086-resource-limits-for-security/README.md)
