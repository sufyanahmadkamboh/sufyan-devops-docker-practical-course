<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 104 · Multi-architecture images · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Build only an `arm64` variant under the tag `cafe-hello:arm`, and show its architecture with
`docker image inspect`.

**Expected result.** `linux/arm64`.

**Verification.**

```bash
docker buildx build -q --platform linux/arm64 -t cafe-hello:arm --load . > /dev/null
docker image inspect --format '{{.Os}}/{{.Architecture}}' cafe-hello:arm
```
