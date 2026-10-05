# Module 02 assessment · Containers

> Lessons [006](006-first-container/README.md)–[016](016-inspecting-containers/README.md) · ⏱ 45 minutes · try every
> question before opening its answer

## Knowledge check

**1. `docker run hello-world` worked, but `docker ps` shows nothing. Where is the container?**

<details><summary>Answer</summary>

It ran its command and exited. `docker ps` lists running containers only; `docker ps -a` shows it as `Exited (0)`
(lessons 006, 008).

</details>

**2. Three containers run from one image and each writes a file. How many copies of the image's files exist?**

<details><summary>Answer</summary>

One. The image's layers are shared and read-only; each container has only its own thin writable layer with its
changes (lesson 007).

</details>

**3. What does `docker stop` do, and what does exit code 137 mean?**

<details><summary>Answer</summary>

It sends `SIGTERM`, waits for the grace period (`-t`), then sends `SIGKILL`. 137 = 128 + 9: the process was killed by
`SIGKILL`, it did not exit by itself (lesson 009).

</details>

**4. Which filter lists stopped containers: `status=stopped` or `status=exited`?**

<details><summary>Answer</summary>

`status=exited`. `stopped` is not a valid state, and the error lists the valid ones (lesson 008).

</details>

**5. `docker ps` shows `80/tcp` in the PORTS column. Can you open the server from your browser?**

<details><summary>Answer</summary>

No. `80/tcp` is a port the image declares. Only a mapping such as `0.0.0.0:8080->80/tcp`, created with `-p`, is
reachable from the host (lessons 011, 012).

</details>

**6. What is the difference between `-p 8080:80` and `-p 127.0.0.1:8080:80`?**

<details><summary>Answer</summary>

The first listens on every interface of the host, so other machines can connect; the second only on the loopback
interface, reachable from the same machine only (lesson 012).

</details>

**7. An application writes its log to `/var/log/app.log`. Why does `docker logs` show nothing?**

<details><summary>Answer</summary>

Docker only captures the main process's stdout and stderr. The application must log to stdout/stderr, or the file must
be a link to `/dev/stdout` (lesson 014).

</details>

**8. `docker exec web bash` fails with `executable file not found`. What do you try next?**

<details><summary>Answer</summary>

`docker exec -it web sh`: small images do not contain Bash. `exec` can only run programs that exist in the image
(lesson 015).

</details>

**9. Which fields of `docker inspect` explain why a container stopped?**

<details><summary>Answer</summary>

`.State.ExitCode`, `.State.OOMKilled`, `.State.Error`, `.State.FinishedAt`, and `.RestartCount`; then read the
application's message with `docker logs` (lesson 016).

</details>

## Practical task

Run an Nginx website named `shop` that:

- serves the page `<h1>Shop</h1>` on <http://localhost:8085>, reachable from this computer only,
- has the label `team=web`,
- is restarted automatically unless you stop it.

Then prove each requirement with a command.

<details><summary>Solution</summary>

<!-- test -->
```bash
docker run -d --name shop -p 127.0.0.1:8085:80 --label team=web --restart unless-stopped nginx:1.30-alpine
docker exec shop sh -c 'echo "<h1>Shop</h1>" > /usr/share/nginx/html/index.html'
```

<!-- test: contains=<h1>Shop</h1>; contains=127.0.0.1:8085; contains=unless-stopped; retry=10; output -->
```bash
curl -s http://localhost:8085
docker port shop
docker ps --filter label=team=web --format '{{.Names}} has the label team=web'
docker inspect --format 'restart policy: {{.HostConfig.RestartPolicy.Name}}' shop
```

```text
<h1>Shop</h1>
80/tcp -> 127.0.0.1:8085
shop has the label team=web
restart policy: unless-stopped
```

</details>

## Troubleshooting task

A colleague's worker container "does not work". Reproduce it:

<!-- test -->
```bash
docker run -d --name worker alpine:3.23 sh -c 'echo "reading queue $QUEUE_NAME"; [ -n "$QUEUE_NAME" ] || exit 2; sleep 300'
```

Find out what happened, fix it, and verify the fix.

<details><summary>Solution</summary>

Status and exit code first, then the log and the configuration:

<!-- test: contains=exit code 2; contains=reading queue; output -->
```bash
sleep 1
docker ps -a --filter name=^worker$ --format '{{.Names}}: {{.Status}}'
docker inspect --format 'exit code {{.State.ExitCode}}, OOM killed {{.State.OOMKilled}}' worker
docker logs worker
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' worker
```

```text
worker: Exited (2) 1 second ago
exit code 2, OOM killed false
reading queue 
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

The worker exited by itself with code 2 (not killed, not out of memory); its log shows an empty queue name
(`reading queue ` followed by nothing), and its environment has no `QUEUE_NAME`. Recreate it with the variable:

<!-- test: contains=reading queue orders; contains=Up; retry=5 -->
```bash
docker rm -f worker > /dev/null
docker run -d --name worker -e QUEUE_NAME=orders alpine:3.23 sh -c 'echo "reading queue $QUEUE_NAME"; [ -n "$QUEUE_NAME" ] || exit 2; sleep 300' > /dev/null 2>&1 || true
sleep 1
docker ps --filter name=^worker$ --format '{{.Status}}'
docker logs worker
```

</details>

## Real-world scenario

Your team's staging server has 60 containers in `docker ps -a`, most of them `Exited`, and the disk is filling up.
Nobody knows which ones are still needed. What do you do?

<details><summary>Model answer</summary>

Do not delete blindly. List what is there with useful columns: `docker ps -a --format 'table
{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Labels}}'` and the sizes with `docker ps -a -s` (lesson 008). Running
containers and those with a restart policy are in use. Exited containers from one-off runs (migrations, test jobs) can
go: remove them by filter (`docker rm $(docker ps -aq --filter status=exited --filter label=…)`, guarded against an
empty list, lesson 013), after checking with the owners. Then prevent it: one-off jobs with `docker run --rm`,
services with names and labels per project, and Compose to manage each system as one unit (module 10).

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f shop worker > /dev/null
```
