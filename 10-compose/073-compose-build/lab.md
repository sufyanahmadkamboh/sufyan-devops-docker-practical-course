<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 073 · Building images with Compose · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Build a second version with `APP_VERSION=1.5.0` without editing `compose.yaml`, using
`docker compose build --build-arg`, and check the variable in a one-off container.

**Expected result.** `1.5.0`. (The image keeps its name `cafe-api:1.4.0` from the file: a reason to take the tag from a
variable, as the challenge does.)

**Verification.**

```bash
cd ~/docker-practice/lesson-073
docker compose build --quiet --build-arg APP_VERSION=1.5.0 api 2> /dev/null
docker compose run --rm --no-deps api printenv APP_VERSION 2> /dev/null
```

Back to 1.4.0:

```bash
docker compose build --quiet 2> /dev/null
docker compose up -d 2> /dev/null
```
