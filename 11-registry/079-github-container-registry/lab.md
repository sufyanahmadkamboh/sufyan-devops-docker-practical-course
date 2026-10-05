<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 079 · GitHub Container Registry · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Add the label `org.opencontainers.image.version` with the value `1.0` at build time, without editing
the Dockerfile (`docker build --label`), and read it back.

**Expected result.** `1.0`.

**Verification.**

```bash
cd ~/docker-practice/lesson-079
docker build -q --label org.opencontainers.image.version=1.0 -t ghcr.io/cafe-team-example/cafe-api:1.0 . > /dev/null
docker image inspect ghcr.io/cafe-team-example/cafe-api:1.0 --format '{{index .Config.Labels "org.opencontainers.image.version"}}'
```
