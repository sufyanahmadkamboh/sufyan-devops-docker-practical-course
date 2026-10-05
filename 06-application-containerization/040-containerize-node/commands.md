<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 040 · Containerizing a Node.js application · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-040 examples/node-api
cp -r 06-application-containerization/040-containerize-node/examples/. ~/docker-practice/lesson-040/
cd ~/docker-practice/lesson-040
ls -a
cat Dockerfile
```

## Demonstration

```bash
docker build -q -t node-api:1.0 . > /dev/null
docker image ls node-api
docker run -d --name node-api -p 8080:3000 -e APP_VERSION=1.0 node-api:1.0 > /dev/null
```

```bash
curl -s http://localhost:8080/
```

```bash
docker exec node-api id
docker exec node-api ps -o pid,user,args
```

## Hands-on lab

```bash
start=$(date +%s)
docker stop node-api > /dev/null
echo "stopped in $(( $(date +%s) - start )) s, exit code $(docker inspect --format '{{.State.ExitCode}}' node-api)"
docker rm node-api > /dev/null
```

## Break it

```bash
cd ~/docker-practice/lesson-040
rm package-lock.json
sed -i.bak 's/package.json package-lock.json/package*.json/' Dockerfile && rm Dockerfile.bak
docker build -t node-api:nolock . 2>&1 | grep -E 'npm (error|ERR)' | head -3
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
ls package-lock.json 2> /dev/null || echo "no lockfile in the context"
```

## Fix it

```bash
docker run --rm -v "$(pwd):/app" -w /app node:24-alpine npm install --package-lock-only --silent
grep lockfileVersion package-lock.json
```

```bash
docker build -q -t node-api:fixed . > /dev/null
docker image ls node-api
```

## Practice challenge

```bash
docker run -d --name node-api-4000 -p 8081:4000 -e PORT=4000 -e GREETING="Hallo aus dem Container" node-api:fixed > /dev/null
sleep 1
curl -s http://localhost:8081/
```

## Cleanup

```bash
docker rm -f node-api node-api-4000 > /dev/null 2>&1 || true
docker image rm -f node-api:1.0 node-api:nolock node-api:fixed > /dev/null 2>&1 || true
rm -rf ~/docker-practice/lesson-040
```
