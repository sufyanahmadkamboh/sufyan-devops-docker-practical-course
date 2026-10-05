<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 081 · Running as a non-root user · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Prove that the application in `cafe-web:fixed` cannot modify its own code: as the container's user, try to append a
line to `/app/app.py`. Then show the same command succeeds in `cafe-web:root`.

## Solution

```bash
docker exec web-fixed sh -c 'echo "# changed" >> /app/app.py' 2>&1 || true
docker exec web-root sh -c 'echo "# changed" >> /app/app.py && echo "root can change the code"'
```

```text
sh: can't create /app/app.py: Permission denied
root can change the code
```

In the root container, anyone who gets code execution can rewrite the application. In the fixed one, the code is
read-only for the process; only `data/` is writable.
