# Lesson 053 · The container's writable layer

> Level 9 · Storage · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

An image is read-only. When a container starts, Docker adds a thin **writable layer** on top of the image's layers:
every file the container creates, changes or deletes is recorded there (copy-on-write). That layer belongs to the
container: it survives a stop and a restart, and it is **deleted with the container**. Anything that must outlive a
container (uploads, databases, logs you want to keep) belongs in a volume or a bind mount (lessons 054–058).

## Visual

```text
   container "notes"                       container "notes-2" (same image)
 ┌─────────────────────────────┐         ┌─────────────────────────────┐
 │ writable layer  (A /data/x) │         │ writable layer  (empty)     │   ← one per container
 ├─────────────────────────────┤         ├─────────────────────────────┤
 │ image layers (read-only)    │ shared  │ image layers (read-only)    │
 │ alpine:3.23                 │◀───────▶│ alpine:3.23                 │
 └─────────────────────────────┘         └─────────────────────────────┘

  docker stop / start  → writable layer kept         docker rm → writable layer deleted
  docker diff C        → what changed: A added, C changed, D deleted
```

## Lab setup

No files are needed.

## Demonstration

Create a container that writes a file into its writable layer:

<!-- test: contains=notes: 1; output -->
```bash
docker run --name notes alpine:3.23 sh -c 'mkdir -p /data && echo "a note" >> /data/notes.txt && echo "notes: $(wc -l < /data/notes.txt)"'
```

```text
notes: 1
```

The container has exited, but it still exists, and so does its writable layer. `docker diff` lists what the
container changed compared with its image:

<!-- test: contains=A /data/notes.txt; output -->
```bash
docker diff notes
```

```text
A /data
A /data/notes.txt
```

Start the same container again. It runs the same command, which appends one more line:

<!-- test: contains=notes: 2; output -->
```bash
docker start -a notes
```

```text
notes: 2
```

`notes: 2`: the line written by the first run was still there. Stopping and starting keeps the writable layer.

`docker container ls -s` shows the size of each container's writable layer, next to the size of its image (`virtual`):

<!-- test: contains=notes; output -->
```bash
docker container ls -a -s --filter name=notes --format '{{.Names}}: {{.Size}}'
```

```text
notes: 12.3kB (virtual 9.11MB)
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker diff C` | changes in C's writable layer: `A` added, `C` changed, `D` deleted |
| `docker start -a C` | start an existing (stopped) container again, attached |
| `docker container ls -s` | include the size of the writable layer |

## Hands-on lab

**Instructions.** Run `nginx:1.30-alpine` in the background for a few seconds and list what nginx itself changed in
its writable layer while starting.

**Expected result.** Some lines starting with `C` or `A` (for example cache directories and the PID file under
`/run` or `/var/cache/nginx`).

**Verification.**

<!-- test: contains=nginx; retry=5 -->
```bash
docker run -d --name web nginx:1.30-alpine > /dev/null
sleep 2
docker diff web
```

## Break it

Remove the container (as a cleanup job or a redeploy does), then start a "new version" from the same image and look
for the notes:

<!-- test: fail; contains=No such file; output -->
```bash
docker rm notes > /dev/null
docker run --rm alpine:3.23 cat /data/notes.txt 2>&1
```

```text
cat: can't open '/data/notes.txt': No such file or directory
```

## Troubleshoot it

`No such file or directory`: the new container starts from the image, which never contained `/data/notes.txt`. The
file only existed in the writable layer of `notes`, and `docker rm` deleted that layer. Confirm that no container
holds it any more:

<!-- test: contains=no container named notes; output -->
```bash
docker container ls -a --filter name=^notes$ --format '{{.Names}}' | grep -q . || echo "no container named notes"
```

```text
no container named notes
```

Every redeploy (new image version → new container) and every `docker run --rm` loses the writable layer. It is
temporary storage by design.

## Fix it

Store the data outside the container, in a **named volume** (lesson 055), so a new container sees it:

<!-- test: contains=a note; output -->
```bash
docker run --rm -v notes-data:/data alpine:3.23 sh -c 'echo "a note" >> /data/notes.txt'
docker run --rm -v notes-data:/data alpine:3.23 cat /data/notes.txt
```

```text
a note
```

Two containers, both removed at once (`--rm`), and the note survived: it lives in the volume `notes-data`.

## Practice challenge

Show the three kinds of changes `docker diff` reports: in one container, add a file, change an existing file, and
delete an existing file. Then list them.

<details>
<summary>Solution</summary>

<!-- test: contains=A /tmp/new.txt; contains=C /etc/motd; contains=D /etc/issue; output -->
```bash
docker run --name changes alpine:3.23 sh -c 'echo new > /tmp/new.txt; echo changed >> /etc/motd; rm /etc/issue'
docker diff changes | grep -E 'new.txt|motd|issue'
docker rm changes > /dev/null
```

```text
C /etc/motd
D /etc/issue
A /tmp/new.txt
```

Deleting a file of the image does not shrink anything: the image layer still contains it, and the writable layer only
records a "deleted" marker (a whiteout). The same is true for layers in a Dockerfile (lesson 038).

</details>

## Real-world example

A team runs a content management system in a container, and editors upload images. After a routine redeploy to a new
image version, every upload from the last month is gone: they were written to the container's writable layer. The fix
is a volume for the uploads directory, and a rule in their deployment checklist: every path the application writes to
is either a volume or explicitly temporary.

## Recap

- Each container has a writable layer on top of the read-only image layers (copy-on-write).
- It survives stop and start, and is deleted with the container: never keep important data there.
- `docker diff` shows what a container changed; `docker container ls -s` shows how much.
- Persistent data goes into volumes or bind mounts.

## Cleanup

<!-- test -->
```bash
docker rm -f web > /dev/null
docker volume rm notes-data > /dev/null
```

Next: [Lesson 054 · Bind mounts](../054-bind-mounts/README.md)
