<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 074 · up, down and the project lifecycle · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-074 examples/python-api
cp -r 10-compose/074-compose-up-down/examples/. ~/docker-practice/lesson-074/
cd ~/docker-practice/lesson-074
cat compose.yaml
```

## Demonstration

```bash
docker compose up -d --build --quiet-build 2>&1 | grep -E "Container .* (Created|Started|Running|Recreated) *$"
```

```bash
docker compose up -d 2>&1 | grep -E "Container .* (Created|Started|Running|Recreated) *$"
```

```bash
sed -i.bak 's/      REDIS_HOST: redis/      REDIS_HOST: redis\
      GREETING: Hello after up/' compose.yaml && rm compose.yaml.bak
docker compose up -d 2>&1 | grep -E "Container .* (Created|Started|Running|Recreated) *$"
```

```bash
docker compose stop 2> /dev/null
docker compose ps -a --format '{{.Service}}: {{.State}}'
docker compose start 2> /dev/null
docker compose ps -a --format '{{.Service}}: {{.State}}'
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-074
docker compose down -v --rmi local 2> /dev/null
echo "$(docker ps -aq --filter name=lesson-074 | wc -l) $(docker network ls -q --filter name=lesson-074 | wc -l) $(docker volume ls -q --filter name=lesson-074 | wc -l) $(docker image ls -q lesson-074-api | wc -l)" | tr -s ' '
```

```bash
docker compose up -d --build --quiet-build 2> /dev/null
```

## Break it

```bash
awk '/^  worker:/ { skip = 1; next } /^[^ ]/ { skip = 0 } skip && /^    / { next } { print }' compose.yaml > compose.new
mv compose.new compose.yaml
docker compose config --services
docker compose up -d 2>&1 | grep -i orphan
```

## Troubleshoot it

```bash
docker ps --filter label=com.docker.compose.project=lesson-074 --format '{{.Names}}: {{.Status}}'
```

## Fix it

```bash
docker compose up -d --remove-orphans 2> /dev/null
docker ps --filter label=com.docker.compose.project=lesson-074 --format '{{.Names}}'
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-074
before=$(docker inspect lesson-074-redis-1 --format '{{.State.StartedAt}}')
docker compose up -d --force-recreate --no-deps api 2> /dev/null
after=$(docker inspect lesson-074-redis-1 --format '{{.State.StartedAt}}')
[ "$before" = "$after" ] && echo "redis unchanged, api recreated at $(docker inspect lesson-074-api-1 --format '{{.State.StartedAt}}')"
```

## Cleanup

```bash
cd ~/docker-practice/lesson-074
docker compose down -v --rmi local --remove-orphans 2> /dev/null
rm -rf ~/docker-practice/lesson-074
```
