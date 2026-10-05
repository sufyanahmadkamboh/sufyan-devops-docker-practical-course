<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 095 · docker stats · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write a command that prints a warning for every running container that uses more than 50% of its memory limit. Test it
by filling the `cache` container's memory: `docker exec cache redis-cli DEBUG POPULATE 550000` writes 550,000
test keys (the `cache` container was started with `--enable-debug-command local` to allow it).

## Solution

```bash
docker exec cache redis-cli DEBUG POPULATE 550000
```

```bash
docker stats --no-stream --format '{{.Name}} {{.MemPerc}}' | tr -d '%' |
  awk '$2 > 50 { print "WARNING " $1 " uses " $2 "% of its memory limit" }'
```

```text
WARNING cache uses 64.40% of its memory limit
```

`tr -d '%'` removes the percent sign so `awk` can compare numbers. Monitoring systems (cAdvisor + Prometheus, the
Docker integration of Datadog and others) collect the same cgroup numbers continuously and alert on rules like this.
