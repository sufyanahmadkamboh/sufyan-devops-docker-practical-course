<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 017 · Image layers · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Find out how many file layers `python:3.14-slim` has, and which of its steps added the most data.

**Expected result.** A layer count and, near the top of the history, the step that installs Python with tens of MB.

**Verification.**

```bash
echo "$(docker image inspect --format '{{len .RootFS.Layers}}' python:3.14-slim) layers"
docker image history --format '{{.Size}}\t{{.CreatedBy}}' python:3.14-slim | sort -h | tail -3
```
