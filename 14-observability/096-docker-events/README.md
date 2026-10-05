# Lesson 096 · docker events

> Level 15 · Observability · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

The Docker engine records an **event** for everything that happens: a container is created, started, dies (with its
exit code), is killed by the kernel for using too much memory (`oom`), changes health status, is destroyed; images are
pulled, networks connected, volumes mounted. `docker events` streams them live or replays a time window. When a
container "keeps restarting" or "disappeared", the events tell you what happened and when.

## Visual

```text
  time ──────────────────────────────────────────────────────────────────────────────────▶
  create ─ start ─ die (exitCode=3) ─ start ─ die (exitCode=3) ─ start ─ die ─ … ─ destroy
    │        │          │
    │        │          └ the process exited; the restart policy may start it again
    │        └ the process started
    └ docker run / docker create

  docker events --since 5m --until "$(date +%s)" --filter container=NAME --format '{{.Action}} …'
                 └─ a past time window (without --until it keeps streaming new events)
```

## Lab setup

No files are needed: this lesson uses `alpine` containers.

## Demonstration

Do a full life cycle, then replay its events. `--until` with the current time (in seconds since 1970, `date +%s`)
makes `docker events` print the window and exit, instead of streaming forever:

<!-- test: contains=create; contains=start; contains=die; contains=destroy; output -->
```bash
docker run --name short-lived alpine:3.23 sh -c 'exit 0'
docker rm short-lived > /dev/null
sleep 1
docker events --since 1m --until "$(date +%s)" --filter container=short-lived --format '{{.Type}} {{.Action}}'
```

```text
container create
container attach
container start
container die
container destroy
```

Every event carries attributes: for `die`, the exit code:

<!-- test: contains=exitCode=7; output -->
```bash
docker run --rm --name exits-seven alpine:3.23 sh -c 'exit 7' || true
sleep 1
docker events --since 1m --until "$(date +%s)" --filter container=exits-seven --filter event=die \
  --format '{{.Actor.Attributes.name}} {{.Action}} exitCode={{.Actor.Attributes.exitCode}}'
```

```text
exits-seven die exitCode=7
```

## Command breakdown

| Command / option | What it does |
|---|---|
| `docker events` | stream new events until Ctrl+C |
| `--since 10m` / `--since 2026-10-05T10:00:00` | start from a moment in the past |
| `--until "$(date +%s)"` | stop at that moment (then exit) |
| `--filter container=NAME` | one container (also `image=`, `network=`, `volume=`, `type=container`) |
| `--filter event=die` | one action (`create`, `start`, `die`, `oom`, `kill`, `health_status`, `destroy`, …) |
| `--format '{{.Action}} {{.Actor.Attributes.exitCode}}'` | chosen fields; `{{json .}}` shows them all |

## Hands-on lab

**Instructions.** Create a network and a volume, remove both, and list the events of type `network` and `volume` from
the last minute.

**Expected result.** `network create`, `network destroy`, `volume create`, `volume destroy` (in time order).

**Verification.**

<!-- test: contains=network create; contains=volume destroy -->
```bash
docker network create lab-net > /dev/null && docker network rm lab-net > /dev/null
docker volume create lab-vol > /dev/null && docker volume rm lab-vol > /dev/null
sleep 1
docker events --since 1m --until "$(date +%s)" --filter type=network --filter type=volume --format '{{.Type}} {{.Action}}'
```

## Break it

A service needs a database address and crashes without one. It runs with a restart policy, so it "keeps restarting":

<!-- test: contains=started api -->
```bash
docker run -d --name api --restart on-failure:3 alpine:3.23 \
  sh -c 'test -n "$DB_URL" || { echo "DB_URL is not set" >&2; exit 3; }; echo "connected to $DB_URL"; sleep 300' > /dev/null && echo "started api"
```

<!-- test: retry=15; contains=Exited (3); output -->
```bash
docker ps -a --filter name=api --format '{{.Names}}: {{.Status}}'
```

```text
api: Exited (3) Less than a second ago
```

## Troubleshoot it

`docker ps` shows only the current state. The events show the history: how often it died, and with which exit code:

<!-- test: contains=exitCode=3; output -->
```bash
id=$(docker inspect --format '{{.Id}}' api)
docker events --since 5m --until "$(date +%s)" --filter container="$id" --filter event=die \
  --format '{{.Action}} exitCode={{.Actor.Attributes.exitCode}}'
docker inspect --format 'restarts={{.RestartCount}}' api
```

```text
die exitCode=3
die exitCode=3
die exitCode=3
die exitCode=3
restarts=3
```

Four runs (the first start plus three restarts of `on-failure:3`), each ending with exit code 3. The filter uses the
container's ID rather than its name: names are reused, and the events of an earlier container called `api` would be
mixed in. The exit code comes from the application itself, so its logs explain it:

<!-- test: contains=DB_URL is not set; output -->
```bash
docker logs api 2>&1 | sort | uniq -c
```

```text
      4 DB_URL is not set
```

## Fix it

Give the service its configuration (lesson 059):

<!-- test: contains=started api -->
```bash
docker rm -f api > /dev/null
docker run -d --name api --restart on-failure:3 -e DB_URL=postgres://db:5432/cafe alpine:3.23 \
  sh -c 'test -n "$DB_URL" || { echo "DB_URL is not set" >&2; exit 3; }; echo "connected to $DB_URL"; sleep 300' > /dev/null && echo "started api"
```

<!-- test: retry=5; contains=connected to postgres://db:5432/cafe; contains=restarts=0 -->
```bash
docker logs api
docker inspect --format 'restarts={{.RestartCount}}' api
```

## Practice challenge

Watch events **live** while they happen: stream the events of a container named `watched` for 8 seconds, while a
background job starts it and stops it. (`--until` with a time in the future makes the live stream end by itself.)

<details>
<summary>Solution</summary>

<!-- test: contains=container start; contains=container stop; output -->
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

</details>

## Real-world example

Monitoring agents (for example the Datadog or Prometheus exporters) subscribe to the event stream and turn `die`,
`oom` and `health_status: unhealthy` events into alerts: "container `api` restarted 4 times in 2 minutes, exit
code 3". During an incident review, `docker events --since … --until …` replays exactly what the engine did and when,
which `docker ps` cannot.

## Recap

- The engine emits an event for every change: create, start, die, oom, kill, health_status, destroy, …
- `--since` / `--until` replay a window; without `--until`, the command streams forever.
- Filter by `container=`, `type=`, `event=`; read attributes such as `exitCode` with `--format`.
- Restart loops: count `die` events, read the exit code, then the logs.

## Cleanup

<!-- test -->
```bash
docker rm -f api watched > /dev/null 2>&1 || true
```

Next: [Lesson 097 · CPU limits](../../15-resources/097-cpu-limits/README.md)
