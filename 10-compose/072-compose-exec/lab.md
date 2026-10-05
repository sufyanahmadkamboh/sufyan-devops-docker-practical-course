<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 072 · exec and run · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Use `exec` and Redis's own client to read the `visits` key directly from Redis.

**Expected result.** The number of visits so far (at least `1`).

**Verification.**

```bash
cd ~/docker-practice/lesson-072
docker compose exec redis redis-cli GET visits
```
