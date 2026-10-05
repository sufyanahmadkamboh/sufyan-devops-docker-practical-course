<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 087 · Why multi-stage builds? · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Use `--target build` to build only the first stage as `go-multi:build`, and show that the binary is
in it at `/out/go-api`, next to the source code.

**Expected result.** `go-multi:build` is about as big as the single-stage image (it is the toolchain stage) and
`/out/go-api` exists in it.

**Verification.**

```bash
docker build -q --target build -t go-multi:build . > /dev/null
docker run --rm go-multi:build ls -l /out/go-api /src
docker image ls --filter 'reference=go-multi' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```
