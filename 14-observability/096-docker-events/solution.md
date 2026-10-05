<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 096 · docker events · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Watch events **live** while they happen: stream the events of a container named `watched` for 8 seconds, while a
background job starts it and stops it. (`--until` with a time in the future makes the live stream end by itself.)

## Solution

```bash
( sleep 2; docker run -d --name watched alpine:3.23 sleep 300; docker stop -t 1 watched ) > /dev/null &
docker events --filter type=container --filter container=watched --until "$(( $(date +%s) + 8 ))" --format '{{.Type}} {{.Action}}'
```

```text
container create
container start
container kill
container kill
container stop
container die
```

`docker stop` sends SIGTERM (a `kill` event with signal 15), waits for `-t` seconds, then sends SIGKILL; `sleep`
running as PID 1 has no handler for SIGTERM, which the kernel then ignores, so you also see a second `kill` (signal 9)
before `die` and `stop`.
