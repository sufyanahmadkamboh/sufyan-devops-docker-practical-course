<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 080 · The attack surface of a container · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
echo "ubuntu:24.04  $(docker run --rm ubuntu:24.04 sh -c 'ls /bin /sbin /usr/bin /usr/sbin | wc -l') programs"
echo "alpine:3.23   $(docker run --rm alpine:3.23 sh -c 'ls /bin /sbin /usr/bin /usr/sbin | wc -l') programs"
```

```bash
docker run --rm ubuntu:24.04 find / -xdev -perm -4000 -type f
```

```bash
docker run --rm gcr.io/distroless/static-debian12:nonroot sh -c 'echo hello' 2>&1
```

## Hands-on lab

```bash
echo "debian:13-slim $(docker run --rm debian:13-slim sh -c "dpkg-query -f '.\n' -W | wc -l") packages"
echo "alpine:3.23    $(docker run --rm alpine:3.23 sh -c 'apk info | wc -l') packages"
```

## Break it

```bash
echo "normal:     $(docker run --rm alpine:3.23 sh -c 'ls /dev | wc -l') devices, $(docker run --rm alpine:3.23 grep CapEff /proc/self/status)"
echo "privileged: $(docker run --rm --privileged alpine:3.23 sh -c 'ls /dev | wc -l') devices, $(docker run --rm --privileged alpine:3.23 grep CapEff /proc/self/status)"
```

## Troubleshoot it

```bash
docker run --rm --privileged alpine:3.23 sysctl -w net.ipv4.ip_forward=1
```

```bash
docker run -d --name too-powerful --privileged alpine:3.23 sleep 300 > /dev/null
docker ps -q | xargs docker inspect --format '{{.Name}} Privileged={{.HostConfig.Privileged}}'
```

## Fix it

```bash
docker rm -f too-powerful > /dev/null
docker run -d --name just-enough alpine:3.23 sleep 300 > /dev/null
docker inspect --format '{{.Name}} Privileged={{.HostConfig.Privileged}}' just-enough
docker rm -f just-enough > /dev/null
```

## Practice challenge

```bash
for image in ubuntu:24.04 alpine:3.23; do
  echo "$image: $(docker run --rm "$image" sh -c 'for t in sh bash apt-get apk wget curl; do command -v $t > /dev/null && printf "%s " $t; done')"
done
```

## Cleanup

```bash
docker rm -f too-powerful just-enough > /dev/null 2>&1 || true
```
