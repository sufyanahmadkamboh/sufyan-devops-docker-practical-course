<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 024 · WORKDIR · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write a Dockerfile that copies `menu.csv` into `/srv/cafe/menu/`, and whose container prints the number of lines of
the file with `wc -l menu.csv` (a relative path), using `WORKDIR` twice: `/srv/cafe`, then `menu`.

## Solution

```bash
cd ~/docker-practice/lesson-024
printf 'FROM alpine:3.23\nWORKDIR /srv/cafe\nWORKDIR menu\nCOPY menu.csv .\nCMD ["wc", "-l", "menu.csv"]\n' > Dockerfile.challenge
docker build -q -f Dockerfile.challenge -t menu:challenge . > /dev/null
docker run --rm menu:challenge
```

```text
4 menu.csv
```

The second, relative `WORKDIR` makes the working directory `/srv/cafe/menu`; `COPY … .` and the command both use it.
