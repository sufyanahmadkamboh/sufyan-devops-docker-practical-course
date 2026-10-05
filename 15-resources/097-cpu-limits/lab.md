<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 097 · CPU limits · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a container pinned to core 0 only and show which cores it may use.

**Expected result.** `0`.

**Verification.**

```bash
docker run --rm --cpuset-cpus 0 alpine:3.23 cat /sys/fs/cgroup/cpuset.cpus.effective
```
