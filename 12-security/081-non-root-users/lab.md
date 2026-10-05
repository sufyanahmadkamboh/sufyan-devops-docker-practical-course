<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 081 · Running as a non-root user · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Run the `alpine:3.23` image as user ID 65534 (`nobody`) with `--user 65534:65534` and show its
identity, then try to write to `/root`.

**Expected result.** `uid=65534(nobody)` and `Permission denied` for `/root`.

**Verification.**

```bash
docker run --rm --user 65534:65534 alpine:3.23 sh -c 'id; touch /root/test 2>&1 || true'
```
