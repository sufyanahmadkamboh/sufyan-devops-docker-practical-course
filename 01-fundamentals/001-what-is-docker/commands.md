<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 001 · What is Docker? · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/prefetch-images.sh
```

## Demonstration

```bash
docker run --rm python:3.14-slim python --version
docker run --rm node:24-alpine node --version
docker run --rm golang:1.26-alpine go version
```

```bash
docker run --rm alpine:3.23 cat /etc/os-release
```

## Hands-on lab

```bash
docker run --rm php:8.5-fpm-alpine php --version
```

## Break it

```bash
docker run --rm python:3.99-slim python --version 2>&1
```

## Troubleshoot it

```bash
docker image ls python
```

## Fix it

```bash
docker run --rm python:3.14-slim python --version
```

## Practice challenge

```bash
docker run --rm alpine:3.23 sh -c 'echo hello > /tmp/note.txt && cat /tmp/note.txt'
docker run --rm alpine:3.23 cat /tmp/note.txt 2>&1 || true
```
