<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 054 · Bind mounts · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Prove that the mount is read-only: try to create a file in `/usr/share/nginx/html` from inside the
container.

**Expected result.** `Read-only file system`.

**Verification.**

```bash
docker exec site sh -c 'touch /usr/share/nginx/html/hacked.html' 2>&1 || true
```
