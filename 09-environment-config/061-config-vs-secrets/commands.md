<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 061 · Configuration vs secrets · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-061
cd ~/docker-practice/lesson-061
printf 'example-db-password-change-me' > db_password.txt
printf 'db_password.txt\n' > .gitignore
```

## Demonstration

```bash
docker run -d --name db-env -e POSTGRES_PASSWORD="$(cat db_password.txt)" postgres:18-alpine > /dev/null
sleep 3
docker exec db-env pg_isready -h 127.0.0.1 -U postgres
```

```bash
docker run -d --name db-file \
  -v "$(pwd)/db_password.txt:/run/secrets/db_password:ro" \
  -e POSTGRES_PASSWORD_FILE=/run/secrets/db_password \
  postgres:18-alpine > /dev/null
sleep 3
docker exec db-file pg_isready -h 127.0.0.1 -U postgres
```

```bash
docker exec -e PGPASSWORD="$(cat db_password.txt)" db-file psql -h 127.0.0.1 -U postgres -tAc "select 'logged in'"
```

## Hands-on lab

```bash
docker exec db-file ls -l /run/secrets/
docker exec db-file sh -c 'echo changed > /run/secrets/db_password' 2>&1 || true
```

## Break it

```bash
docker inspect db-env --format '{{range .Config.Env}}{{println .}}{{end}}' | grep PASSWORD
```

## Troubleshoot it

```bash
docker exec db-env sh -c 'env | grep POSTGRES_PASSWORD'
```

```bash
docker inspect db-file --format '{{range .Config.Env}}{{println .}}{{end}}' | grep PASSWORD
```

## Fix it

```bash
docker rm -f db-env > /dev/null
docker run -d --name db-env \
  -v "$(pwd)/db_password.txt:/run/secrets/db_password:ro" \
  -e POSTGRES_PASSWORD_FILE=/run/secrets/db_password postgres:18-alpine > /dev/null
docker inspect db-env | grep -q 'change-me' || echo "no password in inspect"
```

## Practice challenge

```bash
printf 'example-token-0000-abc' > api_token.txt
docker run -d --name worker -v "$(pwd)/api_token.txt:/run/secrets/api_token:ro" alpine:3.23 \
  sh -c 'TOKEN=$(cat /run/secrets/api_token); echo "token length: ${#TOKEN}"; sleep 300' > /dev/null
sleep 1
docker logs worker
docker inspect worker | grep -q 'example-token' || echo "inspect clean"
```

## Cleanup

```bash
docker rm -f db-env db-file worker > /dev/null
rm -rf ~/docker-practice/lesson-061
```
