<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 035 · docker build · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Build the same folder a second time with **two** tags at once, `node-api:1.1` and `node-api:stable`,
and list the `node-api` images.

**Expected result.** Three tags. `1.1` and `stable` have the same image ID (one image, two names); because nothing
changed, the build was served from the cache and `1.0` has that ID too.

**Verification.**

```bash
cd ~/docker-practice/lesson-035
docker build -q -t node-api:1.1 -t node-api:stable . > /dev/null
docker image ls node-api
```
