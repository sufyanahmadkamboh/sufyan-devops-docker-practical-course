<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 016 · Inspecting containers · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker run -d --name web -p 8080:80 -e APP_ENV=staging --restart unless-stopped nginx:1.30-alpine > /dev/null
docker ps --format '{{.Names}}'
```

## Demonstration

```bash
docker inspect web | grep -E '"(Id|Name|Status|Running|ExitCode|StartedAt|Image)"' | head -12
```

```bash
docker inspect --format 'state: {{.State.Status}}, started: {{.State.StartedAt}}' web
docker inspect --format 'image: {{.Config.Image}}, command: {{json .Config.Cmd}}' web
docker inspect --format 'restart policy: {{.HostConfig.RestartPolicy.Name}}' web
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' web
```

```bash
docker inspect --format '{{json .HostConfig.PortBindings}}' web
docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}}: {{$net.IPAddress}}{{end}}' web
```

## Hands-on lab

```bash
docker inspect --format '{{.Name}} {{.Config.Image}} {{(index (index .HostConfig.PortBindings "80/tcp") 0).HostPort}} {{.HostConfig.RestartPolicy.Name}}' web
```

## Break it

```bash
docker run -d --name api alpine:3.23 sh -c '
  [ -n "$DB_URL" ] || { echo "fatal: DB_URL is not set" >&2; exit 3; }
  echo "connecting to $DB_URL"; sleep 300' > /dev/null
sleep 1
docker ps -a --filter name=^api$ --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

```bash
docker inspect --format 'exit code {{.State.ExitCode}}, OOM killed {{.State.OOMKilled}}, error "{{.State.Error}}", ran from {{.State.StartedAt}} to {{.State.FinishedAt}}' api
```

```bash
docker logs api
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' api
```

## Fix it

```bash
docker rm -f api > /dev/null
docker run -d --name api -e DB_URL=postgres://db:5432/shop alpine:3.23 sh -c '
  [ -n "$DB_URL" ] || { echo "fatal: DB_URL is not set" >&2; exit 3; }
  echo "connecting to $DB_URL"; sleep 300' > /dev/null 2>&1 || true
sleep 1
docker ps --filter name=^api$ --format '{{.Names}}: {{.Status}}'
docker logs api
```

## Practice challenge

```bash
docker inspect --format '{{.Name}} | {{.Config.Image}} | {{.State.Status}} | exit {{.State.ExitCode}} | restarts {{.RestartCount}}' $(docker ps -aq)
```

## Cleanup

```bash
docker rm -f web api > /dev/null
```
