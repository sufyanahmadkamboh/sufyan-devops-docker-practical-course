# Module 17 · Troubleshooting

> 25 problems · about 400 minutes · all levels · run every command from the course folder

Every problem here is reproduced for real on your computer, then worked through the way you would at work:
**problem → symptoms → investigation → commands → output interpretation → root cause → fix → verification →
prevention.** Start from the symptom you see.

## The method

```text
 1. What state is it in?          docker ps -a                     Up? Exited (CODE)? Created? (unhealthy)?
          │
 2. What did it say?              docker logs NAME                 the application's own error
          │
 3. How is it configured?         docker inspect NAME              command, env, ports, mounts, networks, user, limits
          │
 4. What does it see from inside? docker exec NAME …               files, processes, DNS, the app on localhost
          │                       docker run --rm --network container:NAME busybox:1.37 netstat -tln
 5. What happened over time?      docker events --since 10m        die, oom, kill, health_status
          │
 6. Is it starved?                docker stats --no-stream         CPU % against its limit, memory usage / limit
          │
 7. Change one thing, verify, and write down the prevention.
```

| Command | Answers |
|---|---|
| `docker ps -a --format '{{.Names}}: {{.Status}}'` | is it running, how did it end, is it healthy |
| `docker logs NAME 2>&1 \| tail` | what the process printed, also after it stopped |
| `docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.Error}}' NAME` | why it stopped |
| `docker inspect --format '{{json .Config}}' NAME` | the command, environment, user and ports it really got |
| `docker inspect --format '{{json .Mounts}}' NAME` | which volumes and folders are mounted where |
| `docker exec NAME sh` | look around inside a running container |
| `docker events --since 10m --filter container=NAME` | the container's history: start, die, oom, health |
| `docker stats --no-stream` | live CPU and memory use against the limits |

**Exit codes:** `0` the main process finished · `1` (or another small number) the application failed · `125` Docker
could not create or start it · `126` the command is not executable · `127` the command was not found · `137` killed
(`SIGKILL`: out of memory or `docker kill`) · `143` stopped with `SIGTERM`.

## Problems by symptom

| Symptom | Problem |
|---|---|
| `Exited (0)` right after `docker run -d`, clean logs | [01 · Container exits immediately](01-container-exits-immediately/README.md) |
| `executable file not found in $PATH`, status `Created`, exit 127 | [02 · Wrong command](02-wrong-command/README.md) |
| it runs, but the old version | [03 · Wrong image](03-wrong-image/README.md) |
| `port is already allocated` | [04 · Port already in use](04-port-already-in-use/README.md) |
| `curl: (7)` connection refused / could not connect | [05 · Application not reachable](05-application-not-reachable/README.md) |
| `curl: (52) Empty reply`, works inside the container | [06 · Listening on localhost](06-listening-on-localhost/README.md) |
| `curl: (52) Empty reply`, image `EXPOSE`s another port | [07 · Wrong container port](07-wrong-container-port/README.md) |
| `Name does not resolve` / `Try again` between networks | [08 · Wrong network](08-wrong-network/README.md) |
| a container name does not resolve, its IP works | [09 · DNS failure](09-dns-failure/README.md) |
| `Connection refused` / `password authentication failed` to the database | [10 · Database connection failure](10-database-connection-failure/README.md) |
| `KeyError`, `undefined`, `null` for configuration, exit 1 | [11 · Missing environment variable](11-missing-environment-variable/README.md) |
| `Permission denied` reading a file, non-root user | [12 · Permission denied](12-permission-denied/README.md) |
| `Permission denied` / `Read-only file system` writing | [13 · Cannot write files](13-cannot-write-files/README.md) |
| data gone after recreating, volume empty | [14 · Volume not mounted](14-volume-not-mounted/README.md) |
| database empty after recreating, no volume given | [15 · Data disappeared](15-data-disappeared/README.md) |
| `COPY` fails with `not found` although the file exists | [16 · Build failure](16-build-failure/README.md) |
| a rebuild still contains old content, `CACHED` | [17 · Unexpected cache](17-unexpected-cache/README.md) |
| hundreds of MB for a small application | [18 · Huge image](18-huge-image/README.md) |
| a token readable with `docker history` | [19 · Dockerfile security issue](19-dockerfile-security-issue/README.md) |
| `uid=0(root)` in the container | [20 · Running as root](20-running-as-root/README.md) |
| `(unhealthy)` although the app answers | [21 · Healthcheck failure](21-healthcheck-failure/README.md) |
| `Exited (137)`, `OOMKilled: true`, no logs | [22 · Memory limit exceeded](22-memory-limit-exceeded/README.md) |
| slow, no errors, `nr_throttled` growing | [23 · CPU throttling](23-cpu-throttling/README.md) |
| `no basic auth credentials`, `401 Unauthorized` | [24 · Registry authentication failure](24-registry-authentication-failure/README.md) |
| `pull access denied`, `manifest unknown`, `429 Too Many Requests` | [25 · Image pull failure](25-image-pull-failure/README.md) |

## How to work through a problem

1. Run the **Symptoms** commands and look at the real output before reading further: what would you check first?
2. Follow the **Investigation**; every step is one question and one command.
3. Apply the **Fix**, run the **Verification**, and read the **Prevention**: that is what stops it from happening
   again.
4. Run the **Cleanup**. Every problem also starts from scratch, so you can repeat it.

Next: [Module 18 · Production](../18-production/130-production-dockerfile/README.md)
