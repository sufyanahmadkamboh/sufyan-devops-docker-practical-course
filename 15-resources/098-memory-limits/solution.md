<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 098 · Memory limits · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Without restarting it, lower the running `web` container's memory limit to 48 MB, and show the new value inside the
container. (`docker update` needs `--memory-swap` too when the container has swap configured.)

## Solution

```bash
docker update --memory 48m --memory-swap 48m web > /dev/null
docker exec web cat /sys/fs/cgroup/memory.max
```

```text
50331648
```

48 × 1024 × 1024 = 50331648 bytes. Lowering a limit below the current usage makes the kernel reclaim memory, and
OOM-kill if it cannot: measure first.
