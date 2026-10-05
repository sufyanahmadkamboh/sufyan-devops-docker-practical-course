<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 011 · Running Nginx · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Open the website from your own computer:

```bash
curl -sS http://localhost:8080
```

```text
curl: (7) Failed to connect to localhost port 8080 after 2232 ms: Could not connect to server
```

## Troubleshoot it

The server works (other containers get the page), but nothing on your computer listens on port 8080: `curl` gets no
connection (`Failed to connect … Couldn't connect to server`; with Docker Desktop on Windows it can also be
`Empty reply from server`). Look at the PORTS column:

```bash
docker ps --filter name=^web$ --format '{{.Names}}: {{.Ports}}'
```

`80/tcp` without an arrow means "the image says it uses port 80", nothing more. A published port looks like
`0.0.0.0:8080->80/tcp`. The container's network is internal to Docker; you have to publish a port explicitly.

## Fix it

A container's ports are fixed when it is created, so replace it with one that publishes port 80 as 8080 on your
computer (next lesson in detail), and copy the website again:

<!-- test: contains=0.0.0.0:8080->80/tcp -->
```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null
docker cp index.html web:/usr/share/nginx/html/index.html
docker cp styles.css web:/usr/share/nginx/html/styles.css
docker ps --filter name=^web$ --format '{{.Names}}: {{.Ports}}'
```

```bash
curl -s http://localhost:8080 | grep '<h1>'
```

Open <http://localhost:8080> in your browser too.
