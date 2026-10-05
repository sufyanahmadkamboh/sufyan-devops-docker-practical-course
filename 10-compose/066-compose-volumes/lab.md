<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 066 · Volumes in Compose · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Find where the volume is mounted inside the Redis container, and list the files Redis keeps there.

**Expected result.** The mount destination is `/data`; it holds Redis's append-only files (`appendonlydir`).

**Verification.**

```bash
cd ~/docker-practice/lesson-066
docker inspect lesson-066-redis-1 --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{"\n"}}{{end}}'
docker compose exec redis ls /data
```
