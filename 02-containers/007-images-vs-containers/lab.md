<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 007 · Images vs containers · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a container named `deleter` from `alpine:3.23` that deletes `/etc/motd`. Then show, with
`docker container diff`, what changed, and prove that a fresh container from the same image still has `/etc/motd`.

**Expected result.** `D /etc/motd` in the diff, and the fresh container lists `/etc/motd`.

**Verification.**

```bash
docker run --name deleter alpine:3.23 rm /etc/motd
docker container diff deleter
docker run --rm alpine:3.23 ls /etc/motd
```
