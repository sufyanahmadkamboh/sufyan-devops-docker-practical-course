<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 001 · What is Docker? · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Show that two containers from the same image are isolated from each other: create a file in one container, then look for
it in a second container started from the same image.

## Solution

```bash
docker run --rm alpine:3.23 sh -c 'echo hello > /tmp/note.txt && cat /tmp/note.txt'
docker run --rm alpine:3.23 cat /tmp/note.txt 2>&1 || true
```

```text
hello
cat: can't open '/tmp/note.txt': No such file or directory
```

The second container starts from the image again, not from the first container: the file does not exist there.
