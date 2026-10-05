<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 088 · Multi-stage builds for Node.js · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-088 13-multistage/088-multistage-node/examples/ts-api
cp 13-multistage/088-multistage-node/examples/Dockerfile* ~/docker-practice/lesson-088/
cd ~/docker-practice/lesson-088
cat package.json
```

## Demonstration

```bash
docker build -q -f Dockerfile.single -t ts-single:1.0 . > /dev/null
docker build -q -t ts-multi:1.0 . > /dev/null
docker image ls --filter 'reference=ts-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

```bash
echo "single: $(docker run --rm ts-single:1.0 ls /app /app/node_modules | tr '\n' ' ')"
echo "multi:  $(docker run --rm ts-multi:1.0 ls /app | tr '\n' ' ')"
```

```bash
docker run -d --name ts-multi -p 8090:3000 ts-multi:1.0 > /dev/null
docker ps --filter name=ts-multi --format '{{.Names}}: {{.Status}}'
```

```bash
curl -s http://localhost:8090/
```

## Hands-on lab

```bash
docker build -q --target build -t ts-multi:build . > /dev/null
echo "build: $(docker run --rm ts-multi:build sh -c 'ls node_modules | wc -l') packages"
echo "final: $(docker run --rm ts-multi:1.0 sh -c 'ls node_modules 2>/dev/null | wc -l') packages"
```

## Break it

```bash
docker build -q -f Dockerfile.broken -t ts-multi:broken . > /dev/null
docker image ls --filter 'reference=ts-multi' --format '{{.Repository}}:{{.Tag}}'
```

```bash
docker run -d --name ts-broken ts-multi:broken > /dev/null
sleep 2
docker ps -a --filter name=ts-broken --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

```bash
docker logs ts-broken 2>&1 | grep -E '^Error'
```

```bash
diff Dockerfile.broken Dockerfile || true
```

## Fix it

```bash
docker rm -f ts-broken > /dev/null
docker build -q -t ts-multi:fixed . > /dev/null
docker run -d --name ts-fixed ts-multi:fixed > /dev/null
sleep 1
docker logs ts-fixed
docker rm -f ts-fixed > /dev/null
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-088
docker build -q --target build -t ts-multi:build . > /dev/null
docker run --rm ts-multi:build sh -c 'npx tsc --noEmit && echo "types ok"'
```

## Cleanup

```bash
docker rm -f ts-multi ts-broken ts-fixed > /dev/null 2>&1 || true
docker image rm -f ts-single:1.0 ts-multi:1.0 ts-multi:build ts-multi:broken ts-multi:fixed > /dev/null 2>&1 || true
rm -rf ~/docker-practice/lesson-088
```
