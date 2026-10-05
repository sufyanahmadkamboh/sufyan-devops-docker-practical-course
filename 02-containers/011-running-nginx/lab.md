<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 011 · Running Nginx · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a second Nginx container named `web-2` from the image `nginx:1.29-alpine` (an older version) and
ask it for its version from another container. Nginx sends its version in the `Server` response header.

**Expected result.** `Server: nginx/1.29…` for `web-2`.

**Verification.**

```bash
docker run -d --name web-2 nginx:1.29-alpine > /dev/null 2>&1 || true
docker run --rm alpine:3.23 wget -qS -O /dev/null "http://$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web-2)" 2>&1 | grep Server
```
