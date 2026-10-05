<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 136 · Build and push with GitHub Actions · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Release version 1.0.0: create the Git tag `v1.0.0`, and push the image tag the metadata step derives
from it (`1.0.0`, without the `v`) to the local registry.

**Expected result.** The registry lists `1.0.0`, `main` and `sha-…`.

**Verification.**

```bash
cd ~/docker-practice/lesson-136
git tag v1.0.0
version=$(git describe --tags --exact-match | sed 's/^v//')
docker tag localhost:5000/node-api:main "localhost:5000/node-api:$version"
docker push -q "localhost:5000/node-api:$version" > /dev/null
curl -s http://localhost:5000/v2/node-api/tags/list && echo
```
