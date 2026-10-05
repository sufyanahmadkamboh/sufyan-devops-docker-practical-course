<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 084 · Read-only file systems · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start an nginx container normally, request its page once, and use `docker diff` to list the files
and folders nginx changed in the container's writable layer. These are the places a read-only nginx will need.

**Expected result.** Entries under `/var/cache/nginx` and `/run` (plus configuration files the entrypoint script
adjusts in `/etc/nginx`).

**Verification.**

```bash
docker run -d --name web-rw nginx:1.30-alpine > /dev/null
sleep 2
docker diff web-rw
docker rm -f web-rw > /dev/null
```
