<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 054 · Bind mounts · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate copies the command but writes the folder as a relative name:

```bash
docker run -d --name site2 -p 8081:80 -v site:/usr/share/nginx/html nginx:1.30-alpine > /dev/null
curl -s http://localhost:8081 | grep -o '<title>.*</title>'
```

```text
<title>Welcome to nginx!</title>
```

The container runs, but it serves nginx's default page instead of the cafe.

## Troubleshoot it

When a container does not see your files, inspect its mounts:

```bash
docker inspect site2 --format '{{range .Mounts}}{{.Type}} name={{.Name}} -> {{.Destination}}{{end}}'
docker volume ls --filter name=^site$
```

```text
volume name=site -> /usr/share/nginx/html
DRIVER    VOLUME NAME
local     site
```

`volume name=site`: a source without a `/` is the name of a **named volume**. Docker created an empty volume called
`site` and, because it was empty, copied the image's files (nginx's default page) into it. Your folder was never
involved.

## Fix it

Use an absolute path (`"$(pwd)/site"`), or the `--mount` form, which says explicitly what it is and refuses a source
that does not exist:

```bash
docker rm -f site2 > /dev/null
docker volume rm site > /dev/null
docker run -d --name site2 -p 8081:80 --mount type=bind,source="$(pwd)/site",target=/usr/share/nginx/html,readonly nginx:1.30-alpine > /dev/null
curl -s http://localhost:8081 | grep -o '<h1>.*</h1>'
```

```text
<h1>Welcome to the cafe</h1>
```
