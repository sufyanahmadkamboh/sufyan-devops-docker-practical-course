<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 092 · HEALTHCHECK · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The `broken/` image checks the wrong port. Build and start it:

```bash
docker build -q -t cafe-web:broken-health broken > /dev/null
docker run -d --name web-broken -p 8082:80 cafe-web:broken-health > /dev/null && echo "started web-broken"
```

```bash
docker ps --filter name=web-broken --format '{{.Names}}: {{.Status}}'
```

```text
web-broken: Up 9 seconds (unhealthy)
```

## Troubleshoot it

The container is `Up`, and nginx actually serves pages:

```bash
curl -s http://localhost:8082/ | grep -o '<title>.*</title>'
```

So the **check** is wrong, not the application. Read what the check printed:

```bash
docker inspect --format '{{range .State.Health.Log}}{{.ExitCode}} {{.Output}}{{end}}' web-broken | tail -2
docker inspect --format '{{json .Config.Healthcheck.Test}}' web-broken
```

```text
1 wget: can't connect to remote host (127.0.0.1): Connection refused

["CMD-SHELL","wget -q --spider http://127.0.0.1:8080/ || exit 1"]
```

`Connection refused` on `127.0.0.1:8080`: the check runs **inside** the container, where nginx listens on port 80.
`-p 8082:80` maps the host's port 8082 to the container's port 80; the container itself never sees 8082 or 8080.

## Fix it

The health check must use the container's own port (see `fixed/Dockerfile`). Replace the container with the fixed
image:

```bash
docker rm -f web-broken > /dev/null
docker run -d --name web-broken -p 8082:80 cafe-web:health > /dev/null && echo "started web-broken"
```

```bash
docker ps --filter name=web-broken --format '{{.Names}}: {{.Status}}'
```
