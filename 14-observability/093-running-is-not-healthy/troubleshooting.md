<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 093 · Running is not healthy · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

One user requests the report:

```bash
curl -s -m 2 http://localhost:8080/report || echo "gave up after 2 seconds"
```

```text
gave up after 2 seconds
```

## Troubleshoot it

Now nothing answers, not even `/health`:

```bash
curl -s -m 2 http://localhost:8080/health || echo "no answer from /health"
```

```text
no answer from /health
```

What does Docker think?

```bash
docker inspect --format 'state={{.State.Status}} health={{.State.Health.Status}} restarts={{.RestartCount}}' api
```

```text
state=running health=unhealthy restarts=0
```

The process is `running` and the restart policy `always` did nothing (`restarts=0`): it reacts only to exits. The
health check is the one signal that something is wrong. Its log says what it saw:

```bash
docker inspect --format '{{range .State.Health.Log}}{{.Output}}{{end}}' api | grep . | tail -1
```

```text
TimeoutError: timed out
```

The root cause is in the code: this server handles **one request at a time** (`HTTPServer`), so the stuck `/report`
request blocks every other request, including the health check.

## Fix it

Short term: restart the hung container (this is what an orchestrator would do automatically for an unhealthy one):

```bash
docker restart api > /dev/null && echo "restarted"
```

```bash
docker inspect --format 'state={{.State.Status}} health={{.State.Health.Status}}' api
```

Real fix: change the code. The `threaded` version handles every request in its own thread, so one stuck request does
not block the others (the endpoint itself still needs a timeout on its dependency):

```bash
docker rm -f api > /dev/null
docker build -q -t cafe-api:threaded threaded > /dev/null
docker run -d --name api --restart always -p 8080:8080 cafe-api:threaded > /dev/null && echo "started api"
```

```bash
docker inspect --format 'health={{.State.Health.Status}}' api
```

```bash
curl -s -m 2 http://localhost:8080/report || echo "/report gave up after 2 seconds"
curl -s -m 2 http://localhost:8080/health > /dev/null && echo "/health still ok"
```

```text
/report gave up after 2 seconds
/health still ok
```
