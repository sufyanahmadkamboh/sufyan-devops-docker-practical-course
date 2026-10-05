<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 098 · Memory limits · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run --rm --memory 64m alpine:3.23 cat /sys/fs/cgroup/memory.max
```

```bash
docker run --rm alpine:3.23 cat /sys/fs/cgroup/memory.max
```

```bash
docker run --name greedy --memory 32m --memory-swap 32m alpine:3.23 sh -c 'head -c 100m /dev/zero | tail' ||
  echo "exit status: $?"
```

```bash
docker inspect --format 'exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' greedy
docker rm greedy > /dev/null
```

## Hands-on lab

```bash
docker run -d --name limited --memory 128m --memory-reservation 64m alpine:3.23 sleep 300 > /dev/null
docker exec limited sh -c 'echo "max=$(cat /sys/fs/cgroup/memory.max) low=$(cat /sys/fs/cgroup/memory.low)"'
docker inspect --format 'Memory={{.HostConfig.Memory}} MemoryReservation={{.HostConfig.MemoryReservation}}' limited
docker rm -f limited > /dev/null
```

## Break it

```bash
docker run --rm --memory 4m alpine:3.23 true 2>&1
```

## Troubleshoot it

```bash
docker run --rm --memory 64m --memory-reservation 128m alpine:3.23 true 2>&1
```

## Fix it

```bash
docker run -d --name measure nginx:1.30-alpine > /dev/null
sleep 2
docker stats --no-stream --format 'MEM {{.Name}} {{.MemUsage}}' measure
docker rm -f measure > /dev/null
```

```bash
docker run -d --name web --memory 64m nginx:1.30-alpine > /dev/null
docker inspect --format 'Memory={{.HostConfig.Memory}}' web
```

## Practice challenge

```bash
docker update --memory 48m --memory-swap 48m web > /dev/null
docker exec web cat /sys/fs/cgroup/memory.max
```

## Cleanup

```bash
docker rm -f greedy limited measure web > /dev/null 2>&1 || true
```
