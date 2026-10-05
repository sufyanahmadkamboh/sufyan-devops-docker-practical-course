<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 092 · HEALTHCHECK · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Build the image in `fixed/`, start it, and wait until it is healthy. Then list only healthy
containers with a filter.

**Expected result.** The container appears with `(healthy)` in its status.

**Verification.**

```bash
docker build -q -t cafe-web:health fixed > /dev/null
docker run -d --name web-fixed -p 8081:80 cafe-web:health > /dev/null && echo "started web-fixed"
```

```bash
docker ps --filter health=healthy --filter name=web-fixed --format '{{.Names}}: {{.Status}}'
```
