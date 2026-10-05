<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 093 · Running is not healthy · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show both states of the `api` container side by side with one `docker inspect --format` command.

**Expected result.** `state=running health=healthy restarts=0`.

**Verification.**

```bash
docker inspect --format 'state={{.State.Status}} health={{.State.Health.Status}} restarts={{.RestartCount}}' api
```
