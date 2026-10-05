<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 082 · Image security: trusted, minimal, pinned, scanned · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write the first line of a Dockerfile that pins `python:3.14-slim` to its digest while keeping the tag readable for
humans (`FROM name:tag@sha256:…`), then build an image from it to prove it works.

## Solution

```bash
mkdir -p ~/docker-practice/lesson-082 && cd ~/docker-practice/lesson-082
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' python:3.14-slim)
printf 'FROM python:3.14-slim@%s\nCMD ["python", "--version"]\n' "${digest#*@}" > Dockerfile
head -1 Dockerfile | cut -c1-40
docker build -q -t pinned:1.0 . > /dev/null && docker image ls pinned --format '{{.Repository}}:{{.Tag}}'
```

```text
FROM python:3.14-slim@sha256:c3e521df8b2
pinned:1.0
```

When both are given, Docker uses the digest; the tag is documentation. Tools such as Dependabot or Renovate update the
digest when a new base image is published, through a reviewed pull request.
