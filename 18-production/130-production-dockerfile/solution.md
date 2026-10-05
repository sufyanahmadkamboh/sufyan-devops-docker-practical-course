<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 130 · Production Dockerfile · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Add the version of the image as a label `org.opencontainers.image.version`, set at build time with
`--build-arg VERSION=1.2.0`, without editing the Dockerfile permanently for every release.

## Solution

Declare an `ARG` and use it in a label: build arguments are fine for non-secret values like a version.

```bash
cd ~/docker-practice/lesson-130
printf 'ARG VERSION=dev\nLABEL org.opencontainers.image.version=$VERSION\n' >> Dockerfile
docker build -q --build-arg VERSION=1.2.0 -t api:1.2.0 . > /dev/null
docker image inspect api:1.2.0 --format '{{index .Config.Labels "org.opencontainers.image.version"}}'
```

```text
1.2.0
```

The two lines are appended after `CMD`, which is fine: `LABEL` and `ARG` can appear anywhere, and only the last `CMD`
counts. In CI, the version comes from the Git tag (lesson 136).
