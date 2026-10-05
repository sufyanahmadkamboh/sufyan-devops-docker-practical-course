<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 038 · Build layers · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Using only `docker history`, find the single largest layer of `node:24-alpine` and the instruction that created it.

## Solution

```bash
docker history --no-trunc --format '{{.Size}}\t{{.CreatedBy}}' node:24-alpine | sort -h | tail -1 | cut -c1-90
```

```text
165MB	RUN /bin/sh -c addgroup -g 1000 node     && adduser -u 1000 -G node -s /bin/sh -D no
```

`sort -h` sorts human-readable sizes (kB, MB, GB). The biggest layer installs Node.js itself; it starts with
creating the `node` user, which is why the command shows `addgroup` first.
