<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 009 · Container lifecycle · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Remove a container that is still running:

```bash
docker rm web
```

```text
Error response from daemon: cannot remove container "web": container is running: stop the container before removing or force remove
```

## Troubleshoot it

`cannot remove container "web": container is running: stop the container before removing or force remove`. Docker
protects running containers from an accidental `rm`. Confirm the state:

```bash
. ~/docker-practice-state.sh
state web
```

## Fix it

Stop it cleanly, then remove it (or, when you do not care about a clean shutdown, `docker rm -f web`):

```bash
docker stop web
docker rm web
```
