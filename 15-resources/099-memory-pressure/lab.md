<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 099 · Memory pressure and OOM kills · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Use `docker events` to list the OOM events of the `cache` container from the last few minutes.

**Expected result.** At least one line `oom`, followed by `die`.

**Verification.**

```bash
docker events --since 5m --until "$(date +%s)" --filter container=cache --format '{{.Action}}' | grep -E '^(oom|die)'
```
