<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 075 · What is a registry? · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Push `busybox:1.37` to your registry as `localhost:5000/tools/busybox:1.37`, and list the
repositories of the registry.

**Expected result.** The catalog lists `cafe/alpine` and `tools/busybox`.

**Verification.**

```bash
docker tag busybox:1.37 localhost:5000/tools/busybox:1.37
docker push -q localhost:5000/tools/busybox:1.37
curl -s localhost:5000/v2/_catalog
```
