<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 081 · Running as a non-root user · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The `broken` version adds a user and `USER app`, and nothing else. Build and start it:

```bash
docker build -q -t cafe-web:broken broken > /dev/null
docker run -d --name web-broken -p 8081:8080 cafe-web:broken > /dev/null
docker image ls cafe-web --format '{{.Repository}}:{{.Tag}}'
```

```bash
docker ps -a --filter name=web-broken --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

The container exited with status 1. Its logs say why:

```bash
docker logs web-broken 2>&1 | tail -1
```

```text
PermissionError: [Errno 13] Permission denied: 'data'
```

`Permission denied: 'data'`: the app creates `data/` in `/app`, and `/app` belongs to root. Check who owns it and who
the process is (`--entrypoint` replaces the command, so the container lives long enough to look):

```bash
docker run --rm --entrypoint sh cafe-web:broken -c 'id; ls -ld /app'
```

```text
uid=100(app) gid=101(app) groups=101(app),101(app)
drwxr-xr-x    1 root     root          4096 Oct  5 16:56 /app
```

The root cause is not `USER`: it is that the image never gave the new user anywhere to write.

## Fix it

Give the user **only** the folder it writes to; the code stays owned by root, so even this user cannot modify it
(see `fixed/Dockerfile`):

```bash
grep -n "USER\|chown" fixed/Dockerfile
```

```text
6:RUN mkdir data && chown app:app data
7:USER app
```

```bash
docker rm -f web-broken > /dev/null
docker build -q -t cafe-web:fixed fixed > /dev/null
docker run -d --name web-fixed -p 8081:8080 cafe-web:fixed > /dev/null
docker image ls cafe-web --format '{{.Repository}}:{{.Tag}}'
```

```bash
curl -s http://localhost:8081/
docker exec web-fixed ls -l /app
```

```text
hello from uid 100
total 8
-rwxr-xr-x    1 root     root           696 Oct  5 16:56 app.py
drwxr-xr-x    1 app      app           4096 Oct  5 16:56 data
```
