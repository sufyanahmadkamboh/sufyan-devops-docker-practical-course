<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 093 · Running is not healthy · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write a one-line "watchdog" that finds every unhealthy container on the host and restarts it. Test it by breaking the
`single` version again.

## Solution

```bash
docker run -d --name api-single -p 8081:8080 cafe-api:single > /dev/null && echo "started api-single"
```

```bash
docker inspect --format '{{.State.Health.Status}}' api-single
```

```bash
curl -s -m 2 http://localhost:8081/report || echo "gave up"
```

```bash
docker ps --filter health=unhealthy --format '{{.Names}}'
```

```bash
docker ps --filter health=unhealthy --format '{{.Names}}' | xargs -r docker restart
```

```text
api-single
```

`docker ps --filter health=unhealthy` finds them (by name) and `xargs -r docker restart` restarts them (`-r`: do
nothing when the list is empty). Run regularly (cron, a systemd timer), this is a minimal version of what Kubernetes'
liveness probe does. In production, prefer the platform's own mechanism and alerting over a homemade script.
