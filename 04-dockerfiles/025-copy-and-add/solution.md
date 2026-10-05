<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 025 · COPY and ADD · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Make a `.tar.gz` of the `public/` folder and build an image in which `ADD` unpacks it into `/srv/www/`. Verify that
`/srv/www/public/index.html` exists in the image.

## Solution

```bash
cd ~/docker-practice/lesson-025/menu-service
tar -czf public.tar.gz public
printf 'FROM alpine:3.23\nADD public.tar.gz /srv/www/\n' > Dockerfile.targz
docker build -q -f Dockerfile.targz -t copy-demo:targz . > /dev/null
docker run --rm copy-demo:targz ls /srv/www/public/index.html
```

```text
/srv/www/public/index.html
```

`ADD` recognises compressed archives too. With `COPY`, the file would arrive as `public.tar.gz`, unchanged.
