<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 008 · Listing containers · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Show only the containers that **failed**, i.e. exited with code 3, with their name and status. Then show the size of the
writable layer of every container.

## Solution

```bash
docker ps -a --filter exited=3 --format '{{.Names}}: {{.Status}}'
docker ps -a -s --format 'table {{.Names}}\t{{.Size}}'
```

```text
job-failed: Exited (3) 2 seconds ago
NAMES         SIZE
not-started   4.1kB (virtual 9.1MB)
job-failed    4.1kB (virtual 9.1MB)
job-ok        4.1kB (virtual 9.1MB)
web           81.9kB (virtual 66.8MB)
```

`exited=CODE` matches the exit code. `-s` adds the size of each container's writable layer (and, in brackets, the
"virtual" size including the image).
