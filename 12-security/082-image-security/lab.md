<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 082 · Image security: trusted, minimal, pinned, scanned · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Get the digest reference of `python:3.14-slim` and run `python --version` from it by digest.

**Expected result.** `Python 3.14…`, from an image referenced as `python@sha256:…`.

**Verification.**

```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' python:3.14-slim)
echo "$digest"
docker run --rm "$digest" python --version
```
