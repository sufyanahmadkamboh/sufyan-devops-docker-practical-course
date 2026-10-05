<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 004 · Docker architecture · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

`docker run` = pull (if needed) + create + start. Using only `docker image pull`, `docker container create` and
`docker container start -a`, run `busybox:1.37` with the command `echo it works`, then remove the container.

## Solution

```bash
docker image inspect busybox:1.37 > /dev/null 2>&1 || docker image pull -q busybox:1.37
docker container create --name by-hand busybox:1.37 echo it works > /dev/null
docker container start -a by-hand
docker container rm by-hand > /dev/null
```

```text
it works
```

Each command is one request to the daemon. `docker run` sends the same requests for you, and like the first line it
only pulls when the image is missing: an explicit `docker image pull` always asks the registry for the latest digest.
