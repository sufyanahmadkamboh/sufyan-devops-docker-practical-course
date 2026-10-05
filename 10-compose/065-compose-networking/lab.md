<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 065 · Networking in Compose · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Find the IP addresses of the `api` container: it has one per network.

**Expected result.** Two addresses, one on `lesson-065_backend`, one on `lesson-065_frontend`.

**Verification.**

```bash
docker inspect lesson-065-api-1 --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{$net.IPAddress}}{{"\n"}}{{end}}'
```
