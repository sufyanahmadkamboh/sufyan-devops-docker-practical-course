<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 051 · EXPOSE vs publishing ports · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Publish one container on **two** host ports: 8082 for everyone and 8083 for this computer only, both to port 80.

## Solution

```bash
docker run -d --name two-ports -p 8082:80 -p 127.0.0.1:8083:80 nginx:1.30-alpine > /dev/null
docker port two-ports
```

```text
80/tcp -> 0.0.0.0:8082
80/tcp -> 127.0.0.1:8083
80/tcp -> [::]:8082
```

`-p` can be repeated; each one is a separate forwarding rule.
