<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 019 · Listing and removing images · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Remove `cafe-site:1.0` and verify that `cafe-site:1.1` is still there.

**Expected result.** `Untagged: cafe-site:1.0` and `Deleted: sha256:…`; the list shows only version 1.1.

**Verification.**

```bash
docker image rm cafe-site:1.0
docker image ls --format '{{.Repository}}:{{.Tag}}' cafe-site
```
