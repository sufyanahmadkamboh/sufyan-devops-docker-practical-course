<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 100 · Metadata and docker inspect · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker network create shop-net > /dev/null
docker volume create shop-data > /dev/null
docker run -d --name web --network shop-net -p 8080:80 -v shop-data:/data -e APP_ENV=staging --memory 128m \
  nginx:1.30-alpine > /dev/null && echo "started web"
```

## Demonstration

```bash
docker container inspect web | grep -E '^        "[A-Za-z]+": ' | cut -d'"' -f2 | tr '\n' ' '; echo
```

```bash
docker inspect --format 'status={{.State.Status}} started={{.State.StartedAt}}' web
docker inspect --format 'image={{.Config.Image}} memory={{.HostConfig.Memory}}' web
```

```bash
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' web | grep APP_ENV
docker inspect --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{$net.IPAddress}}{{end}}' web
docker inspect --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}' web
docker inspect --format '{{json .NetworkSettings.Ports}}' web
docker inspect --format '{{(index (index .NetworkSettings.Ports "80/tcp") 0).HostPort}}' web
```

```bash
docker image inspect --format 'Cmd={{json .Config.Cmd}} Exposed={{json .Config.ExposedPorts}} Layers={{len .RootFS.Layers}}' nginx:1.30-alpine
```

## Hands-on lab

```bash
docker inspect --format 'restart={{.HostConfig.RestartPolicy.Name}} memory={{.HostConfig.Memory}} port={{(index (index .NetworkSettings.Ports "80/tcp") 0).HostPort}}' web
```

## Break it

```bash
docker inspect --format '{{.State.Status}}' nginx:1.30-alpine 2>&1
```

## Troubleshoot it

```bash
docker image inspect nginx:1.30-alpine | grep -E '^        "[A-Za-z]+": ' | cut -d'"' -f2 | tr '\n' ' '; echo
```

## Fix it

```bash
docker container inspect --format '{{.State.Status}}' web
docker image inspect --format '{{.Os}}/{{.Architecture}}' nginx:1.30-alpine
```

## Practice challenge

```bash
docker ps -q | xargs docker inspect --format \
  '{{.Name}} user={{if .Config.User}}{{.Config.User}}{{else}}root{{end}} privileged={{.HostConfig.Privileged}} memory={{.HostConfig.Memory}} readonly={{.HostConfig.ReadonlyRootfs}}'
```

## Cleanup

```bash
docker rm -f web > /dev/null 2>&1 || true
docker volume rm shop-data > /dev/null 2>&1 || true
docker network rm shop-net > /dev/null 2>&1 || true
```
