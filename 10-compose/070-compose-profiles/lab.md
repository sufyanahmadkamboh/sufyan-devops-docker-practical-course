<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 070 · Profiles · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Use the `tools` container to look up the address of `redis` on the project network.

**Expected result.** An IP address followed by the name `redis`.

**Verification.**

```bash
cd ~/docker-practice/lesson-070
docker compose exec tools getent hosts redis
```
