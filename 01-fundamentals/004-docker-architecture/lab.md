<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 004 · Docker architecture · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Find which engine endpoint your client talks to, with `docker context ls` (the active context has a
`*`) and `docker context show`.

**Expected result.** One context marked active; its `DOCKER ENDPOINT` is a Unix socket (`unix:///var/run/docker.sock`)
on Linux or a named pipe (`npipe:////./pipe/…`) on Windows.

**Verification.**

```bash
docker context ls
docker context show
```
