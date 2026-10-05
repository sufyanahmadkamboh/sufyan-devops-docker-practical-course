<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 099 · Memory pressure and OOM kills · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

In real services the application often runs **under** another process: a shell script, a process manager, a web
server with worker processes. Run the same cache as a child of a shell that keeps the container alive:

```bash
docker run -d --name service --memory 64m --memory-swap 64m -v "$(pwd)/leak.py:/leak.py:ro" python:3.14-alpine \
  sh -c 'python /leak.py; echo "worker exited with status $?"; sleep 300' > /dev/null && echo "started service"
```

```bash
docker logs service | tail -1
```

The container is up, the cache is gone:

```bash
docker inspect --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}' service
```

```text
status=running exit=0 oom=true
```

## Troubleshoot it

A **running** container with `OOMKilled=true`: the main process (the shell) survived, a process under it was killed.
`docker ps` shows nothing unusual, so this is easy to miss. The kernel's counters for the container's cgroup include
every process in it:

```bash
docker exec service cat /sys/fs/cgroup/memory.events
```

```text
low 0
high 0
max 20
oom 1
oom_kill 1
oom_group_kill 0
```

And the engine recorded the event:

```bash
docker events --since 5m --until "$(date +%s)" --filter container=service --filter event=oom --format '{{.Action}} in {{.Actor.Attributes.name}}'
```

```text
oom in service
```

The root cause is in the logs: memory grew steadily, 8 MB at a time, until the limit. A steady climb means a leak
(more memory will only delay the kill); a jump at a particular request means one operation needs more than the limit.

## Fix it

Fix the leak: bound the cache. With at most 4 entries (32 MB) the service runs indefinitely within its 64 MB limit:

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

```text
cache holds 32 MB
oom_kill 0
service 36.13MiB / 64MiB
```
