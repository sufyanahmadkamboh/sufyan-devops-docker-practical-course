<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 133 · Production configuration · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a third environment, `api-dev`, on port 8083, with the greeting `Hello from dev` and version
`dev`, from the same image. Verify its answer and that its image ID matches `api-production`.

**Expected result.** The new greeting, and the two image IDs are identical.

**Verification.**

```bash
docker run -d --name api-dev -p 8083:3000 -e GREETING="Hello from dev" -e APP_VERSION=dev node-api:1.0 > /dev/null
sleep 1
curl -s http://localhost:8083/ && echo
[ "$(docker inspect api-dev --format '{{.Image}}')" = "$(docker inspect api-production --format '{{.Image}}')" ] && echo "same image"
```
