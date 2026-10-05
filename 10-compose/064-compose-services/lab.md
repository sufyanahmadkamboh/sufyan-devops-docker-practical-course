<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 064 · Services · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Stop the `redis` service with `docker compose stop redis`, wait a few seconds, and check whether its
restart policy brought it back.

**Expected result.** It stays `exited`: `unless-stopped` never restarts a container you stopped yourself. Start it
again with `docker compose start redis`.

**Verification.**

```bash
cd ~/docker-practice/lesson-064
docker compose stop redis 2> /dev/null; sleep 3
docker inspect lesson-064-redis-1 --format '{{.State.Status}}'
docker compose start redis 2> /dev/null
docker inspect lesson-064-redis-1 --format '{{.State.Status}}'
```
