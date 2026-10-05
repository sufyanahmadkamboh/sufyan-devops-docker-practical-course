<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 101 · Labels · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Find every image on the engine that has an `org.opencontainers.image.version` label, and print its name with that
version.

## Solution

```bash
docker image ls --filter label=org.opencontainers.image.version --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>' |
  while read -r image; do
    echo "$image version=$(docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.version"}}' "$image")"
  done
```

```text
cafe-web:1.4.0 version=1.4.0
ubuntu:24.04 version=24.04
```

`index` is needed because the key contains dots, which the template language would read as nested fields. Other
images may appear too: many official images (Ubuntu, for example) carry OCI labels. `grep -v '<none>'` skips untagged
images, which cannot be inspected by name.
