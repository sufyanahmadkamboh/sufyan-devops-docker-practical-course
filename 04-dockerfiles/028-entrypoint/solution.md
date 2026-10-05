<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 028 · ENTRYPOINT · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Without changing the image, use `--entrypoint` to count the lines of `/app/menu.csv` with `wc -l`.

## Solution

```bash
docker run --rm --entrypoint wc price:1.0 -l /app/menu.csv
```

```text
4 /app/menu.csv
```

`--entrypoint` takes only the program name; its arguments come after the image name.
