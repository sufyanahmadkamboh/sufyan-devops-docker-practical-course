<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 058 · A persistent database · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker image inspect postgres:18-alpine --format 'VOLUME {{json .Config.Volumes}}{{"\n"}}{{range .Config.Env}}{{println .}}{{end}}' | grep -E 'VOLUME|PGDATA'
mkdir -p ~/docker-practice/lesson-058 && cd ~/docker-practice/lesson-058
printf 'example-db-password-change-me' > db_password.txt
```

## Demonstration

```bash
docker run -d --name db -v pgdata:/var/lib/postgresql \
  -v "$(pwd)/db_password.txt:/run/secrets/db_password:ro" -e POSTGRES_PASSWORD_FILE=/run/secrets/db_password \
  postgres:18-alpine > /dev/null
sleep 3
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

```bash
docker exec db psql -U postgres -c "CREATE TABLE orders (id serial PRIMARY KEY, item text NOT NULL)"
docker exec db psql -U postgres -c "INSERT INTO orders (item) VALUES ('espresso'), ('cappuccino')"
docker exec db psql -U postgres -tAc "SELECT count(*) FROM orders"
```

```bash
docker rm -f db > /dev/null
docker run -d --name db -v pgdata:/var/lib/postgresql \
  -v "$(pwd)/db_password.txt:/run/secrets/db_password:ro" -e POSTGRES_PASSWORD_FILE=/run/secrets/db_password \
  postgres:18-alpine > /dev/null
sleep 3
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

```bash
docker exec db psql -U postgres -tAc "SELECT item FROM orders ORDER BY id"
docker logs db 2>&1 | grep -m1 'Skipping initialization'
```

## Hands-on lab

```bash
docker run --rm -v pgdata:/data:ro alpine:3.23 sh -c 'du -sh /data; ls /data/18/docker'
```

## Break it

```bash
docker run -d --name old-path -v old-pgdata:/var/lib/postgresql/data -e POSTGRES_PASSWORD=example-password-change-me postgres:18-alpine > /dev/null
sleep 5
docker ps -a --filter name=old-path --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

```bash
docker logs old-path 2>&1
```

```bash
docker inspect old-path --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{println}}{{end}}'
```

## Fix it

```bash
docker rm -f old-path > /dev/null
docker volume rm old-pgdata > /dev/null
docker volume prune -f > /dev/null
docker run -d --name old-path -v old-pgdata:/var/lib/postgresql -e POSTGRES_PASSWORD=example-password-change-me postgres:18-alpine > /dev/null
sleep 3
docker exec old-path pg_isready -h 127.0.0.1 -U postgres
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-058
docker exec db pg_dump -U postgres postgres > backup.sql
docker exec db psql -U postgres -c "DROP TABLE orders" > /dev/null
docker exec -i db psql -U postgres -q < backup.sql > /dev/null
echo "restored: $(docker exec db psql -U postgres -tAc 'SELECT count(*) FROM orders') orders"
```

## Cleanup

```bash
docker rm -f db old-path > /dev/null
docker volume rm pgdata old-pgdata > /dev/null
rm -rf ~/docker-practice/lesson-058
```
