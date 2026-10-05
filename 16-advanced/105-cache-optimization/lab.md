<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 105 · Build cache optimization · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Change `requirements.txt` by adding a comment line, rebuild the `after` version, and check the output
of the pip step: with the cache mount, pip reuses the packages it downloaded before.

**Expected result.** The pip step runs (its input changed), but pip prints `Using cached` for the packages.

**Verification.**

```bash
echo "# pinned versions, reviewed" >> requirements.txt
docker build --progress plain -f Dockerfile.after -t cafe-api:after . 2>&1 | grep -m 3 'Using cached'
```
