<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 018 · Pulling images · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Pull `alpine:3.23` from `mirror.gcr.io` (the official images are under `library/`), show that it has
the same ID as your `alpine:3.23`, then remove only the mirror's name.

**Expected result.** Both names list the same image ID; after the removal, `alpine:3.23` is still there.

**Verification.**

```bash
docker image pull -q mirror.gcr.io/library/alpine:3.23
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' | grep alpine
docker image rm mirror.gcr.io/library/alpine:3.23
docker image ls --format '{{.Repository}}:{{.Tag}}' alpine
```

`Untagged` (not `Deleted`): the image is still used by the name `alpine:3.23`, so only the name is removed.
