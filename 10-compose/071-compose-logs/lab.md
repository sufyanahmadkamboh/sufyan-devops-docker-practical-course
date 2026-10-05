<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 071 · Logs · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Find every request to `/visits` in the API's logs, and count them.

**Expected result.** A number (1 or more, depending on how often you called it).

**Verification.**

```bash
cd ~/docker-practice/lesson-071
docker compose logs --no-log-prefix api | grep -c "GET /visits"
```
