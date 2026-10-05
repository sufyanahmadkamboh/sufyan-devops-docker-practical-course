<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 065 · Networking in Compose · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-065 examples/python-api
cp -r 10-compose/065-compose-networking/examples/. ~/docker-practice/lesson-065/
cd ~/docker-practice/lesson-065
cat compose.yaml
```

## Demonstration

```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker network ls --filter name=lesson-065 --format '{{.Name}}  driver={{.Driver}}'
```

```bash
for net in frontend backend; do
  echo "$net: $(docker network inspect lesson-065_$net --format '{{range .Containers}}{{.Name}} {{end}}')"
done
```

```bash
docker compose exec api python -c "import socket; print('redis ->', socket.gethostbyname('redis'))"
```

```bash
curl -s localhost:8080/visits
```

```bash
docker compose exec tools ping -c 1 -W 2 redis 2>&1
```

## Hands-on lab

```bash
docker inspect lesson-065-api-1 --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{$net.IPAddress}}{{"\n"}}{{end}}'
```

## Break it

```bash
cat broken/compose.override.yaml
docker compose -f compose.yaml -f broken/compose.override.yaml up -d 2> /dev/null
sleep 3
curl -s -w '\nHTTP %{http_code}\n' localhost:8080/visits | tail -1
```

## Troubleshoot it

```bash
docker compose logs api 2>&1 | grep -o "redis.exceptions.ConnectionError.*" | tail -1
docker compose exec api python -c "import socket; print('localhost ->', socket.gethostbyname('localhost'))"
```

## Fix it

```bash
docker compose up -d 2> /dev/null
docker compose exec api printenv REDIS_HOST
curl -s localhost:8080/visits
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-065
docker compose exec tools wget -qO- http://api:5000/health; echo
docker compose exec tools nc -z -w 2 redis 6379 2>&1 || echo "redis unreachable"
```

## Cleanup

```bash
cd ~/docker-practice/lesson-065
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-065
```
