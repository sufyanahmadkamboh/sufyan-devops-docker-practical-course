<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 031 · ARG · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Build `menu-arg:1.5.0` with `VERSION=1.5.0` and also set `ENV APP_VERSION=$VERSION` so the version is
available to the running container as an environment variable.

**Expected result.** `docker run --rm menu-arg:1.5.0 sh -c 'echo $APP_VERSION'` prints `1.5.0`.

**Verification.**

```bash
cd ~/docker-practice/lesson-031
printf 'FROM alpine:3.23\nARG VERSION=dev\nENV APP_VERSION=$VERSION\n' > Dockerfile.env
docker build -q -f Dockerfile.env --build-arg VERSION=1.5.0 -t menu-arg:1.5.0 . > /dev/null
docker run --rm menu-arg:1.5.0 sh -c 'echo $APP_VERSION'
```
