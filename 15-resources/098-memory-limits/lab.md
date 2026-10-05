<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 098 · Memory limits · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a container with `--memory 128m --memory-reservation 64m`, and show both values in the
container's cgroup files (`memory.max`, `memory.low`) and in `docker inspect`.

**Expected result.** `134217728` and `67108864` in both places.

**Verification.**

```bash
docker run -d --name limited --memory 128m --memory-reservation 64m alpine:3.23 sleep 300 > /dev/null
docker exec limited sh -c 'echo "max=$(cat /sys/fs/cgroup/memory.max) low=$(cat /sys/fs/cgroup/memory.low)"'
docker inspect --format 'Memory={{.HostConfig.Memory}} MemoryReservation={{.HostConfig.MemoryReservation}}' limited
docker rm -f limited > /dev/null
```
