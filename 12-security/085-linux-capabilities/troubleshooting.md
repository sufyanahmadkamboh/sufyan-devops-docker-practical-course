<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 085 · Linux capabilities · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Harden an nginx container by dropping every capability:

```bash
docker run -d --name web --cap-drop ALL -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web"
```

```bash
docker ps -a --filter name=web --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

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

```bash
docker run --rm --cap-drop ALL alpine:3.23 sysctl net.ipv4.ip_unprivileged_port_start
```

```text
net.ipv4.ip_unprivileged_port_start = 0
```

## Fix it

Add back exactly those three, and forbid any further privilege gain:

```bash
docker rm -f web > /dev/null
docker run -d --name web --cap-drop ALL --cap-add CHOWN --cap-add SETUID --cap-add SETGID \
  --security-opt no-new-privileges -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web"
```

```bash
curl -s http://localhost:8080/ | grep -o '<title>.*</title>'
```

```bash
docker inspect --format 'add={{.HostConfig.CapAdd}} drop={{.HostConfig.CapDrop}}' web
```

```text
add=[CAP_CHOWN CAP_SETGID CAP_SETUID] drop=[ALL]
```

Three capabilities instead of fourteen: `KILL`, `MKNOD`, `NET_RAW`, `DAC_OVERRIDE` and the others are gone. An image
built to run as a non-root user on a high port (lesson 081) needs **none**.
