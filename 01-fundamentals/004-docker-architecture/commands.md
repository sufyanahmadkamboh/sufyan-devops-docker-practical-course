<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 004 · Docker architecture · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker version --format 'client {{.Client.Version}} (API {{.Client.APIVersion}}) -> server {{.Server.Version}} (API {{.Server.APIVersion}})'
```

```bash
docker version --format '{{range .Server.Components}}{{.Name}} {{.Version}}{{"\n"}}{{end}}'
```

```bash
docker container create --name demo alpine:3.23 echo "hello from the container" > /dev/null
docker container ls -a --filter name=demo --format '{{.Names}}: {{.Status}}'
docker container start -a demo
docker container ls -a --filter name=demo --format '{{.Names}}: {{.Status}}'
docker container rm demo > /dev/null
```

## Hands-on lab

```bash
docker context ls
docker context show
```

## Break it

```bash
DOCKER_HOST=tcp://127.0.0.1:1 docker version --format '{{.Server.Version}}' 2>&1
```

## Troubleshoot it

```bash
echo "DOCKER_HOST=${DOCKER_HOST:-(not set)}"
echo "context: $(docker context show)"
```

## Fix it

```bash
unset DOCKER_HOST
docker version --format '{{.Server.Version}}' > /dev/null && echo "server is reachable"
```

## Practice challenge

```bash
docker image inspect busybox:1.37 > /dev/null 2>&1 || docker image pull -q busybox:1.37
docker container create --name by-hand busybox:1.37 echo it works > /dev/null
docker container start -a by-hand
docker container rm by-hand > /dev/null
```
