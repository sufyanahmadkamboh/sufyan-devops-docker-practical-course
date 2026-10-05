<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 066 · Volumes in Compose · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-066 examples/python-api
cp -r 10-compose/066-compose-volumes/examples/. ~/docker-practice/lesson-066/
cd ~/docker-practice/lesson-066
cat compose.yaml
```

## Demonstration

```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker volume ls --filter name=lesson-066 --format '{{.Name}}'
```

```bash
curl -s localhost:8080/visits; curl -s localhost:8080/visits; curl -s localhost:8080/visits
```

```bash
docker compose down 2> /dev/null
docker ps -a --filter label=com.docker.compose.project=lesson-066 --format '{{.Names}}' | wc -l
docker volume ls --filter name=lesson-066 --format '{{.Name}}'
```

```bash
docker compose up -d 2> /dev/null
sleep 2
curl -s localhost:8080/visits
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-066
docker inspect lesson-066-redis-1 --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{"\n"}}{{end}}'
docker compose exec redis ls /data
```

## Break it

```bash
docker compose -f broken/compose.yaml config 2>&1
```

## Troubleshoot it

```bash
diff broken/compose.yaml compose.yaml || true
```

## Fix it

```bash
cp compose.yaml broken/compose.yaml
docker compose -f broken/compose.yaml config --volumes
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-066
docker compose down -v 2> /dev/null
docker volume ls --filter name=lesson-066 --format '{{.Name}}' | wc -l
docker compose up -d 2> /dev/null
sleep 2
curl -s localhost:8080/visits
```

## Cleanup

```bash
cd ~/docker-practice/lesson-066
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-066
```
