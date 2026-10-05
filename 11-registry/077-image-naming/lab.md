<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 077 · Image naming · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Add the tag `sha-3f1a2b4` (a short Git commit, as CI pipelines do) to the same image, push it, and list
the repository's tags.

**Expected result.** Four tags: `1`, `1.4`, `1.4.2`, `sha-3f1a2b4`.

**Verification.**

```bash
docker tag localhost:5000/cafe-team/cafe-api:1.4.2 localhost:5000/cafe-team/cafe-api:sha-3f1a2b4
docker push -q localhost:5000/cafe-team/cafe-api:sha-3f1a2b4
curl -s localhost:5000/v2/cafe-team/cafe-api/tags/list
```
