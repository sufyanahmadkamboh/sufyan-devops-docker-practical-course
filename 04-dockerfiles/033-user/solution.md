<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 033 · USER · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Prove that in `orders:fixed` the application cannot change its own script, but can write its data.

## Solution

```bash
docker run --rm --entrypoint sh orders:fixed -c '
  (echo "# changed" >> /app/take-order.sh) 2>/dev/null && echo "script: changed" || echo "script: Permission denied"
  touch /app/data/test && echo "data: ok"'
```

```text
script: Permission denied
data: ok
```
