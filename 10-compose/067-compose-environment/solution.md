<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 067 · Environment variables in Compose · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Create `.env.staging` with `API_PORT=8085` and `GREETING=Hello from staging`, and start the stack with it, without
changing `.env`.

## Solution

```bash
cd ~/docker-practice/lesson-067
printf 'API_PORT=8085\nGREETING=Hello from staging\n' > .env.staging
docker compose --env-file .env.staging up -d 2> /dev/null
curl -s localhost:8085/
```

```text
{"hostname":"7741779652cd","message":"Hello from staging"}
```

`--env-file` replaces `.env` for interpolation; one `compose.yaml` serves several environments.
