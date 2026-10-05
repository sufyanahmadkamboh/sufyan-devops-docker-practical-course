<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 099 · Memory pressure and OOM kills · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Use `docker events` to list the OOM events of the `cache` container from the last few minutes.

**Expected result.** `die` (most engines also report an `oom` line before it), and `OOMKilled=true` in the
container's state.

**Verification.**

```bash
docker events --since 5m --until "$(date +%s)" --filter container=cache --format '{{.Action}}' | grep -E '^(oom|die)'
docker inspect cache --format 'OOMKilled={{.State.OOMKilled}}'
```
