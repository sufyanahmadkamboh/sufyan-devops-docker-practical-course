<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 099 · Memory pressure and OOM kills · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write a short script that reports, for every container on the host (running or stopped), whether its main process was
OOM-killed, and how many OOM kills its running processes have suffered according to `memory.events`.

## Solution

```bash
for id in $(docker ps -aq); do
  name=$(docker inspect --format '{{.Name}}' "$id")
  oom=$(docker inspect --format '{{.State.OOMKilled}}' "$id")
  kills=$(docker exec "$id" sh -c 'grep oom_kill /sys/fs/cgroup/memory.events' 2>/dev/null | head -1)
  echo "$name oom=$oom ${kills:-(not running)}"
done
```

```text
/service oom=false oom_kill 0
/killed oom=false (not running)
/cache oom=true (not running)
```

`docker exec` only works on running containers; for stopped ones, `OOMKilled` and the `oom` events are what remains.
`oom=true` on a running container means one of its child processes was killed.
