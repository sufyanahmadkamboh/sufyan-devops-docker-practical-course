<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 014 · Container logs · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

A container crashes on start. Without running anything inside it, find out why from its log, and show the exit code.

```bash
docker run -d --name crasher alpine:3.23 sh -c 'echo "loading config /etc/app/config.yml"; cat /etc/app/config.yml'
```

The solution is in [solution.md](solution.md).
