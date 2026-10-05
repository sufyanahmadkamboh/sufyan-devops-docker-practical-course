# Lesson 056 · Inspecting volumes

> Level 9 · Storage · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Volumes outlive containers, so they pile up and need looking after: which volumes exist, which container uses each
one, where the data is, how big it is, and which ones nobody uses any more (**dangling**). Some volumes have no
meaningful name at all: an image that declares `VOLUME /path` gets an **anonymous volume** (a random 64-character name)
every time a container starts without a mount for that path. Anonymous volumes are where "lost" data is usually found.

## Visual

```text
 docker volume ls                       all volumes: named (app-data) and anonymous (3f9c1e…)
 docker volume ls -f dangling=true      volumes no container references → candidates for cleanup (or lost data!)
 docker volume inspect NAME             driver, mountpoint, creation date, labels
 docker ps -a --filter volume=NAME      which containers use it
 docker system df -v                    disk usage of images, containers and volumes

  image with VOLUME /data
       │  docker run IMAGE            (no -v for /data)
       ▼
  container A ──▶ anonymous volume 3f9c1e…      docker rm A → volume stays, dangling
  container B ──▶ anonymous volume 8a27d0…      a NEW, empty one: the data "disappeared"
```

## Lab setup

An image that declares a volume, like many database images do:

<!-- test: contains=/data -->
```bash
printf 'FROM alpine:3.23\nVOLUME /data\nCMD ["sh", "-c", "echo \\"entry $(date +%%s)\\" >> /data/log.txt; cat /data/log.txt"]\n' | docker build -q -t journal:1.0 - > /dev/null
docker image inspect journal:1.0 --format '{{json .Config.Volumes}}'
```

## Demonstration

Create a named volume with a label, and inspect it:

<!-- test: contains=Mountpoint; contains=team; output -->
```bash
docker volume create --label team=cafe orders > /dev/null
docker volume inspect orders
```

```text
[
    {
        "CreatedAt": "2026-10-05T10:52:30Z",
        "Driver": "local",
        "Labels": {
            "team": "cafe"
        },
        "Mountpoint": "/var/lib/docker/volumes/orders/_data",
        "Name": "orders",
        "Options": null,
        "Scope": "local"
    }
]
```

`Mountpoint` is where the engine keeps the data (inside Docker Desktop's VM on Windows and macOS: use a container to
look at it, not your file explorer). Labels let you find volumes by purpose:

<!-- test: contains=orders; output -->
```bash
docker volume ls --filter label=team=cafe
```

```text
DRIVER    VOLUME NAME
local     orders
```

Run the `journal` image without any `-v`. Docker still creates a volume, an anonymous one:

<!-- test: contains=volume; output -->
```bash
docker run --name journal-1 journal:1.0 > /dev/null
docker inspect journal-1 --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}'
```

```text
volume b4ae83cca42c7bfc1db1b6a9889e8f1acbb0a33cad406e4d3b762ae78fccdb15 -> /data
```

How big is a volume? Measure it from a container that mounts it:

<!-- test: contains=/data; output -->
```bash
volume=$(docker inspect journal-1 --format '{{range .Mounts}}{{.Name}}{{end}}')
docker run --rm -v "$volume:/data:ro" alpine:3.23 du -sh /data
```

```text
8.0K	/data
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker volume inspect NAME` | details: `Driver`, `Mountpoint`, `CreatedAt`, `Labels`, `Scope` |
| `docker volume create --label K=V NAME` | a volume with metadata |
| `docker volume ls --filter label=K=V` | volumes with that label (also `dangling=true`, `name=…`) |
| `docker system df -v` | disk usage per image, container and volume |
| `docker volume prune` | delete unused **anonymous** volumes (`-a`: unused named ones too) |

## Hands-on lab

**Instructions.** Show the creation date and the driver of `orders`, and list every container that uses the anonymous
volume of `journal-1`.

**Expected result.** A timestamp and `local`; the container `journal-1`.

**Verification.**

<!-- test: contains=local; contains=journal-1 -->
```bash
docker volume inspect orders --format '{{.CreatedAt}} {{.Driver}}'
docker ps -a --filter volume="$(docker inspect journal-1 --format '{{range .Mounts}}{{.Name}}{{end}}')" --format '{{.Names}}'
```

## Break it

A redeploy: remove the old container and start a new one from the same image. The journal should continue:

<!-- test: contains=entry; output -->
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

<!-- test: contains=DRIVER; output -->
```bash
docker volume ls --filter dangling=true
```

```text
DRIVER    VOLUME NAME
local     b4ae83cca42c7bfc1db1b6a9889e8f1acbb0a33cad406e4d3b762ae78fccdb15
local     orders
```

Find the one that holds the journal by looking inside each dangling volume:

<!-- test: contains=log.txt; output -->
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

<!-- test: contains=entry; output -->
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

## Practice challenge

Find out how much disk space all your volumes use, and which volume is the largest, using `docker system df -v`.

<details>
<summary>Solution</summary>

<!-- test: contains=Local Volumes space usage; output -->
```bash
docker system df -v | grep -A6 '^Local Volumes space usage:'
```

```text
Local Volumes space usage:

VOLUME NAME                                                        LINKS     SIZE
a20fecfb516f4dbc6667963aa462ef1868e56c6b29276fe0ab1d3dfd0b22d985   0         17B
journal-data                                                       0         34B
b4ae83cca42c7bfc1db1b6a9889e8f1acbb0a33cad406e4d3b762ae78fccdb15   0         17B
orders                                                             0         0B
```

The `SIZE` column shows each volume's size and `LINKS` how many containers use it (0 = dangling).

</details>

## Real-world example

A developer's laptop runs out of disk space. `docker system df` shows 30 volumes, most of them anonymous: every
`docker run` of a database image without `-v` left one behind. They prune the dangling ones, and switch their scripts
to named volumes (`-v pgdata:/var/lib/postgresql`) so the data has a name, survives redeploys and is easy to back up.

## Recap

- `docker volume ls`, `inspect` and `docker ps -a --filter volume=…` answer "what exists and who uses it".
- Images with `VOLUME` create an anonymous volume for every container started without a mount for that path.
- After `docker rm`, anonymous volumes stay behind as dangling volumes: that is where "disappeared" data usually is.
- Use named volumes for everything you care about; prune dangling ones regularly.

## Cleanup

<!-- test -->
```bash
docker volume rm orders journal-data > /dev/null
docker volume prune -f > /dev/null
docker image rm -f journal:1.0 > /dev/null
```

Next: [Lesson 057 · Volumes vs bind mounts](../057-volumes-vs-bind-mounts/README.md)
