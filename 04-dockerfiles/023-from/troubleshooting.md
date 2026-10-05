<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 023 · FROM: choosing a base image · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A build step copied from a Debian-based Dockerfile, now on Alpine:

```bash
printf 'FROM alpine:3.23\nRUN bash -c "echo preparing the image"\n' > Dockerfile.alpine
docker build --progress=plain -f Dockerfile.alpine -t base-demo:alpine . 2>&1 | grep -E 'not found|ERROR'
```

```text
#5 0.175 /bin/sh: bash: not found
#5 ERROR: process "/bin/sh -c bash -c \"echo preparing the image\"" did not complete successfully: exit code: 127
0.175 /bin/sh: bash: not found
ERROR: failed to build: failed to solve: process "/bin/sh -c bash -c \"echo preparing the image\"" did not complete successfully: exit code: 127
```

## Troubleshoot it

Exit code **127** always means "command not found", and the step's output names it: `bash: not found`. The base image
does not contain the program. Check what the image provides:

```bash
docker run --rm alpine:3.23 sh -c 'command -v bash || echo "no bash"; ls -l /bin/sh'
```

```text
no bash
lrwxrwxrwx    1 root     root            12 Sep 17 17:32 /bin/sh -> /bin/busybox
```

Alpine's shell is BusyBox `sh`. The same happens with `apt-get` on Alpine, `apk` on Debian, or any shell at all in
distroless images.

## Fix it

Either write the step for the base you chose (POSIX `sh` is enough here), or install the missing tool with the base's
package manager (`RUN apk add --no-cache bash`), or choose a base that has it. The simplest fix:

```bash
printf 'FROM alpine:3.23\nRUN sh -c "echo preparing the image"\n' > Dockerfile.alpine
docker build --progress=plain -f Dockerfile.alpine -t base-demo:alpine . 2>&1 | grep "preparing the image"
```
