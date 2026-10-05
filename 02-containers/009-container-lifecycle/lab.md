<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 009 · Container lifecycle · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start `redis:8-alpine` in the background with the name `cache`, stop it, and check its exit code.
Then start the same container again and remove it while it runs, in one command.

**Expected result.** Redis handles `SIGTERM` and saves its data, so it exits with code `0`. `docker rm -f` removes the
running container.

**Verification.**

```bash
. ~/docker-practice-state.sh
docker run -d --name cache redis:8-alpine > /dev/null
docker stop cache > /dev/null; state cache
docker start cache > /dev/null
docker rm -f cache > /dev/null && echo "cache removed"
```
