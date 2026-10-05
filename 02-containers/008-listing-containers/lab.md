<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 008 · Listing containers · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** List the names and commands of all containers created from `alpine:3.23`, with the full commands not
shortened.

**Expected result.** `job-ok`, `job-failed` and `not-started`, with commands such as `"sh -c 'exit 3'"`.

**Verification.**

```bash
docker ps -a --filter ancestor=alpine:3.23 --no-trunc --format 'table {{.Names}}\t{{.Command}}'
```
