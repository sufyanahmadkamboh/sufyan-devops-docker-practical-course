<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 053 · The container's writable layer · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Run `nginx:1.30-alpine` in the background for a few seconds and list what nginx itself changed in
its writable layer while starting.

**Expected result.** Some lines starting with `C` or `A` (for example cache directories and the PID file under
`/run` or `/var/cache/nginx`).

**Verification.**

```bash
docker run -d --name web nginx:1.30-alpine > /dev/null
sleep 2
docker diff web
```
