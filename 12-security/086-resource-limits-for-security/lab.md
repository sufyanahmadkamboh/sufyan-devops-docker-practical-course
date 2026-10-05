<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 086 · Resource limits for security · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a container with `--ulimit nofile=64:64` and show the open-file limit inside it with
`ulimit -n`.

**Expected result.** `64`.

**Verification.**

```bash
docker run --rm --ulimit nofile=64:64 alpine:3.23 sh -c 'ulimit -n'
```
