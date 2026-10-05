<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 096 · docker events · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A service needs a database address and crashes without one. It runs with a restart policy, so it "keeps restarting":

```bash
docker run -d --name api --restart on-failure:3 alpine:3.23 \
  sh -c 'test -n "$DB_URL" || { echo "DB_URL is not set" >&2; exit 3; }; echo "connected to $DB_URL"; sleep 300' > /dev/null && echo "started api"
```

```bash
docker ps -a --filter name=api --format '{{.Names}}: {{.Status}}'
```

```text
api: Exited (3) Less than a second ago
```

## Troubleshoot it

`docker ps` shows only the current state. The events show the history: how often it died, and with which exit code:

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

```bash
docker logs api 2>&1 | sort | uniq -c
```

```text
      4 DB_URL is not set
```

## Fix it

Give the service its configuration (lesson 059):

```bash
docker rm -f api > /dev/null
docker run -d --name api --restart on-failure:3 -e DB_URL=postgres://db:5432/cafe alpine:3.23 \
  sh -c 'test -n "$DB_URL" || { echo "DB_URL is not set" >&2; exit 3; }; echo "connected to $DB_URL"; sleep 300' > /dev/null && echo "started api"
```

```bash
docker logs api
docker inspect --format 'restarts={{.RestartCount}}' api
```
