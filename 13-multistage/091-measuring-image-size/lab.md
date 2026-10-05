<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 091 · Measuring image size · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show how much disk all images, containers, volumes and the build cache use on your engine, and how
much of it is reclaimable.

**Expected result.** A table with the four types, their total size and the `RECLAIMABLE` column. Shared base layers
are counted once here, unlike in `docker image ls`.

**Verification.**

```bash
docker system df
```
