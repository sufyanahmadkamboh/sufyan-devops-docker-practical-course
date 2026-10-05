<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 135 · Docker in CI · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show that the shipped image contains no tests and does not run as root, and that the tests exist
only in the test stage.

**Expected result.** `ls /app` in the production image shows no `test` folder; the user is `node`.

**Verification.**

```bash
docker run --rm localhost:5000/node-api:1.0.0 ls /app
echo "user=$(docker image inspect localhost:5000/node-api:1.0.0 --format '{{.Config.User}}')"
```
