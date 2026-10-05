<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 010 · Container names · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a `redis:8-alpine` container in the background named `cache-1`, rename it to `session-cache`,
and print its name and the first 12 characters of its ID.

**Expected result.** `session-cache` followed by a 12-character ID.

**Verification.**

```bash
docker run -d --name cache-1 redis:8-alpine > /dev/null
docker rename cache-1 session-cache
docker ps --filter name=session-cache --format '{{.Names}} {{.ID}}'
```
