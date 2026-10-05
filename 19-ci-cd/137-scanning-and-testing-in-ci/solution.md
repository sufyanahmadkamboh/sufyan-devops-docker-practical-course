<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 137 · Scanning and testing in CI · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Your team decides on a size budget of 10 MB for this image (impossible with Node.js, which is the point). Run the gate
with that budget, and show that only the size rule fails.

## Solution

```bash
cd ~/docker-practice/lesson-137
MAX_MB=10 bash image-policy.sh node-api:1.0.1 || echo "gate failed: exit code $?"
```

```text
PASS  version tag
PASS  non-root user
PASS  healthcheck
PASS  no secrets in ENV
FAIL  size (59 MB, budget 10 MB): 59 MB > 10 MB
gate failed: exit code 1
```

A budget turns "the image got bigger" into a visible, reviewable decision. To meet a small budget, the image must
change (a smaller base, multi-stage builds: module 13), or the team raises the budget on purpose.
