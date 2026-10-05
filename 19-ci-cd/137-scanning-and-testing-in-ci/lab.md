<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 137 · Scanning and testing in CI · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Use the gate the way a pipeline does: push to the local registry only if the gate passes.

**Expected result.** All five rules pass, then `push allowed`.

**Verification.**

```bash
cd ~/docker-practice/lesson-137
bash image-policy.sh node-api:1.0.0 && echo "push allowed"
```
