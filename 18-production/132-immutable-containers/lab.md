<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 132 · Immutable containers · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show which image the running container was started from, and its image ID.

**Expected result.** `site:1.0` and a `sha256:` ID: the exact version that is running.

**Verification.**

```bash
docker inspect site --format '{{.Config.Image}} {{.Image}}'
```
