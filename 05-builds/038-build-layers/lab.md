<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 038 · Build layers · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Count the file system layers of `layers:demo` and of its base image `alpine:3.23`. How many layers did
our Dockerfile add?

**Expected result.** Alpine has 1 layer; `layers:demo` has 4: `RUN`, `WORKDIR` and `COPY` each added one (BuildKit
records `WORKDIR` as a small layer because it creates the folder).

**Verification.**

```bash
for image in alpine:3.23 layers:demo; do
  echo "$image $(docker image inspect --format '{{len .RootFS.Layers}}' "$image")"
done
```
