<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 030 · ENV · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show the environment variables stored in `cafe-api:env`, and the ones the container `cafe-api-de`
really has.

**Expected result.** The image has `GREETING=Hello from the cafe`; the container has the German greeting.

**Verification.**

```bash
docker image inspect --format '{{json .Config.Env}}' cafe-api:env
docker exec cafe-api-de env | grep -e GREETING -e PORT -e APP_VERSION
```
