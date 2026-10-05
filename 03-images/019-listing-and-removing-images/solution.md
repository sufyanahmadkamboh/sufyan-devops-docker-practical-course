<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 019 · Listing and removing images · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Create two tags for the same image (`docker image tag alpine:3.23 cafe-base:1` and `cafe-base:1.0`), remove one, then
the other. Explain why the first removal prints only `Untagged` and why `alpine:3.23` survives both.

## Solution

```bash
docker image tag alpine:3.23 cafe-base:1
docker image tag alpine:3.23 cafe-base:1.0
docker image rm cafe-base:1
docker image rm cafe-base:1.0
docker image ls --format '{{.Repository}}:{{.Tag}}' alpine
```

```text
Untagged: cafe-base:1
Untagged: cafe-base:1.0
alpine:3.23
```

A tag is only a name pointing to an image ID (lesson 020). `docker image rm` removes the name; the image itself is
deleted only when no name and no container refers to it any more. Here `alpine:3.23` still points to it, so both
removals only untag.
