<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 060 · Environment files · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-060 examples/node-api
cd ~/docker-practice/lesson-060
printf '# cafe API, development\nGREETING=Welcome to the cafe\nAPP_VERSION=1.4.0\nLOG_LEVEL=info\n' > app.env
cat app.env
```

## Demonstration

```bash
docker run -d --name api -p 8080:3000 --env-file app.env -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8080; echo
```

```bash
docker inspect api --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E 'GREETING|APP_VERSION|LOG_LEVEL'
```

```bash
docker run --rm --env-file app.env -e LOG_LEVEL=debug alpine:3.23 sh -c 'echo "LOG_LEVEL=$LOG_LEVEL"'
```

## Hands-on lab

```bash
printf 'GREETING=Welcome, production guest\nLOG_LEVEL=warn\n' > prod.env
docker run --rm --env-file app.env --env-file prod.env alpine:3.23 sh -c 'env | grep -E "GREETING|APP_VERSION|LOG_LEVEL" | sort'
```

## Break it

```bash
printf 'GREETING="Welcome to the cafe"\nAPP_VERSION=1.4.0\n' > quoted.env
docker run -d --name quoted -p 8081:3000 --env-file quoted.env -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8081; echo
```

## Troubleshoot it

```bash
docker exec quoted printenv GREETING | sed 's/^/GREETING=/'
```

## Fix it

```bash
printf 'GREETING=Welcome to the cafe\nAPP_VERSION=1.4.0\n' > quoted.env
docker rm -f quoted > /dev/null
docker run -d --name quoted -p 8081:3000 --env-file quoted.env -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8081; echo
```

## Practice challenge

```bash
printf 'RELEASE\n' > release.env
export RELEASE=2026.10
docker run --rm --env-file release.env alpine:3.23 sh -c 'echo "release $RELEASE"'
```

## Cleanup

```bash
docker rm -f api quoted > /dev/null
rm -rf ~/docker-practice/lesson-060
```
