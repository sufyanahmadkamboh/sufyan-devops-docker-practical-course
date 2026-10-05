<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 010 · Container names · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Try to name a container `my web`. What does Docker say? Then find the valid name rule in the error and start
a container named `web.v2_blue-1`.

## Solution

```bash
docker run -d --name "my web" nginx:1.30-alpine 2>&1 | head -1
docker run -d --name web.v2_blue-1 nginx:1.30-alpine > /dev/null
docker ps --filter name=web.v2 --format '{{.Names}}'
```

```text
docker: Error response from daemon: Invalid container name (my web), only [a-zA-Z0-9][a-zA-Z0-9_.-] are allowed
web.v2_blue-1
```

Names may contain letters, digits, `_`, `.` and `-`, and must start with a letter or digit (`[a-zA-Z0-9][a-zA-Z0-9_.-]`).
