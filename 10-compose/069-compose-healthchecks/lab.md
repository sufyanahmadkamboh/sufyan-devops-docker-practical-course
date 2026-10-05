<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 069 · Healthchecks in Compose · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Watch Redis's healthcheck work: run its check command yourself, then read the output of the last check
Docker recorded.

**Expected result.** `PONG` both times.

**Verification.**

```bash
cd ~/docker-practice/lesson-069
docker compose exec redis redis-cli ping
docker inspect lesson-069-redis-1 --format '{{range .State.Health.Log}}{{.Output}}{{end}}' | tail -1
```
