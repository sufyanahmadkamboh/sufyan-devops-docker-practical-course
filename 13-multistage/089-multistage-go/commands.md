<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 089 · Multi-stage builds for Go · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-089 examples/go-api
cp 13-multistage/089-multistage-go/examples/Dockerfile* ~/docker-practice/lesson-089/
cd ~/docker-practice/lesson-089
cat Dockerfile
```

## Demonstration

```bash
docker build -q -t go-distroless:1.0 . > /dev/null
docker image ls go-distroless
```

```bash
docker run -d --name go-distroless -p 8091:8080 go-distroless:1.0 > /dev/null
docker ps --filter name=go-distroless --format '{{.Names}}: {{.Status}}'
```

```bash
curl -s http://localhost:8091/
```

```bash
docker image inspect --format 'user={{.Config.User}} entrypoint={{.Config.Entrypoint}}' go-distroless:1.0
```

```bash
docker exec go-distroless sh 2>&1
```

## Hands-on lab

```bash
docker build -q --target build -t go-distroless:build . > /dev/null
docker run --rm go-distroless:build sh -c 'CGO_ENABLED=0 go build -o /tmp/go-api-full . && ls -l /out/go-api /tmp/go-api-full'
```

## Break it

```bash
docker build -q -f Dockerfile.broken -t go-distroless:broken . > /dev/null 2>&1
docker run -d --name go-broken go-distroless:broken 2>&1
```

## Troubleshoot it

```bash
docker image inspect --format '{{json .Config.Entrypoint}}' go-distroless:broken
```

## Fix it

```bash
docker rm -f go-broken > /dev/null 2>&1 || true
docker build -q -t go-distroless:fixed . > /dev/null
docker image inspect --format '{{json .Config.Entrypoint}}' go-distroless:fixed
```

## Practice challenge

```bash
docker run --rm --network container:go-distroless busybox:1.37 wget -qO- http://localhost:8080/health
```

## Cleanup

```bash
docker rm -f go-distroless go-broken > /dev/null 2>&1 || true
docker image rm -f go-distroless:1.0 go-distroless:build go-distroless:broken go-distroless:fixed > /dev/null 2>&1 || true
rm -rf ~/docker-practice/lesson-089
```
