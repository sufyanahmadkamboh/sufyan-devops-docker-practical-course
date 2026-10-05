<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 015 · Running commands in containers (exec) · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Open a Bash shell, as you would on a server:

```bash
docker exec web bash 2>&1
```

```text
OCI runtime exec failed: exec failed: unable to start container process: exec: "bash": executable file not found in $PATH
```

## Troubleshoot it

`exec: "bash": executable file not found in $PATH`: the container started, but the program does not exist **in the
image**. Small images (Alpine, distroless) do not include Bash. Check which shells the image has:

```bash
docker exec web cat /etc/shells
```

```text
# valid login shells
/bin/sh
/bin/ash
```

Other `exec` errors you will meet:

| Error | Cause |
|---|---|
| `container … is not running` | `exec` needs a running container: read its logs instead (lesson 014) |
| `No such container` | wrong name: check `docker ps` |
| `executable file not found` | the program is not in the image (no shell at all in distroless images: lesson 087) |

## Fix it

Use the shell the image has:

```bash
docker exec web sh -c 'echo "inside the container, as $(whoami), in $(pwd)"'
```
