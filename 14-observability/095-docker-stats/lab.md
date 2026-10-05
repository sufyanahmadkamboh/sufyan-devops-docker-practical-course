<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 095 · docker stats · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Print one snapshot with only the name and memory percentage of every running container, sorted by
memory percentage, highest first.

**Expected result.** Two lines, `cache` and `web`, each with a percentage.

**Verification.**

```bash
docker stats --no-stream --format '{{.MemPerc}} {{.Name}}' | sort -rn
```
