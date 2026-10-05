<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 097 · CPU limits · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run --rm --cpus 0.5 alpine:3.23 cat /sys/fs/cgroup/cpu.max
```

```bash
docker run --rm alpine:3.23 cat /sys/fs/cgroup/cpu.max
```

```bash
docker run -d --name burner --cpus 0.5 alpine:3.23 sh -c 'while :; do :; done' > /dev/null && echo "started burner"
```

```bash
sleep 3
docker stats --no-stream --format '{{.Name}} {{.CPUPerc}}' burner
```

```bash
docker exec burner sh -c 'grep -E "nr_periods|nr_throttled" /sys/fs/cgroup/cpu.stat'
```

## Hands-on lab

```bash
docker run --rm --cpuset-cpus 0 alpine:3.23 cat /sys/fs/cgroup/cpuset.cpus.effective
```

## Break it

```bash
docker run --rm --cpus 64 alpine:3.23 true 2>&1
```

## Troubleshoot it

```bash
echo "engine CPUs: $(docker info --format '{{.NCPU}}')"
```

## Fix it

```bash
docker run --rm --cpus 1 alpine:3.23 sh -c 'echo "cpu.max: $(cat /sys/fs/cgroup/cpu.max)"'
```

## Practice challenge

```bash
docker update --cpus 1 burner > /dev/null
docker exec burner cat /sys/fs/cgroup/cpu.max
```

```bash
sleep 3
docker stats --no-stream --format '{{.Name}} {{.CPUPerc}}' burner
```

## Cleanup

```bash
docker rm -f burner > /dev/null 2>&1 || true
```
