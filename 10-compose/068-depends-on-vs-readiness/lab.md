<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 068 · depends_on vs readiness · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start the whole stack (both services) with `docker compose up -d`, wait a few seconds, and look at
the state and exit code of `migrate`.

**Expected result.** `migrate` has `exited` with a non-zero code (2): it ran before the database was ready.

**Verification.**

```bash
cd ~/docker-practice/lesson-068
docker compose up -d 2> /dev/null
sleep 5
docker compose ps -a --format '{{.Service}}: {{.Status}}'
```
