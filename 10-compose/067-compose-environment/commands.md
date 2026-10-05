<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 067 · Environment variables in Compose · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-067 examples/python-api
cp -r 10-compose/067-compose-environment/examples/. ~/docker-practice/lesson-067/
cd ~/docker-practice/lesson-067
cp .env.example .env
cat compose.yaml .env api.env
```

## Demonstration

```bash
docker compose config | grep -E 'GREETING|APP_VERSION|published'
```

```bash
GREETING="Hello from the shell" docker compose config | grep GREETING
```

```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker compose exec api sh -c 'env | grep -E "^(GREETING|REDIS_HOST|APP_VERSION|LOG_LEVEL)=" | sort'
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-067
API_PORT=8090 docker compose up -d 2> /dev/null
curl -s localhost:8090/
```

```bash
docker compose up -d 2> /dev/null
```

## Break it

```bash
mv .env .env.disabled
docker compose up -d 2>&1 | grep -i warn | head -1
```

```bash
curl -s -w '\nHTTP %{http_code}\n' localhost:8080/ | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
docker compose config | grep -A 3 'ports:'
docker compose port api 5000
```

## Fix it

```bash
sed -i.bak 's/"${API_PORT}:5000"/"${API_PORT:?API_PORT must be set, copy .env.example to .env}:5000"/' compose.yaml && rm compose.yaml.bak
docker compose config 2>&1 > /dev/null
```

```bash
mv .env.disabled .env
docker compose up -d 2> /dev/null
curl -s localhost:8080/
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-067
printf 'API_PORT=8085\nGREETING=Hello from staging\n' > .env.staging
docker compose --env-file .env.staging up -d 2> /dev/null
curl -s localhost:8085/
```

## Cleanup

```bash
cd ~/docker-practice/lesson-067
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-067
```
