<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 073 · Building images with Compose · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Make the image tag configurable: change `image:` to `cafe-api:${APP_VERSION:-dev}` and the build argument to
`${APP_VERSION:-dev}`, then build version `2.0.0` from the command line only.

## Solution

```bash
cd ~/docker-practice/lesson-073
sed -i.bak -e 's/image: cafe-api:1.4.0/image: cafe-api:${APP_VERSION:-dev}/' \
           -e 's/APP_VERSION: "1.4.0"/APP_VERSION: "${APP_VERSION:-dev}"/' compose.yaml && rm compose.yaml.bak
APP_VERSION=2.0.0 docker compose build --quiet 2> /dev/null
docker image ls cafe-api --format '{{.Repository}}:{{.Tag}}' | sort
```

```text
cafe-api:1.4.0
cafe-api:2.0.0
```

One variable now sets both the version inside the image and its tag: CI pipelines pass the Git tag or commit here.
