<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 086 · Resource limits for security · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run --rm alpine:3.23 cat /sys/fs/cgroup/pids.max
```

```bash
docker run --rm --pids-limit 10 alpine:3.23 cat /sys/fs/cgroup/pids.max
```

```bash
docker run --rm --pids-limit 10 alpine:3.23 sh -c 'for i in $(seq 1 20); do sleep 30 & done; echo "all started"' 2>&1 | tail -1
```

## Hands-on lab

```bash
docker run --rm --ulimit nofile=64:64 alpine:3.23 sh -c 'ulimit -n'
```

## Break it

```bash
docker run -d --name web --pids-limit 3 nginx:1.30-alpine > /dev/null && echo "started web"
```

```bash
docker logs web 2>&1 | grep -iE 'fork|resource' | head -2
```

## Troubleshoot it

```bash
echo "limit=$(docker inspect --format '{{.HostConfig.PidsLimit}}' web)"
docker ps -a --filter name=web --format 'status={{.Status}}'
```

## Fix it

```bash
docker rm -f web > /dev/null
docker run -d --name web nginx:1.30-alpine > /dev/null
sleep 2
docker stats --no-stream --format 'running={{.PIDs}}' web
```

```bash
docker rm -f web > /dev/null
docker run -d --name web --pids-limit 100 --memory 128m --cpus 1 nginx:1.30-alpine > /dev/null && echo "started web"
```

```bash
docker inspect --format 'pids={{.HostConfig.PidsLimit}} memory={{.HostConfig.Memory}} cpus={{.HostConfig.NanoCpus}}' web
```

## Practice challenge

```bash
docker run --rm --ulimit nofile=20:20 python:3.14-alpine python -c '
files = []
try:
    while True:
        files.append(open("/dev/null"))
except OSError as error:
    print(f"opened {len(files)} files, then: {error}")'
```

## Cleanup

```bash
docker rm -f web > /dev/null 2>&1 || true
```
