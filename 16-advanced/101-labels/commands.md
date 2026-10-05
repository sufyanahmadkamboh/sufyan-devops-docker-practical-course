<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 101 · Labels · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-101 16-advanced/101-labels/examples
cd ~/docker-practice/lesson-101
cat Dockerfile
```

## Demonstration

```bash
docker build -q --build-arg VERSION=1.4.0 --build-arg REVISION=3f2c1ab -t cafe-web:1.4.0 . > /dev/null
docker image ls cafe-web --format '{{.Repository}}:{{.Tag}}'
```

```bash
docker image inspect --format '{{range $k, $v := .Config.Labels}}{{$k}}={{$v}}{{println}}{{end}}' cafe-web:1.4.0 | grep '^org.opencontainers'
```

```bash
docker run -d --name pay-web --label team=payments --label env=staging cafe-web:1.4.0 > /dev/null
docker run -d --name pay-api --label team=payments --label env=test alpine:3.23 sleep 300 > /dev/null
docker run -d --name shop-web --label team=shop --label env=staging cafe-web:1.4.0 > /dev/null
docker ps --filter label=team=payments --format '{{.Names}} {{.Label "env"}}'
```

## Hands-on lab

```bash
docker ps --filter label=env=staging --format '{{.Names}} {{.Label "team"}}'
```

## Break it

```bash
found=$(docker ps -q --filter label=Team=payments --filter label=env=test)
[ -n "$found" ] && docker rm -f $found || echo "nothing to remove"
```

## Troubleshoot it

```bash
docker inspect --format '{{json .Config.Labels}}' pay-api
```

## Fix it

```bash
docker ps --filter label=team=payments --filter label=env=test --format '{{.Names}}'
docker container rm -f $(docker ps -q --filter label=team=payments --filter label=env=test) > /dev/null && echo "removed"
```

## Practice challenge

```bash
docker image ls --filter label=org.opencontainers.image.version --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>' |
  while read -r image; do
    echo "$image version=$(docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.version"}}' "$image")"
  done
```

## Cleanup

```bash
docker rm -f pay-web pay-api shop-web > /dev/null 2>&1 || true
docker image rm -f cafe-web:1.4.0 > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-101
```
