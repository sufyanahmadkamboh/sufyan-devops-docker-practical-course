<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 018 · Pulling images · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Show that `alpine:3.23`, `docker.io/library/alpine:3.23` and `alpine@sha256:…` (its digest) are three names for the
same image, without contacting any registry.

## Solution

```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23)
for name in alpine:3.23 docker.io/library/alpine:3.23 "$digest"; do
  docker image inspect --format '{{.Id}}' "$name"
done | sort -u | wc -l | grep -q '^ *1$' && echo "one ID: the same image"
```

```text
one ID: the same image
```

`docker image inspect` only reads the local image store. The short name and the full name are the same reference; the
digest names the content.
