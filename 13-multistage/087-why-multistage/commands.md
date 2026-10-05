<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 087 · Why multi-stage builds? · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-087 examples/go-api
cp 13-multistage/087-why-multistage/examples/Dockerfile* ~/docker-practice/lesson-087/
cd ~/docker-practice/lesson-087
ls
cat Dockerfile
```

## Demonstration

```bash
docker build -q -f Dockerfile.single -t go-single:1.0 . > /dev/null
docker build -q -t go-multi:1.0 . > /dev/null
docker image ls --filter 'reference=go-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

```bash
docker run -d --name go-multi -p 8089:8080 go-multi:1.0 > /dev/null
docker ps --filter name=go-multi --format '{{.Names}}: {{.Status}}'
```

```bash
curl -s http://localhost:8089/
```

```bash
docker run --rm go-single:1.0 go version
docker run --rm go-multi:1.0 sh -c 'go version' 2>&1 || true
```

## Hands-on lab

```bash
docker build -q --target build -t go-multi:build . > /dev/null
docker run --rm go-multi:build ls -l /out/go-api /src
docker image ls --filter 'reference=go-multi' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

## Break it

```bash
grep 'COPY --from' Dockerfile.broken
docker build -f Dockerfile.broken -t go-multi:broken . 2>&1 | grep ERROR | head -1
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
docker build -q -f Dockerfile.broken --target build -t go-multi:debug . > /dev/null
docker run --rm go-multi:debug sh -c 'ls /src; find / -name go-api -type f 2>/dev/null'
```

## Fix it

```bash
diff Dockerfile.broken Dockerfile || true
docker build -q -t go-multi:fixed . > /dev/null && grep 'COPY --from' Dockerfile
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-087
{ sed -n '1,/^RUN CGO_ENABLED/p' Dockerfile
  printf '\n# a test stage: never shipped, built only with --target test\nFROM build AS test\nRUN go vet ./... && echo "vet passed"\n'
  sed -n '/^# stage 2/,$p' Dockerfile
} > Dockerfile.test
grep -E '^FROM' Dockerfile.test
docker build --progress=plain --no-cache-filter test --target test -f Dockerfile.test -t go-multi:test . 2>&1 | grep -o 'vet passed' | head -1
```

## Cleanup

```bash
docker rm -f go-multi > /dev/null
docker image rm -f go-single:1.0 go-multi:1.0 go-multi:build go-multi:debug go-multi:fixed go-multi:test > /dev/null 2>&1 || true
rm -rf ~/docker-practice/lesson-087
```
