<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 056 · Inspecting volumes · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A redeploy: remove the old container and start a new one from the same image. The journal should continue:

```bash
docker rm journal-1 > /dev/null
docker run --name journal-2 journal:1.0
```

```text
entry 1791197553
```

Only **one** entry: the history is gone.

## Troubleshoot it

The new container got a new, empty anonymous volume. The old one was not deleted (`docker rm` without `-v` keeps
volumes), so it is now **dangling**:

```bash
docker volume ls --filter dangling=true
```

```text
DRIVER    VOLUME NAME
local     b4ae83cca42c7bfc1db1b6a9889e8f1acbb0a33cad406e4d3b762ae78fccdb15
local     orders
```

Find the one that holds the journal by looking inside each dangling volume:

```bash
for v in $(docker volume ls -q --filter dangling=true); do
  echo "$v: $(docker run --rm -v "$v:/data:ro" alpine:3.23 sh -c 'ls /data 2>/dev/null')"
done
```

```text
b4ae83cca42c7bfc1db1b6a9889e8f1acbb0a33cad406e4d3b762ae78fccdb15: log.txt
orders: 
```

## Fix it

Recover the data into a **named** volume, and run the journal with it from now on:

```bash
old=$(for v in $(docker volume ls -q --filter dangling=true); do
  docker run --rm -v "$v:/data:ro" alpine:3.23 test -f /data/log.txt && echo "$v"
done | head -1)
docker run --rm -v "$old:/from:ro" -v journal-data:/to alpine:3.23 cp -a /from/. /to/
docker rm journal-2 > /dev/null
docker run --rm -v journal-data:/data journal:1.0
```

```text
entry 1791197551
entry 1791197559
```

Two entries: the old one, recovered, and the new one. Every later run with `-v journal-data:/data` keeps adding to the
same file. Then delete the anonymous leftovers: `docker volume prune -f`.
