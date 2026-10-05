<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 042 · Containerizing a Go application · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Check that the binary is really static: run it in a **different** image that has no Go at all
(`alpine:3.23`), by copying it out of the image with `docker cp`.

**Expected result.** The program starts in plain Alpine and logs `go-api listening on port 8080`.

**Verification.**

```bash
cd ~/docker-practice/lesson-042
docker create --name go-extract go-api:1.0 > /dev/null
docker cp go-extract:/usr/local/bin/go-api ./go-api-binary
docker rm go-extract > /dev/null
docker run -d --name go-plain -v "$(pwd)/go-api-binary:/go-api" alpine:3.23 /go-api > /dev/null
sleep 1
docker logs go-plain 2>&1
docker rm -f go-plain > /dev/null
```

`docker create` makes a container without starting it; `docker cp` copies files out of it. This is the manual version
of what a multi-stage build does automatically (lesson 087).
