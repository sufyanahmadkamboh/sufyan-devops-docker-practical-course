<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 014 · Container logs · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Using `docker logs` with `--tail` and `grep`, show how many requests to `/missing` Nginx answered
with status `404`.

**Expected result.** `1` (one request to `/missing`, from the Demonstration).

**Verification.**

```bash
docker logs web 2>/dev/null | grep '"GET /missing' | grep -c ' 404 '
```
