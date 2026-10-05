<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 069 · Healthchecks in Compose · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-069 examples/python-api
cp -r 10-compose/069-compose-healthchecks/examples/. ~/docker-practice/lesson-069/
cd ~/docker-practice/lesson-069
cat compose.yaml
```

## Demonstration

```bash
docker compose up -d --build --quiet-build --wait 2> /dev/null
docker compose ps --format '{{.Service}}: {{.Status}}'
```

```bash
docker inspect lesson-069-api-1 --format '{{.State.Health.Status}}: {{range .State.Health.Log}}ExitCode={{.ExitCode}} {{end}}'
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-069
docker compose exec redis redis-cli ping
docker inspect lesson-069-redis-1 --format '{{range .State.Health.Log}}{{.Output}}{{end}}' | tail -1
```

## Break it

```bash
cp compose.yaml compose.good.yaml
cp broken/compose.yaml compose.yaml
docker compose up -d --wait --wait-timeout 40 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
curl -s localhost:8080/health
```

```bash
docker inspect lesson-069-api-1 --format '{{range .State.Health.Log}}{{.ExitCode}} {{.Output}}{{end}}' | grep -o "ConnectionRefusedError.*" | tail -1
docker inspect lesson-069-api-1 --format '{{json .Config.Healthcheck.Test}}'
```

## Fix it

```bash
cp compose.good.yaml compose.yaml
docker compose up -d --wait 2> /dev/null
docker compose ps --format '{{.Service}}: {{.Status}}'
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-069
docker compose exec redis redis-cli CONFIG SET requirepass x > /dev/null
docker compose exec redis redis-cli ping
sleep 25
echo "after 25 s: $(docker inspect lesson-069-redis-1 --format '{{.State.Health.Status}}')"
docker compose exec redis redis-cli -a x --no-auth-warning CONFIG SET requirepass "" > /dev/null
sleep 3
echo "after the undo: $(docker inspect lesson-069-redis-1 --format '{{.State.Health.Status}}') again"
```

## Cleanup

```bash
cd ~/docker-practice/lesson-069
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-069
```
