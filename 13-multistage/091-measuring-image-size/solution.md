<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 091 · Measuring image size · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write a small size report: for `ts-single:1.0`, `ts-copyall:1.0` and `ts-multi:1.0`, print the content size in MB
(from `docker image inspect`) and how many MB larger than `node:24-alpine` each one is.

## Solution

```bash
base=$(docker image inspect --format '{{.Size}}' node:24-alpine)
for image in ts-single:1.0 ts-copyall:1.0 ts-multi:1.0; do
  size=$(docker image inspect --format '{{.Size}}' "$image")
  echo "$image  $((size / 1000000)) MB content, +$(((size - base) / 1000000)) MB over the base image"
done
```

```text
ts-single:1.0  72 MB content, +10 MB over the base image
ts-copyall:1.0  66 MB content, +4 MB over the base image
ts-multi:1.0  62 MB content, +0 MB over the base image
```

Integer division rounds down; the point is the comparison. Comparing against the base image isolates what your
Dockerfile adds, which is the part you control. A CI job can fail a build when that number grows unexpectedly.
