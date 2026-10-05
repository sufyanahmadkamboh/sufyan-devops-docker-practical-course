<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 003 · Docker vs virtual machines · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
engine=$(docker info --format '{{.KernelVersion}}')
alpine=$(docker run --rm alpine:3.23 uname -r)
debian=$(docker run --rm debian:13-slim uname -r)
echo "engine: $engine"
echo "alpine: $alpine"
echo "debian: $debian"
[ "$engine" = "$alpine" ] && [ "$alpine" = "$debian" ] && echo "same kernel in every container"
```

```bash
docker run --rm alpine:3.23 ps
```

```bash
time docker run --rm alpine:3.23 true
```

```bash
docker image ls alpine:3.23
```

## Hands-on lab

```bash
[ "$(docker run --rm ubuntu:24.04 uname -r)" = "$(docker run --rm busybox:1.37 uname -r)" ] && echo "kernels match"
```

## Break it

```bash
docker run --rm alpine:3.23 sysctl -w net.ipv4.ip_forward=0
```

## Troubleshoot it

```bash
docker run --rm alpine:3.23 sh -c 'grep " /proc/sys " /proc/mounts'
```

## Fix it

```bash
docker run --rm --sysctl net.ipv4.ip_forward=1 alpine:3.23 sysctl net.ipv4.ip_forward
```

## Practice challenge

```bash
docker run -d --name sleeper alpine:3.23 sleep 300 > /dev/null
docker run --rm alpine:3.23 ps | grep -q sleep && echo "sleep-visible" || echo "sleep-absent"
docker rm -f sleeper > /dev/null
```
