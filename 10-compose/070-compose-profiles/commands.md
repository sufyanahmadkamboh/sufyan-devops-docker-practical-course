<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 070 · Profiles · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-070 examples/python-api
cp -r 10-compose/070-compose-profiles/examples/. ~/docker-practice/lesson-070/
cd ~/docker-practice/lesson-070
cat compose.yaml
```

## Demonstration

```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker compose ps --format '{{.Service}}'
```

```bash
docker compose --profile "*" config --services
docker compose config --profiles
```

```bash
docker compose --profile seed up -d 2> /dev/null
sleep 2
curl -s localhost:8080/visits
```

```bash
COMPOSE_PROFILES=debug docker compose up -d 2> /dev/null
docker compose ps --format '{{.Service}}'
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-070
docker compose exec tools getent hosts redis
```

## Break it

```bash
cp compose.yaml compose.good.yaml
cp broken/compose.yaml compose.yaml
docker compose up -d 2>&1
```

## Troubleshoot it

```bash
docker compose --profile seed config --services
```

## Fix it

```bash
cp compose.good.yaml compose.yaml
docker compose config --services
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-070
docker compose run --rm seed 2> /dev/null
curl -s localhost:8080/visits
```

## Cleanup

```bash
cd ~/docker-practice/lesson-070
docker compose --profile "*" down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-070
```
