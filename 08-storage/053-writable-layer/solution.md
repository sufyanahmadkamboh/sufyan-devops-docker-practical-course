<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 053 · The container's writable layer · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Show the three kinds of changes `docker diff` reports: in one container, add a file, change an existing file, and
delete an existing file. Then list them.

## Solution

```bash
docker run --name changes alpine:3.23 sh -c 'echo new > /tmp/new.txt; echo changed >> /etc/motd; rm /etc/issue'
docker diff changes | grep -E 'new.txt|motd|issue'
docker rm changes > /dev/null
```

```text
C /etc/motd
D /etc/issue
A /tmp/new.txt
```

Deleting a file of the image does not shrink anything: the image layer still contains it, and the writable layer only
records a "deleted" marker (a whiteout). The same is true for layers in a Dockerfile (lesson 038).
