<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 057 · Volumes vs bind mounts · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Use `docker inspect` to show the type of the mount of `with-volume`, and the folder of the host or
engine where its data lives.

**Expected result.** `volume`, and a `Source` under Docker's data directory (`/var/lib/docker/volumes/web-root/_data`).

**Verification.**

```bash
docker inspect with-volume --format '{{range .Mounts}}{{.Type}} {{.Source}}{{end}}'
```
