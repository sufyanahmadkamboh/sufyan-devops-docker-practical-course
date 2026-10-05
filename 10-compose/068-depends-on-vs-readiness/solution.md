<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 068 · depends_on vs readiness · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Add an `api` service (image `alpine:3.23`, command `echo "api starting after the migration"`) that starts only after
`migrate` has **finished successfully**. Show the order in which the three services started.

## Solution

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

```text
db
migrate
api
api starting after the migration
```

`service_completed_successfully` is made for one-off jobs (migrations, seeding, downloading assets): the application
starts only on a prepared database.
