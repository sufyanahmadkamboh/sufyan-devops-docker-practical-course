<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 074 · up, down and the project lifecycle · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Recreate only the `api` container (without changing the file) and show that `redis` kept running: its start time must
not change.

## Solution

```bash
cd ~/docker-practice/lesson-074
before=$(docker inspect lesson-074-redis-1 --format '{{.State.StartedAt}}')
docker compose up -d --force-recreate --no-deps api 2> /dev/null
after=$(docker inspect lesson-074-redis-1 --format '{{.State.StartedAt}}')
[ "$before" = "$after" ] && echo "redis unchanged, api recreated at $(docker inspect lesson-074-api-1 --format '{{.State.StartedAt}}')"
```

```text
redis unchanged, api recreated at 2026-10-05T17:15:56.715289908Z
```

`--force-recreate` recreates even an unchanged container; `--no-deps` keeps Compose away from the dependencies.
