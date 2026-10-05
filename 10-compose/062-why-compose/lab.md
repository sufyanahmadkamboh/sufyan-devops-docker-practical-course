<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 062 · Why Docker Compose? · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** List the project's containers with `docker compose ps`, and the network Compose created.

**Expected result.** Two services, `api` and `redis`, both running, and a network `lesson-062_default`.

**Verification.**

```bash
cd ~/docker-practice/lesson-062
docker compose ps --format '{{.Service}}: {{.State}}'
docker network ls --filter name=lesson-062 --format '{{.Name}}'
```
