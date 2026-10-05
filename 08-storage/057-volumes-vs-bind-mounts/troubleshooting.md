<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 057 · Volumes vs bind mounts · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Now mount the **empty host folder** at the same place:

```bash
docker run -d --name with-bind -p 8081:80 -v "$(pwd)/empty-folder:/usr/share/nginx/html" nginx:1.30-alpine > /dev/null
sleep 1
curl -s -w '\nHTTP %{http_code}\n' http://localhost:8081 | tail -1
```

```text
HTTP 403
```

## Troubleshoot it

`HTTP 403 Forbidden`: nginx runs, but has no `index.html` to serve and directory listing is off. Look at the folder
from inside the container, and at nginx's log:

```bash
echo "files: [$(docker exec with-bind ls /usr/share/nginx/html)]"
docker logs with-bind 2>&1 | grep -m1 'directory index'
```

```text
files: []
2026/10/05 10:52:46 [error] 32#32: *1 directory index of "/usr/share/nginx/html/" is forbidden, client: 172.17.0.1, server: localhost, request: "GET / HTTP/1.1", host: "localhost:8081"
```

The folder is empty: a bind mount shows exactly the host folder and **hides** the image's files at that path. Docker
never copies anything into a bind mount.

## Fix it

With a bind mount, the host must provide the content:

```bash
echo '<h1>Served from the host</h1>' > empty-folder/index.html
curl -s -w '\nHTTP %{http_code}\n' http://localhost:8081 | tail -1
```

```text
HTTP 200
```

Rule of thumb: use a bind mount when the host owns the files (you edit them), a named volume when the application
owns them (it writes them).
