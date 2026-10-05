<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 052 · Network troubleshooting · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Run steps 1 and 2 of the checklist for `app`: show that it is running and that its port is
published.

**Expected result.** `Up …`, and `8000/tcp -> 0.0.0.0:8080`.

**Verification.**

```bash
docker ps --filter name=app --format '{{.Status}}'
docker port app
```
