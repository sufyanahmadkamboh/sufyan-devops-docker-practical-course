<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 016 · Inspecting containers · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A new service is deployed, and stops shortly after starting:

```bash
docker run -d --name api alpine:3.23 sh -c '
  [ -n "$DB_URL" ] || { echo "fatal: DB_URL is not set" >&2; exit 3; }
  echo "connecting to $DB_URL"; sleep 300' > /dev/null
sleep 1
docker ps -a --filter name=^api$ --format '{{.Names}}: {{.Status}}'
```

```text
api: Exited (3) 1 second ago
```

## Troubleshoot it

Ask Docker how it ended. `ExitCode 3` means the application chose to exit (a crash by a signal would be 128 + n, like
137); `OOMKilled false` rules out memory:

```bash
docker inspect --format 'exit code {{.State.ExitCode}}, OOM killed {{.State.OOMKilled}}, error "{{.State.Error}}", ran from {{.State.StartedAt}} to {{.State.FinishedAt}}' api
```

```text
exit code 3, OOM killed false, error "", ran from 2026-10-05T10:49:23.602362905Z to 2026-10-05T10:49:23.746326719Z
```

The application's own message is in its log, and its configuration in `inspect`:

```bash
docker logs api
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' api
```

```text
fatal: DB_URL is not set
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

Root cause: the container received no `DB_URL` (only `PATH`). Investigation order for any stopped container: **status
and exit code** (`inspect`) → **the application's message** (`logs`) → **the configuration it got** (`inspect`).

## Fix it

Recreate the container with the variable (lesson 059 covers configuration in depth):

```bash
docker rm -f api > /dev/null
docker run -d --name api -e DB_URL=postgres://db:5432/shop alpine:3.23 sh -c '
  [ -n "$DB_URL" ] || { echo "fatal: DB_URL is not set" >&2; exit 3; }
  echo "connecting to $DB_URL"; sleep 300' > /dev/null 2>&1 || true
sleep 1
docker ps --filter name=^api$ --format '{{.Names}}: {{.Status}}'
docker logs api
```
