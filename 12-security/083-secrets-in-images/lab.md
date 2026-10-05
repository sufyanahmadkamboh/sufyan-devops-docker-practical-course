<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 083 · Secrets in images · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Find the layer created by `COPY credentials.txt` in the leaky image's history and note its size.

**Expected result.** A layer created by `COPY credentials.txt /tmp/credentials.txt` with a non-zero size; the
following `RUN … rm` layer does not make the image smaller.

**Verification.**

```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' cafe-secrets:leaky | head -4
```
