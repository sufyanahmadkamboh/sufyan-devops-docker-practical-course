<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 097 · CPU limits · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

`burner` is running with `--cpus 0.5`. Raise its limit to `1.0` without restarting it, prove that the new limit is
active inside the container, and check that it now uses about one full core.

## Solution

```bash
docker update --cpus 1 burner > /dev/null
docker exec burner cat /sys/fs/cgroup/cpu.max
```

```text
100000 100000
```

```bash
sleep 3
docker stats --no-stream --format '{{.Name}} {{.CPUPerc}}' burner
```

```text
burner 100.32%
```

`docker update` rewrites the container's cgroup settings while it runs: useful to contain a runaway container during
an incident (lesson 095).
