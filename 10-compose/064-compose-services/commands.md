<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 064 · Services · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-064 examples/python-api
cp -r 10-compose/064-compose-services/examples/. ~/docker-practice/lesson-064/
cd ~/docker-practice/lesson-064
cat compose.yaml
```

## Demonstration

```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker compose config --services
docker compose ps --no-trunc --format '{{.Name}}  image={{.Image}}  command={{.Command}}'
```

```bash
curl -s localhost:8080/visits
```

```bash
docker compose exec api sh -c 'kill 1'
```

```bash
docker inspect lesson-064-api-1 --format 'policy: {{.HostConfig.RestartPolicy.Name}}, restarts: {{.RestartCount}}, state: {{.State.Status}}'
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-064
docker compose stop redis 2> /dev/null; sleep 3
docker inspect lesson-064-redis-1 --format '{{.State.Status}}'
docker compose start redis 2> /dev/null
docker inspect lesson-064-redis-1 --format '{{.State.Status}}'
```

## Break it

```bash
docker compose up -d --scale api=2 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
docker compose ps -a --format '{{.Name}}: {{.State}}'
```

## Fix it

```bash
sed -i.bak 's/"8080:5000"/"8080-8081:5000"/' compose.yaml && rm compose.yaml.bak
docker compose up -d --scale api=2 2> /dev/null
docker compose ps --format '{{.Name}}  {{.Ports}}'
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-064
curl -s localhost:8080/visits
curl -s localhost:8081/visits
curl -s localhost:8080/ | grep -o '"hostname":"[0-9a-f]*"'
curl -s localhost:8081/ | grep -o '"hostname":"[0-9a-f]*"'
```

## Cleanup

```bash
cd ~/docker-practice/lesson-064
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-064
```
