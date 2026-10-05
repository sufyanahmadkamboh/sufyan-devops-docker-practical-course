<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 101 · Labels · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** List only the containers that belong to the `staging` environment, with their team.

**Expected result.** `pay-web payments` and `shop-web shop`.

**Verification.**

```bash
docker ps --filter label=env=staging --format '{{.Names}} {{.Label "team"}}'
```
