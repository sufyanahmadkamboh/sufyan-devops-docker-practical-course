# Module 14 assessment · Observability

> Lessons [092](092-healthcheck/README.md)–[096](096-docker-events/README.md) · ⏱ 40 minutes · try every question
> before opening its answer

## Knowledge check

**1. Where does a `HEALTHCHECK` command run, and what decides healthy or unhealthy?**

<details><summary>Answer</summary>

Inside the container, every `--interval`. Exit status 0 = success; after `--retries` failures in a row the status is
`unhealthy` (lesson 092).

</details>

**2. A health check uses `http://127.0.0.1:8082/` because the container was started with `-p 8082:80`. What happens?**

<details><summary>Answer</summary>

It fails: inside the container the application listens on port 80. The published host port 8082 does not exist inside
the container (lesson 092).

</details>

**3. A container is `unhealthy` and has `--restart always`. Does Docker restart it?**

<details><summary>Answer</summary>

No. Restart policies act only when the main process exits. Restarting unhealthy containers is the job of an
orchestrator, a monitoring system, or a script (lesson 093).

</details>

**4. A Python worker's `print` lines do not appear in `docker logs`, but its errors do. Why, and what is the fix?**

<details><summary>Answer</summary>

stdout is not a terminal, so Python buffers it; stderr is written line by line. Set `PYTHONUNBUFFERED=1` (or run
`python -u`) (lesson 094).

</details>

**5. How do you print only what a container wrote to stderr?**

<details><summary>Answer</summary>

`docker logs NAME 2>&1 >/dev/null` (lesson 094).

</details>

**6. What does `CPU %` = 200% mean in `docker stats`?**

<details><summary>Answer</summary>

The container used two full CPU cores' worth of time during the measurement (100% = one core) (lesson 095).

</details>

**7. How do you replay what happened to a container in the last 10 minutes and then exit?**

<details><summary>Answer</summary>

`docker events --since 10m --until "$(date +%s)" --filter container=NAME` (lesson 096).

</details>

**8. Which event attribute tells you why a container stopped?**

<details><summary>Answer</summary>

`exitCode` of the `die` event (`--format '{{.Actor.Attributes.exitCode}}'`); an `oom` event before it means the
kernel killed it for memory (lessons 096, 099).

</details>

## Practical task

Start a Redis container named `store` from `redis:8-alpine` with a health check that runs `redis-cli ping` every
2 seconds, wait until it is healthy, and show the output of its last health check and its CPU and memory usage.

<details><summary>Solution</summary>

<!-- test: contains=started store -->
```bash
docker run -d --name store --health-cmd 'redis-cli ping | grep -q PONG' --health-interval 2s --health-retries 3 \
  redis:8-alpine > /dev/null && echo "started store"
```

<!-- test: retry=10; contains=healthy; output -->
```bash
docker inspect --format '{{.State.Health.Status}} last exit={{(index .State.Health.Log 0).ExitCode}}' store
docker stats --no-stream --format '{{.Name}} cpu={{.CPUPerc}} mem={{.MemUsage}}' store
```

```text
healthy last exit=0
store cpu=0.29% mem=6.012MiB / 15.35GiB
```

</details>

## Troubleshooting task

A service keeps "restarting". Reproduce it:

<!-- test: contains=started payments -->
```bash
docker run -d --name payments --restart on-failure:2 alpine:3.23 \
  sh -c 'echo "loading config"; test -f /config/payments.yml || { echo "config file missing" >&2; exit 2; }' > /dev/null && echo "started payments"
```

Using only Docker commands, find out how often it ran, how each run ended, and why.

<details><summary>Solution</summary>

<!-- test: retry=15; contains=exitCode=2; contains=restarts=2; output -->
```bash
docker events --since 2m --until "$(date +%s)" --filter container=payments --filter event=die \
  --format '{{.Action}} exitCode={{.Actor.Attributes.exitCode}}'
docker inspect --format 'status={{.State.Status}} restarts={{.RestartCount}}' payments
```

```text
die exitCode=2
die exitCode=2
die exitCode=2
status=exited restarts=2
```

<!-- test: contains=config file missing; output -->
```bash
docker logs payments 2>&1 >/dev/null | sort | uniq -c
```

```text
      3 config file missing
```

Three runs (the first plus two restarts of `on-failure:2`), each ending with exit code 2, because the configuration
file is missing. The fix is to provide `/config/payments.yml` (a bind mount or volume, module 08), not more restarts.

</details>

## Real-world scenario

Users report that the shop is "sometimes slow, sometimes down" since yesterday's release. `docker ps` shows every
container `Up`. Describe how you would investigate with the tools of this module, in order.

<details><summary>Model answer</summary>

1. `docker ps --filter health=unhealthy`: is any container unhealthy although it runs (lesson 093)? Read its last
   checks with `docker inspect --format '{{json .State.Health}}'` (lesson 092).
2. `docker stats --no-stream`, sorted by CPU and memory: is one container at its CPU limit (throttled) or close to its
   memory limit (lesson 095)?
3. `docker events --since 24h --until "$(date +%s)" --filter event=die --filter event=oom`: were containers or their
   worker processes killed and restarted since the release (lessons 096, 099)?
4. `docker logs --since 1h -t` of the suspicious container, stderr first (`2>&1 >/dev/null`), to find the errors and
   the moment they started (lesson 094).

Then compare with the release: which image changed, and what changed in it.

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f store payments > /dev/null 2>&1 || true
```
