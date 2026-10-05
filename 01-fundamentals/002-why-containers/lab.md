<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 002 · Why containers? · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Check which Flask version is inside the image, and which (if any) is on your own computer.

**Expected result.** `3.1.3` in the image, whatever is (or is not) installed locally.

**Verification.**

```bash
cd ~/docker-practice/lesson-002
docker run --rm cafe-api:1.0 pip show flask | grep Version
```
