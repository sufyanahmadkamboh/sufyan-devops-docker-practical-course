<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 027 · CMD · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

A Dockerfile has two `CMD` lines: `CMD ["echo", "first"]` and then `CMD ["echo", "second"]`. Predict what the
container prints, then prove it, and show that only one default command is stored.

## Solution

```bash
cd ~/docker-practice/lesson-027
printf 'FROM alpine:3.23\nCMD ["echo", "first"]\nCMD ["echo", "second"]\n' > Dockerfile.twice
docker build -q -f Dockerfile.twice -t cmd-form:twice . > /dev/null 2>&1
docker run --rm cmd-form:twice
docker image inspect --format '{{json .Config.Cmd}}' cmd-form:twice
docker build --check -f Dockerfile.twice . 2>&1 | grep -o "WARNING: [A-Za-z]*"
```

```text
second
["echo","second"]
WARNING: MultipleInstructionsDisallowed
```

Each `CMD` overwrites the previous one: only the last counts. This also applies to the base image's `CMD`: `alpine`
sets `CMD ["/bin/sh"]`, and your `CMD` replaces it. `docker build --check` reports `MultipleInstructionsDisallowed`
for the duplicate.
