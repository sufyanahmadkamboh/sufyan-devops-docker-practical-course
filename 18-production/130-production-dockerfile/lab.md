<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 130 · Production Dockerfile · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Prove that the production container cannot change its own application code, and that the
"before" container can.

**Expected result.** `Permission denied` for `api:final` (user `node`, files owned by root); no error for
`api:before` (root).

**Verification.**

```bash
docker run --rm api:final sh -c 'echo hacked >> /app/server.js' 2>&1 || true
docker run --rm api:before sh -c 'echo hacked >> /server.js && echo "before: changed"'
```
