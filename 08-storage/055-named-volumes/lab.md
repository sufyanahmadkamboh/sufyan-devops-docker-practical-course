<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 055 · Named volumes · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** List your volumes, then list every container (running or stopped) that uses `app-data`.

**Expected result.** `app-data` in the list; `writer` as its user.

**Verification.**

```bash
docker volume ls --filter name=app-data
docker ps -a --filter volume=app-data --format '{{.Names}} ({{.Status}})'
```
