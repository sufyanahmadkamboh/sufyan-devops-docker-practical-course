<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 072 · exec and run · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Stop the API, then try to look inside it:

```bash
docker compose stop api 2> /dev/null
docker compose exec api ls 2>&1
```

```text
service "api" is not running
```

## Troubleshoot it

`exec` needs a running container: it starts a process inside an existing one. Check the state:

```bash
docker compose ps -a --format '{{.Service}}: {{.State}} ({{.Status}})'
```

```text
api: exited (Exited (0) Less than a second ago)
redis: running (Up 6 seconds)
```

When the container crashed instead of being stopped, `exec` is impossible too, and `docker compose logs api` is the
first place to look (lesson 071).

## Fix it

Start it again, or use `run` when you need the image and configuration but not the running container (for example to
inspect files of a service that crashes at start):

```bash
docker compose run --rm --no-deps api ls 2> /dev/null
docker compose start api 2> /dev/null
docker compose exec api ls
```
