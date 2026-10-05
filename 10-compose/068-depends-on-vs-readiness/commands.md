<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 068 · depends_on vs readiness · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-068 10-compose/068-depends-on-vs-readiness/examples
cd ~/docker-practice/lesson-068
cat compose.yaml
```

## Demonstration

```bash
docker compose up -d db 2> /dev/null
docker compose exec db pg_isready -h 127.0.0.1 || true
sleep 6
docker compose exec db pg_isready -h 127.0.0.1
```

```bash
docker compose down -v 2> /dev/null
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-068
docker compose up -d 2> /dev/null
sleep 5
docker compose ps -a --format '{{.Service}}: {{.Status}}'
```

## Break it

```bash
docker compose logs --no-log-prefix migrate
```

## Troubleshoot it

```bash
docker inspect lesson-068-db-1 lesson-068-migrate-1 --format '{{.Name}} started {{.State.StartedAt}}'
docker compose logs --no-log-prefix -t db | grep "ready to accept connections" | tail -1
```

## Fix it

```bash
docker compose down -v 2> /dev/null
diff compose.yaml fixed/compose.yaml | grep '^>'
```

```bash
cp fixed/compose.yaml compose.yaml
docker compose up -d 2> /dev/null
docker compose ps -a --format '{{.Service}}: {{.Status}}'
docker compose logs --no-log-prefix migrate
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-068
cat >> compose.yaml <<'EOF'
  api:
    image: alpine:3.23
    command: echo "api starting after the migration"
    depends_on:
      migrate:
        condition: service_completed_successfully
EOF
docker compose up -d 2> /dev/null
docker compose ps -a --format '{{.CreatedAt}} {{.Service}}' | sort | cut -d' ' -f5
docker compose logs --no-log-prefix api
```

## Cleanup

```bash
cd ~/docker-practice/lesson-068
docker compose down -v 2> /dev/null
rm -rf ~/docker-practice/lesson-068
```
