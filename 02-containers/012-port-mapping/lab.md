<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 012 · Port mapping · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start `redis:8-alpine` named `cache` and publish its port 6379 on the host port 6380, on the loopback
interface only. Then check the mapping.

**Expected result.** `6379/tcp -> 127.0.0.1:6380`.

**Verification.**

<!-- test: contains=6379/tcp -> 127.0.0.1:6380 -->
```bash
docker run -d --name cache -p 127.0.0.1:6380:6379 redis:8-alpine > /dev/null
docker port cache
```
