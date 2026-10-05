<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 089 · Multi-stage builds for Go · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Compare the binary built with and without `-ldflags="-s -w"`. Build the `build` stage, then build the
same program once more inside it without the flags, and list both files.

**Expected result.** The stripped binary is noticeably smaller (often around 30 %); both run the same code.

**Verification.**

```bash
docker build -q --target build -t go-distroless:build . > /dev/null
docker run --rm go-distroless:build sh -c 'CGO_ENABLED=0 go build -o /tmp/go-api-full . && ls -l /out/go-api /tmp/go-api-full'
```
