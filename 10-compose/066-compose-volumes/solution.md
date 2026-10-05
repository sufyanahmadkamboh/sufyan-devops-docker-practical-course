<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 066 · Volumes in Compose · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Show what `down -v` does to the counter: remove the project with its volumes, start it again, and call `/visits`.

## Solution

```bash
cd ~/docker-practice/lesson-066
docker compose down -v 2> /dev/null
docker volume ls --filter name=lesson-066 --format '{{.Name}}' | wc -l
docker compose up -d 2> /dev/null
sleep 2
curl -s localhost:8080/visits
```

```text
0
{"visits":1}
```

`-v` deleted `lesson-066_redis-data`; the new Redis started empty. Use `down -v` deliberately: on a database it deletes
the data.
