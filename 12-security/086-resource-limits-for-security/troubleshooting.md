<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 086 · Resource limits for security · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The same protection with a limit that is too tight for a legitimate application: a web server with worker processes
under `--pids-limit 3`:

```bash
docker run -d --name web --pids-limit 3 nginx:1.30-alpine > /dev/null && echo "started web"
```

```bash
docker logs web 2>&1 | grep -iE 'fork|resource' | head -2
```

```text
/docker-entrypoint.sh: line 8: can't fork: Resource temporarily unavailable
```

## Troubleshoot it

`can't fork: Resource temporarily unavailable` (`EAGAIN`) is the error a process gets when the pids limit is reached.
Here it hit nginx's start script, before nginx itself even ran. Compare the limit with the container's state:

```bash
echo "limit=$(docker inspect --format '{{.HostConfig.PidsLimit}}' web)"
docker ps -a --filter name=web --format 'status={{.Status}}'
```

```text
limit=3
status=Exited (2) Less than a second ago
```

The start script runs helper commands (each one a process), and nginx then starts one worker process per CPU core:
three processes are far too few.

## Fix it

Measure what the application needs without a limit, then set a limit with generous headroom, so it stops runaways
without hurting normal operation:

```bash
docker rm -f web > /dev/null
docker run -d --name web nginx:1.30-alpine > /dev/null
sleep 2
docker stats --no-stream --format 'running={{.PIDs}}' web
```

```text
running=15
```

```bash
docker rm -f web > /dev/null
docker run -d --name web --pids-limit 100 --memory 128m --cpus 1 nginx:1.30-alpine > /dev/null && echo "started web"
```

```bash
docker inspect --format 'pids={{.HostConfig.PidsLimit}} memory={{.HostConfig.Memory}} cpus={{.HostConfig.NanoCpus}}' web
```
