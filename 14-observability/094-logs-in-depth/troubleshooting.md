<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 094 · Logs in depth · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Start the worker, which processes an order every half second, and look at its logs after a few seconds:

```bash
docker run -d --name worker -v "$(pwd)/worker.py:/worker.py:ro" python:3.14-alpine python /worker.py > /dev/null && echo "started worker"
```

```bash
sleep 4
docker logs worker
```

```text
ERROR order 5: payment declined
```

Only errors. Did the worker process anything at all?

## Troubleshoot it

The process is running:

```bash
docker top worker -o pid,args
```

And the code prints an `INFO` line for every successful order. The `INFO` lines are written to **stdout**, the
`ERROR` lines to **stderr**. When stdout is not a terminal (in a container, it is a pipe to Docker), Python collects
stdout in an 8 KB buffer and writes it out only when the buffer is full or the program exits; stderr is written line
by line. The lines exist, they are just stuck in the buffer. Proof: with a terminal (`-t`), Python does not buffer:

```bash
docker run -d --name worker-tty -t -v "$(pwd)/worker.py:/worker.py:ro" python:3.14-alpine python /worker.py > /dev/null
sleep 2
docker logs worker-tty | head -2
docker rm -f worker-tty > /dev/null
```

`-t` is a workaround for a test, not a fix: it mixes stdout and stderr into one stream.

## Fix it

Tell Python not to buffer: `PYTHONUNBUFFERED=1` (in a Dockerfile: `ENV PYTHONUNBUFFERED=1`; or `python -u`):

```bash
docker rm -f worker > /dev/null
docker run -d --name worker -e PYTHONUNBUFFERED=1 -v "$(pwd)/worker.py:/worker.py:ro" python:3.14-alpine python /worker.py > /dev/null && echo "started worker"
```

```bash
sleep 3
docker logs worker | head -5
```

```text
ERROR order 5: payment declined
INFO order 1: processed
INFO order 2: processed
INFO order 3: processed
INFO order 4: processed
INFO order 6: processed
```

Every line arrives as it is written, in order.
