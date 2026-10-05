<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 131 · Container design · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Request a page that does not exist from the `web` container, then find that request in the
container's logs.

**Expected result.** `curl` prints `HTTP/1.1 404 Not Found`, and `docker logs web` contains a line with `"HEAD /missing.html HTTP/1.1" 404`.

**Verification.**

```bash
curl -sI http://localhost:8080/missing.html | head -1
docker logs web 2>/dev/null | grep missing.html
```
