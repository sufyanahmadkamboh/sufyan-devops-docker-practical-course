<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 130 · Production Dockerfile · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Production platforms stop containers all the time: every deployment, scale-down and node maintenance sends `SIGTERM`
to the container, waits for it to stop (Docker: up to 10 seconds by default), then kills it with `SIGKILL`. Stop a
container of each image and look at how it ended:

```bash
docker run -d --name api-before api:before > /dev/null
sleep 2
docker stop api-before api-final > /dev/null
docker inspect api-before api-final --format '{{.Name}}: exit code {{.State.ExitCode}}' | tr -d /
```

```text
api-before: exit code 137
api-final: exit code 0
```

`api-final` stopped cleanly (`0`). `api-before` was killed: 137 = 128 + 9, the number of `SIGKILL`.

## Troubleshoot it

Look at process 1 in each container (start them again first):

```bash
docker start api-before api-final > /dev/null
sleep 2
docker top api-before -o pid,args
docker top api-final -o pid,args
```

```text
PID                 COMMAND
2569042             sh start.sh
2569057             node server.js
PID                 COMMAND
2569096             node server.js
```

`SIGTERM` goes to process 1 only. In `api-final` that is Node.js, whose `SIGTERM` handler closes the server and exits
with code 0. In `api-before` process 1 is the shell running `start.sh`, and Node.js is its child. The shell does not
pass the signal on, so Node.js never runs its handler: it is killed in the middle of whatever it was doing, and open
requests are cut off, on every deployment.

## Fix it

Use the exec form for `CMD` (and `ENTRYPOINT`) so that the application is process 1, as in `Dockerfile`:

```bash
cd ~/docker-practice/lesson-130
grep '^CMD' Dockerfile
grep SIGTERM server.js
```

When a start script is really needed, end it with `exec`: the shell then **replaces** itself with Node.js, which
becomes process 1. Fix `start.sh`, rebuild, and stop it again:

```bash
cd ~/docker-practice/lesson-130
sed 's|^node server.js|exec node server.js|' start.sh > start.new && mv start.new start.sh
docker rm -f api-before > /dev/null
docker build -q -f Dockerfile.before -t api:before . > /dev/null
docker run -d --name api-before api:before > /dev/null
sleep 2
docker top api-before -o pid,args
docker stop api-before > /dev/null
docker inspect api-before --format '{{.Name}}: exit code {{.State.ExitCode}}' | tr -d /
```

```text
PID                 COMMAND
2569297             node server.js
api-before: exit code 0
```

For programs that do not handle `SIGTERM` at all, `docker run --init` adds a tiny init process as PID 1 that forwards
signals.
