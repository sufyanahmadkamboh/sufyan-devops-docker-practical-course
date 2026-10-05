<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 021 · The danger of the latest tag · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a container `menu-a` from `cafe-menu` (no tag), then print the image ID it uses and the
version file inside it.

**Expected result.** An image ID (`sha256:…`) and `cafe menu 1.0`.

**Verification.**

```bash
cd ~/docker-practice/lesson-021
docker run -d --name menu-a cafe-menu > /dev/null
docker container inspect --format '{{.Image}}' menu-a
docker exec menu-a cat /version
```
