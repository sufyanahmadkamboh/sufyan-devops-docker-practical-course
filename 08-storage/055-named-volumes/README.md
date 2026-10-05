# Lesson 055 · Named volumes

> Level 9 · Storage · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

A **named volume** is storage that Docker creates and manages, independent of any container. You refer to it by name
(`-v app-data:/data`), several containers can use it, and it survives when containers are removed. Volumes are the
default choice for data that an application owns: databases, uploads, queues. Docker never deletes a volume on its
own; you remove it explicitly, once no container uses it.

## Visual

```text
   container "writer" ─┐                                ┌─ container "reader"
   -v app-data:/data   │     ┌──────────────────────┐   │  -v app-data:/data
                       └───▶ │ volume "app-data"    │ ◀─┘
                             │ managed by Docker    │      docker rm writer reader
                             │ /var/lib/docker/     │      → the volume and its data stay
                             │   volumes/app-data   │
                             └──────────────────────┘
   docker volume create · ls · inspect · rm · prune
```

## Lab setup

No files are needed.

## Demonstration

Create a volume and write to it from one container:

<!-- test: contains=app-data; output -->
```bash
docker volume create app-data
docker run --rm -v app-data:/data alpine:3.23 sh -c 'echo "order 1001: 2 coffees" > /data/orders.txt'
```

```text
app-data
```

The writing container is gone (`--rm`). A different container, from a different image, reads the data:

<!-- test: contains=order 1001; output -->
```bash
docker run --rm -v app-data:/data busybox:1.37 cat /data/orders.txt
```

```text
order 1001: 2 coffees
```

Two running containers can share a volume at the same time:

<!-- test: contains=order 1002; output -->
```bash
docker run -d --name writer -v app-data:/data alpine:3.23 sh -c 'echo "order 1002: 1 tea" >> /data/orders.txt; sleep 300' > /dev/null
sleep 1
docker run --rm -v app-data:/data:ro busybox:1.37 cat /data/orders.txt
```

```text
order 1001: 2 coffees
order 1002: 1 tea
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker volume create NAME` | create an empty volume (`docker run -v NAME:…` also creates it if missing) |
| `-v NAME:/path[:ro]` | mount the volume at `/path` |
| `--mount type=volume,source=NAME,target=/path` | the explicit form |
| `docker volume ls` | list volumes |
| `docker volume rm NAME` | delete a volume and its data (only when no container uses it) |

## Hands-on lab

**Instructions.** List your volumes, then list every container (running or stopped) that uses `app-data`.

**Expected result.** `app-data` in the list; `writer` as its user.

**Verification.**

<!-- test: contains=app-data; contains=writer -->
```bash
docker volume ls --filter name=app-data
docker ps -a --filter volume=app-data --format '{{.Names}} ({{.Status}})'
```

## Break it

Delete the volume to "start fresh":

<!-- test: fail; contains=volume is in use; output -->
```bash
docker volume rm app-data 2>&1
```

```text
Error response from daemon: remove app-data: volume is in use - [c7384d8caa0fb7e6c44c4e013e5142c13d628d21535f8ed2d71a7f86a724c055]
```

## Troubleshoot it

`volume is in use - [ID]`: Docker refuses to delete a volume that a container (running **or stopped**) references; the
ID in brackets is that container. Find it by name:

<!-- test: contains=writer; output -->
```bash
docker ps -a --filter volume=app-data --format '{{.ID}} {{.Names}} {{.Status}}'
```

```text
c7384d8caa0f writer Up 2 seconds
```

This protection is deliberate: removing a database's volume by accident is how data is lost.

## Fix it

Decide first whether the data may really go. If yes, remove the container, then the volume:

<!-- test: contains=volume removed; output -->
```bash
docker rm -f writer > /dev/null
docker volume rm app-data > /dev/null && echo "volume removed"
```

```text
volume removed
```

`docker rm -v CONTAINER` removes a container together with its **anonymous** volumes; named volumes always need an
explicit `docker volume rm`.

## Practice challenge

Back up a volume: create a volume `menu` with a file in it, then write its contents into a `menu.tar` archive in a lab
folder on your computer, using a temporary container that mounts both the volume and the folder.

<details>
<summary>Solution</summary>

<!-- test: contains=menu.txt; output -->
```bash
mkdir -p ~/docker-practice/lesson-055 && cd ~/docker-practice/lesson-055
docker run --rm -v menu:/data alpine:3.23 sh -c 'echo "espresso 2.50" > /data/menu.txt'
docker run --rm -v menu:/data:ro -v "$(pwd):/backup" alpine:3.23 tar -cf /backup/menu.tar -C /data .
tar -tf menu.tar
```

```text
./
./menu.txt
```

The same pattern restores it (`tar -xf /backup/menu.tar -C /data` into a new volume). Lesson 058 backs up a real
database.

</details>

## Real-world example

A team runs a self-hosted Git server in a container with a volume `git-data`. Upgrading means stopping the container,
starting the new image version with the same volume, and checking the logs: the repositories are untouched, because
they never lived in the container. A nightly job backs up the volume with the temporary-container pattern from the
challenge.

## Recap

- Named volumes are managed by Docker, independent of containers, and survive `docker rm`.
- Several containers can mount the same volume (use `:ro` for readers).
- A volume in use by any container, even a stopped one, cannot be deleted: `docker ps -a --filter volume=NAME`.
- Back up a volume with a temporary container that mounts it and a host folder.

## Cleanup

<!-- test -->
```bash
docker volume rm menu > /dev/null
rm -rf ~/docker-practice/lesson-055
```

Next: [Lesson 056 · Inspecting volumes](../056-inspecting-volumes/README.md)
