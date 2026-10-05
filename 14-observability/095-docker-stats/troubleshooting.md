<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 095 · docker stats · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Somebody starts a "worker" with a bug: an endless loop that never sleeps.

```bash
docker run -d --name worker alpine:3.23 sh -c 'while :; do :; done' > /dev/null && echo "started worker"
```

Everything on the host gets slower. Which container is it?

## Troubleshoot it

Take a snapshot and sort by CPU (give the worker a few seconds to show up in the measurement):

```bash
sleep 3
docker stats --no-stream --format '{{.CPUPerc}} {{.Name}}' | sort -rn | head -1
```

```text
99.80% worker
```

About 100%: one full CPU core, all the time. Look inside it:

```bash
docker top worker -o pid,args
```

```text
PID                 COMMAND
2622829             sh -c while :; do :; done
```

The loop has no pause and no work: it is a bug, not load.

## Fix it

Two steps, as in a real incident. **Contain** it immediately with a CPU limit, without restarting it (lesson 097):

```bash
docker update --cpus 0.2 worker
```

```bash
sleep 3
docker stats --no-stream --format '{{.CPUPerc}} {{.Name}}' worker
```

```text
20.07% worker
```

The worker now gets at most a fifth of a core: the host is fine again. Then **fix the cause** (the code) and replace
the container:

```bash
docker rm -f worker > /dev/null
docker run -d --name worker --cpus 0.5 alpine:3.23 sh -c 'while :; do sleep 1; done' > /dev/null
docker stats --no-stream --format '{{.CPUPerc}} {{.Name}}' worker
```
