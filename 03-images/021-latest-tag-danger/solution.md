<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 021 · The danger of the latest tag · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Your Dockerfile starts with `FROM python`. Without pulling anything, find out which of your local Python images that
line would *not* use, and rewrite the line so that it uses the slim 3.14 image you tested.

## Solution

```bash
docker image ls --format '{{.Repository}}:{{.Tag}}' python
docker image inspect python:latest > /dev/null 2>&1 || echo "python:latest is not local: FROM python would pull it"
echo "FROM python" | sed 's/^FROM python$/FROM python:3.14-slim/'
```

```text
python:3.14-slim
python:3.14-alpine
python:latest is not local: FROM python would pull it
FROM python:3.14-slim
```

`FROM python` means `python:latest`: neither local image. It would pull whatever `latest` is today (a full Debian image
with the newest Python), so the next build silently changes Python version and image size.
