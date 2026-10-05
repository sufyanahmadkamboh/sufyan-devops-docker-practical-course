<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 086 · Resource limits for security · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Show that the open-file limit works: in a container with `--ulimit nofile=20:20`, open files until the kernel refuses,
and report how many could be opened.

## Solution

```bash
docker run --rm --ulimit nofile=20:20 python:3.14-alpine python -c '
files = []
try:
    while True:
        files.append(open("/dev/null"))
except OSError as error:
    print(f"opened {len(files)} files, then: {error}")'
```

```text
opened 17 files, then: [Errno 24] No file descriptors available: '/dev/null'
```

With a limit of 20, descriptors 0–19 exist; standard input, output and error already use three of them. A service that
leaks connections or file handles hits the same wall, inside its own container only. Error 24 (`EMFILE`) reads
`No file descriptors available` with Alpine's C library (musl) and `Too many open files` with glibc (Debian, Ubuntu).
