<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 073 · Building images with Compose · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-073 examples/python-api
cp -r 10-compose/073-compose-build/examples/. ~/docker-practice/lesson-073/
cd ~/docker-practice/lesson-073
cat compose.yaml
```

## Demonstration

```bash
docker compose build --quiet 2> /dev/null
docker image ls cafe-api --format '{{.Repository}}:{{.Tag}}  {{.Size}}'
```

```bash
docker compose up -d 2> /dev/null
docker compose exec api printenv APP_VERSION | sed 's/^/APP_VERSION=/'
```

```bash
docker compose images --format json | grep -o '"Repository":"[^"]*","Tag":"[^"]*"' | sort -u
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-073
docker compose build --quiet --build-arg APP_VERSION=1.5.0 api 2> /dev/null
docker compose run --rm --no-deps api printenv APP_VERSION 2> /dev/null
```

```bash
docker compose build --quiet 2> /dev/null
docker compose up -d 2> /dev/null
```

## Break it

```bash
sed -i.bak 's/Hello from Python/Hello from version 1.4.0/' app.py && rm app.py.bak
grep -c "Hello from version 1.4.0" app.py
docker compose up -d 2> /dev/null
sleep 2
curl -s localhost:8080/
```

## Troubleshoot it

```bash
docker image inspect cafe-api:1.4.0 --format 'image built: {{.Created}}'
docker compose exec api grep -o "Hello from [A-Za-z0-9. ]*" app.py
```

## Fix it

```bash
docker compose up -d --build --quiet-build 2> /dev/null
curl -s localhost:8080/
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-073
sed -i.bak -e 's/image: cafe-api:1.4.0/image: cafe-api:${APP_VERSION:-dev}/' \
           -e 's/APP_VERSION: "1.4.0"/APP_VERSION: "${APP_VERSION:-dev}"/' compose.yaml && rm compose.yaml.bak
APP_VERSION=2.0.0 docker compose build --quiet 2> /dev/null
docker image ls cafe-api --format '{{.Repository}}:{{.Tag}}' | sort
```

## Cleanup

```bash
cd ~/docker-practice/lesson-073
docker compose down -v 2> /dev/null
docker image rm -f cafe-api:1.4.0 cafe-api:1.5.0 cafe-api:2.0.0 > /dev/null 2>&1
rm -rf ~/docker-practice/lesson-073
```
