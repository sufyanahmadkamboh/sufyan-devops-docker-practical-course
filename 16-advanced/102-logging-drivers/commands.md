<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 102 · Logging drivers · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker info --format 'default logging driver: {{.LoggingDriver}}'
```

```bash
docker run -d --name chatty alpine:3.23 sh -c 'pad=$(printf "%0100d" 0); i=0; while [ $i -lt 50000 ]; do i=$((i+1)); echo "line $i $pad"; done; sleep 300' > /dev/null
docker inspect --format '{{.HostConfig.LogConfig.Type}} {{json .HostConfig.LogConfig.Config}}' chatty
```

```bash
sleep 3
echo "$(docker logs chatty 2>&1 | wc -l) lines so far"
docker inspect --format '{{.LogPath}}' chatty
```

## Hands-on lab

```bash
docker run -d --name rotated --log-opt max-size=1m --log-opt max-file=3 alpine:3.23 \
  sh -c 'pad=$(printf "%0100d" 0); i=0; while [ $i -lt 50000 ]; do i=$((i+1)); echo "line $i $pad"; done; sleep 300' > /dev/null
sleep 5
echo "rotated: $(docker logs rotated 2>&1 | wc -l) lines kept (first kept: $(docker logs rotated 2>&1 | head -1))"
echo "chatty:  $(docker logs chatty 2>&1 | wc -l) lines kept"
docker inspect --format '{{json .HostConfig.LogConfig.Config}}' rotated
```

## Break it

```bash
docker run -d --name quiet --log-driver none nginx:1.30-alpine > /dev/null && echo "started quiet"
```

```bash
docker logs quiet 2>&1
```

## Troubleshoot it

```bash
docker inspect --format '{{.HostConfig.LogConfig.Type}}' quiet
```

## Fix it

```bash
docker rm -f quiet > /dev/null
docker run -d --name quiet --log-driver local --log-opt max-size=10m --log-opt max-file=3 nginx:1.30-alpine > /dev/null
docker inspect --format '{{.HostConfig.LogConfig.Type}} {{json .HostConfig.LogConfig.Config}}' quiet
```

```bash
docker logs quiet 2>&1 | grep 'Configuration complete'
```

```bash
{
  "log-driver": "local",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```

## Practice challenge

```bash
docker ps -q | xargs docker inspect --format \
  '{{.Name}} {{.HostConfig.LogConfig.Type}} {{with index .HostConfig.LogConfig.Config "max-size"}}{{.}}{{else}}unlimited{{end}}'
```

## Cleanup

```bash
docker rm -f chatty rotated quiet > /dev/null 2>&1 || true
```
