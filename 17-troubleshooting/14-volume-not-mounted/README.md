# Troubleshooting problem 14 · Volume not mounted

> ⏱ 15 minutes · run every command from the course folder · related lessons: 054, 055, 056, 057

## Problem

The notes service was given a named volume "so the notes survive". After the container was recreated, the notes are
gone anyway, and the volume turns out to be empty.

## Symptoms

The service (a shell loop standing in for the application) appends to `/data/notes.txt`. The volume is mounted with
a typo in the target path:

<!-- test -->
```bash
docker run -d --name notes -v notes-data:/dat alpine:3.23 \
  sh -c 'mkdir -p /data && echo "buy coffee beans" >> /data/notes.txt && sleep 3600' > /dev/null
```

<!-- test: contains=buy coffee beans; output -->
```bash
sleep 1
docker exec notes cat /data/notes.txt
```

```text
buy coffee beans
```

A routine update recreates the container:

<!-- test: fail; contains=No such file; output -->
```bash
docker rm -f notes > /dev/null
docker run -d --name notes -v notes-data:/dat alpine:3.23 sleep 3600 > /dev/null
docker exec notes cat /data/notes.txt 2>&1
```

```text
cat: can't open '/data/notes.txt': No such file or directory
```

## Investigation

**1. Where is the volume mounted?**

<!-- test: contains=/dat; output -->
```bash
docker inspect --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{println}}{{end}}' notes
```

```text
volume notes-data -> /dat
```

**2. What is in the volume?**

<!-- test: contains=files in the volume: 0; output -->
```bash
echo "files in the volume: $(docker run --rm -v notes-data:/volume alpine:3.23 find /volume -type f | wc -l)"
```

```text
files in the volume: 0
```

**3. Where does the application write?**

<!-- test: absent=/data; output -->
```bash
docker exec notes sh -c 'mount | grep " /da" || true'
```

```text
/dev/sdd on /dat type ext4 (rw,relatime)
```

The mount list shows `/dat`; nothing is mounted at `/data`, so `/data` lived in the container's writable layer and was
deleted with the container (lesson 053).

## Commands

| Command | What it tells you |
|---|---|
| `docker inspect --format '{{range .Mounts}}…{{end}}' NAME` | every mount: type, source volume or path, destination |
| `docker run --rm -v VOL:/volume alpine:3.23 ls -la /volume` | what a volume really contains |
| `docker volume inspect VOL` | when it was created, where the engine stores it (lesson 056) |
| `docker exec NAME mount` | the mounts as the process sees them |

## Output interpretation

Docker accepts any absolute target path: `-v notes-data:/dat` is valid, it simply mounts at a path the app never uses.
No error, no warning. The volume stays empty (0 files) and the data is written next to it, into the writable layer.

Bind mounts have their own trap: with `-v`, a missing host folder is created as an empty directory (on Linux),
so a typo in the **source** path also starts the container with nothing in it. `--mount type=bind` is stricter and
refuses a missing source on Linux engines. Check the `Source` field of `docker inspect` for bind mounts.

## Root cause

A typo in the mount target (`/dat` instead of `/data`): the volume and the application's data directory never met.

## Fix

<!-- test -->
```bash
docker rm -f notes > /dev/null
docker run -d --name notes --mount type=volume,source=notes-data,target=/data alpine:3.23 \
  sh -c 'echo "buy coffee beans" >> /data/notes.txt && sleep 3600' > /dev/null
```

## Verification

Recreate the container: the note must survive.

<!-- test: contains=buy coffee beans; contains=/data; output -->
```bash
sleep 1
docker rm -f notes > /dev/null
docker run -d --name notes --mount type=volume,source=notes-data,target=/data alpine:3.23 sleep 3600 > /dev/null
docker exec notes cat /data/notes.txt
docker inspect --format '{{range .Mounts}}{{.Name}} -> {{.Destination}}{{end}}' notes
```

```text
buy coffee beans
notes-data -> /data
```

## Prevention

- Declare the data path once: `VOLUME /data` in the Dockerfile documents it, and Compose files reference the same path
  (lesson 066).
- Prefer `--mount` (explicit keys, errors on missing bind sources) over `-v` in scripts.
- After the first deployment, run the "recreate and check" test above: it is the only proof that data persists.

## Cleanup

<!-- test -->
```bash
docker rm -f notes > /dev/null
docker volume rm notes-data > /dev/null
```

Next: [Problem 15 · Data disappeared](../15-data-disappeared/README.md)
