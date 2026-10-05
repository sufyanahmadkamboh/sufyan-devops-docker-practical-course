# Lesson 057 · Volumes vs bind mounts

> Level 9 · Storage · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Both put data outside the container's writable layer, but they serve different owners. A **bind mount** is a host
path that **you** manage: ideal for source code during development and for configuration files. A **named volume** is
storage that **Docker** manages: ideal for application data, portable between hosts, independent of the host's folder
layout, and pre-filled from the image when it is empty. A third type, **tmpfs**, lives only in memory. The visible
difference that surprises people: an empty volume is filled with the image's files, an empty bind mount hides them.

## Visual

```text
                         bind mount                      named volume                 tmpfs
 source                  a host path you choose          managed by Docker            memory
 managed with            your file manager, git          docker volume …              nothing (gone at stop)
 empty at first mount    hides the image's files         filled with the image's      empty
                                                         files (copy-up)
 performance (Desktop)   slower (crosses into the VM)    fast (inside the VM)         fastest
 typical use             code in development, config     databases, uploads, caches   secrets, scratch files
 example                 -v "$(pwd)/src:/app/src"        -v pgdata:/var/lib/postgresql  --tmpfs /tmp
```

## Lab setup

An empty folder on the host:

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-057
cd ~/docker-practice/lesson-057
mkdir empty-folder
```

## Demonstration

Mount an **empty named volume** over nginx's web root. Docker copies the image's files into it first:

<!-- test: contains=Welcome to nginx; output; retry=5 -->
```bash
docker run -d --name with-volume -p 8080:80 -v web-root:/usr/share/nginx/html nginx:1.30-alpine > /dev/null
curl -s http://localhost:8080 | grep -o '<title>.*</title>'
docker run --rm -v web-root:/data alpine:3.23 ls /data
```

```text
<title>Welcome to nginx!</title>
50x.html
index.html
```

The image's `index.html` and `50x.html` are now in the volume, where they stay even if the image changes.

## Command breakdown

| Form | Type |
|---|---|
| `-v NAME:/path` | named volume (created if missing, pre-filled from the image when empty) |
| `-v /abs/path:/path` or `-v "$(pwd)/dir:/path"` | bind mount (never pre-filled) |
| `--tmpfs /path` or `--mount type=tmpfs,target=/path,tmpfs-size=64m` | in-memory file system |
| `--mount type=volume,source=NAME,target=/path,volume-nocopy` | a volume without the copy-up |

## Hands-on lab

**Instructions.** Use `docker inspect` to show the type of the mount of `with-volume`, and the folder of the host or
engine where its data lives.

**Expected result.** `volume`, and a `Source` under Docker's data directory (`/var/lib/docker/volumes/web-root/_data`).

**Verification.**

<!-- test: contains=volume; contains=web-root -->
```bash
docker inspect with-volume --format '{{range .Mounts}}{{.Type}} {{.Source}}{{end}}'
```

## Break it

Now mount the **empty host folder** at the same place:

<!-- test: contains=403; output; retry=5 -->
```bash
docker run -d --name with-bind -p 8081:80 -v "$(pwd)/empty-folder:/usr/share/nginx/html" nginx:1.30-alpine > /dev/null
sleep 1
curl -s -w '\nHTTP %{http_code}\n' http://localhost:8081 | tail -1
```

```text
HTTP 403
```

## Troubleshoot it

`HTTP 403 Forbidden`: nginx runs, but has no `index.html` to serve and directory listing is off. Look at the folder
from inside the container, and at nginx's log:

<!-- test: contains=directory index; output -->
```bash
echo "files: [$(docker exec with-bind ls /usr/share/nginx/html)]"
docker logs with-bind 2>&1 | grep -m1 'directory index'
```

```text
files: []
2026/10/05 10:52:46 [error] 32#32: *1 directory index of "/usr/share/nginx/html/" is forbidden, client: 172.17.0.1, server: localhost, request: "GET / HTTP/1.1", host: "localhost:8081"
```

The folder is empty: a bind mount shows exactly the host folder and **hides** the image's files at that path. Docker
never copies anything into a bind mount.

## Fix it

With a bind mount, the host must provide the content:

<!-- test: contains=HTTP 200; output; retry=5 -->
```bash
echo '<h1>Served from the host</h1>' > empty-folder/index.html
curl -s -w '\nHTTP %{http_code}\n' http://localhost:8081 | tail -1
```

```text
HTTP 200
```

Rule of thumb: use a bind mount when the host owns the files (you edit them), a named volume when the application
owns them (it writes them).

## Practice challenge

Give a container a 16 MB in-memory scratch directory at `/scratch`, prove that it is a `tmpfs`, and show that its
content is gone after a restart.

<details>
<summary>Solution</summary>

<!-- test: contains=tmpfs; contains=after restart: []; output -->
```bash
docker run -d --name scratch --mount type=tmpfs,target=/scratch,tmpfs-size=16m alpine:3.23 sleep 300 > /dev/null
docker exec scratch sh -c 'grep " /scratch " /proc/mounts; echo temp > /scratch/file.txt'
docker restart scratch > /dev/null
echo "after restart: [$(docker exec scratch ls /scratch)]"
```

```text
tmpfs /scratch tmpfs rw,nosuid,nodev,noexec,relatime,size=16384k 0 0
after restart: []
```

tmpfs data never touches the disk, which also makes it a good place for decrypted secrets and temporary files.

</details>

## Real-world example

A team's development setup bind-mounts `./src` into the API container (hot reload of the code the developers edit)
and uses a named volume `pgdata` for the database (the data belongs to Postgres, and is fast on Docker Desktop). In
production, the code is baked into the image, Postgres keeps its named volume, and a `--tmpfs /tmp` gives the
read-only API container a writable scratch space (lesson 084).

## Recap

- Bind mount: a host path you manage; hides the image's files; best for code in development and config files.
- Named volume: managed by Docker; pre-filled from the image when empty; best for application data.
- tmpfs: in memory only, gone when the container stops; for scratch files and secrets.
- `docker inspect … .Mounts` shows which type a container really got.

## Cleanup

<!-- test -->
```bash
docker rm -f with-volume with-bind scratch > /dev/null
docker volume rm web-root > /dev/null
rm -rf ~/docker-practice/lesson-057
```

Next: [Lesson 058 · A persistent database](../058-persistent-database/README.md)
