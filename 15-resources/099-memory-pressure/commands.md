<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 099 · Memory pressure and OOM kills · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-099 15-resources/099-memory-pressure/examples
cd ~/docker-practice/lesson-099
head -4 leak.py
```

## Demonstration

```bash
docker run -d --name cache --memory 64m --memory-swap 64m -v "$(pwd)/leak.py:/leak.py:ro" python:3.14-alpine python /leak.py > /dev/null && echo "started cache"
```

```bash
docker inspect --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' cache
```

```bash
docker logs cache | tail -2
```

```bash
docker run -d --name killed alpine:3.23 sleep 300 > /dev/null
docker kill killed > /dev/null
docker inspect --format 'exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' killed
```

## Hands-on lab

```bash
docker events --since 5m --until "$(date +%s)" --filter container=cache --format '{{.Action}}' | grep -E '^(oom|die)'
docker inspect cache --format 'OOMKilled={{.State.OOMKilled}}'
```

## Break it

```bash
docker run -d --name service --memory 64m --memory-swap 64m -v "$(pwd)/leak.py:/leak.py:ro" python:3.14-alpine \
  sh -c 'python /leak.py; echo "worker exited with status $?"; sleep 300' > /dev/null && echo "started service"
```

```bash
docker logs service | tail -1
```

```bash
docker inspect --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' service
```

## Troubleshoot it

```bash
docker exec service cat /sys/fs/cgroup/memory.events
```

```bash
docker events --since 5m --until "$(date +%s)" --filter container=service --filter event=oom --format '{{.Action}} in {{.Actor.Attributes.name}}'
```

## Fix it

```bash
docker rm -f service > /dev/null
docker run -d --name service --memory 64m --memory-swap 64m -e MAX_ENTRIES=4 -v "$(pwd)/leak.py:/leak.py:ro" python:3.14-alpine \
  sh -c 'python /leak.py; echo "worker exited with status $?"; sleep 300' > /dev/null && echo "started service"
```

```bash
sleep 6
docker logs service | tail -1
docker exec service grep oom_kill /sys/fs/cgroup/memory.events
docker stats --no-stream --format '{{.Name}} {{.MemUsage}}' service
```

## Practice challenge

```bash
for id in $(docker ps -aq); do
  name=$(docker inspect --format '{{.Name}}' "$id")
  oom=$(docker inspect --format '{{.State.OOMKilled}}' "$id")
  kills=$(docker exec "$id" sh -c 'grep oom_kill /sys/fs/cgroup/memory.events' 2>/dev/null | head -1)
  echo "$name oom=$oom ${kills:-(not running)}"
done
```

## Cleanup

```bash
docker rm -f cache killed service > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-099
```
