<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 042 · Containerizing a Go application · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-042 examples/go-api
cp 06-application-containerization/042-containerize-go/examples/Dockerfile* ~/docker-practice/lesson-042/
cd ~/docker-practice/lesson-042
ls
```

## Demonstration

```bash
docker build -q -t go-api:1.0 . > /dev/null
docker image ls go-api
docker run -d --name go-api -p 8085:8080 go-api:1.0 > /dev/null
```

```bash
curl -s http://localhost:8085/
```

```bash
docker run --rm go-api:1.0 ls -lh /usr/local/bin/go-api
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-042
docker create --name go-extract go-api:1.0 > /dev/null
docker cp go-extract:/usr/local/bin/go-api ./go-api-binary
docker rm go-extract > /dev/null
docker run -d --name go-plain -v "$(pwd)/go-api-binary:/go-api" alpine:3.23 /go-api > /dev/null
sleep 1
docker logs go-plain 2>&1
docker rm -f go-plain > /dev/null
```

## Break it

```bash
docker build -f Dockerfile.broken -t go-api:broken . 2>&1 | grep -E 'go: |ERROR' | head -2
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
grep COPY Dockerfile.broken
ls
```

## Fix it

```bash
docker build -q -t go-api:fixed . > /dev/null
docker run --rm -d --name go-fixed -p 8086:8080 go-api:fixed > /dev/null
sleep 1
curl -s http://localhost:8086/
docker rm -f go-fixed > /dev/null
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-042
docker run --rm -v "$(pwd):/src" -w /src -e CGO_ENABLED=0 -e GOOS=linux -e GOARCH=arm64 golang:1.26-alpine go build -o go-api-arm64 .
docker run --rm -v "$(pwd):/src" -w /src golang:1.26-alpine go version -m go-api-arm64 | grep GOARCH
```

## Cleanup

```bash
docker rm -f go-api > /dev/null
docker image rm -f go-api:1.0 go-api:fixed > /dev/null
rm -rf ~/docker-practice/lesson-042
```
