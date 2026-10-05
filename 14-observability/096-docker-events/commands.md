<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 096 · docker events · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run --name short-lived alpine:3.23 sh -c 'exit 0'
docker rm short-lived > /dev/null
sleep 1
docker events --since 1m --until "$(date +%s)" --filter container=short-lived --format '{{.Type}} {{.Action}}'
```

```bash
docker run --rm --name exits-seven alpine:3.23 sh -c 'exit 7' || true
sleep 1
docker events --since 1m --until "$(date +%s)" --filter container=exits-seven --filter event=die \
  --format '{{.Actor.Attributes.name}} {{.Action}} exitCode={{.Actor.Attributes.exitCode}}'
```

## Hands-on lab

```bash
docker network create lab-net > /dev/null && docker network rm lab-net > /dev/null
docker volume create lab-vol > /dev/null && docker volume rm lab-vol > /dev/null
sleep 1
docker events --since 1m --until "$(date +%s)" --filter type=network --filter type=volume --format '{{.Type}} {{.Action}}'
```

## Break it

```bash
docker run -d --name api --restart on-failure:3 alpine:3.23 \
  sh -c 'test -n "$DB_URL" || { echo "DB_URL is not set" >&2; exit 3; }; echo "connected to $DB_URL"; sleep 300' > /dev/null && echo "started api"
```

```bash
docker ps -a --filter name=api --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

```bash
id=$(docker inspect --format '{{.Id}}' api)
docker events --since 5m --until "$(date +%s)" --filter container="$id" --filter event=die \
  --format '{{.Action}} exitCode={{.Actor.Attributes.exitCode}}'
docker inspect --format 'restarts={{.RestartCount}}' api
```

```bash
docker logs api 2>&1 | sort | uniq -c
```

## Fix it

```bash
docker rm -f api > /dev/null
docker run -d --name api --restart on-failure:3 -e DB_URL=postgres://db:5432/cafe alpine:3.23 \
  sh -c 'test -n "$DB_URL" || { echo "DB_URL is not set" >&2; exit 3; }; echo "connected to $DB_URL"; sleep 300' > /dev/null && echo "started api"
```

```bash
docker logs api
docker inspect --format 'restarts={{.RestartCount}}' api
```

## Practice challenge

```bash
( sleep 2; docker run -d --name watched alpine:3.23 sleep 300; docker stop -t 1 watched ) > /dev/null &
docker events --filter type=container --filter container=watched --until "$(( $(date +%s) + 8 ))" --format '{{.Type}} {{.Action}}'
```

## Cleanup

```bash
docker rm -f api watched > /dev/null 2>&1 || true
```
