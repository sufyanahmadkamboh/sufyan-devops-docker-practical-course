<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 022 · Your first Dockerfile · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write a Dockerfile, `Dockerfile.hello`, for an image that only prints `Hello from my first image` when it runs, based
on `alpine:3.23`. Build it as `hello-image:1.0` and run it.

## Solution

```bash
cd ~/docker-practice/lesson-022
printf 'FROM alpine:3.23\nCMD ["echo", "Hello from my first image"]\n' > Dockerfile.hello
docker build -q -f Dockerfile.hello -t hello-image:1.0 . > /dev/null
docker run --rm hello-image:1.0
```

```text
Hello from my first image
```

Two instructions are enough: the base image and the command. No `COPY` is needed because the image adds no files.
