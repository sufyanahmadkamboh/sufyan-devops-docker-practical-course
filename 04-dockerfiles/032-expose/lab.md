<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 032 · EXPOSE · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a second container of `cafe-api:expose` without any `-p` or `-P` option, and show with
`docker port` that nothing is published, although the image exposes 3000.

**Expected result.** `docker port` prints nothing for that container; `docker container ls` shows `3000/tcp` without
a host address.

**Verification.**

```bash
docker run -d --name cafe-api-internal cafe-api:expose > /dev/null
echo "published: [$(docker port cafe-api-internal)]"
docker container ls --filter name=cafe-api-internal --format 'unpublished: {{.Ports}}'
```
