<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 098 · Memory limits · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Make a tiny service even tinier:

```bash
docker run --rm --memory 4m alpine:3.23 true 2>&1
```

```text
docker: Error response from daemon: Minimum memory limit allowed is 6MB

Run 'docker run --help' for more information
```

## Troubleshoot it

The engine refuses the container before it starts: a limit below 6 MB cannot hold even the container's own runtime
overhead. The message names the rule. Other limits are refused the same way, for example a reservation above the
limit:

```bash
docker run --rm --memory 64m --memory-reservation 128m alpine:3.23 true 2>&1
```

```text
docker: Error response from daemon: Minimum memory limit can not be less than memory reservation limit, see usage

Run 'docker run --help' for more information
```

## Fix it

Choose a limit from what the application really uses. Measure it first, without a limit, with `docker stats`
(lesson 095), and add headroom:

```bash
docker run -d --name measure nginx:1.30-alpine > /dev/null
sleep 2
docker stats --no-stream --format 'MEM {{.Name}} {{.MemUsage}}' measure
docker rm -f measure > /dev/null
```

```text
MEM measure 11.48MiB / 15.35GiB
```

```bash
docker run -d --name web --memory 64m nginx:1.30-alpine > /dev/null
docker inspect --format 'Memory={{.HostConfig.Memory}}' web
```
