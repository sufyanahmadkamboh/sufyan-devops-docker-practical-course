<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 051 · EXPOSE vs publishing ports · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A developer adds `EXPOSE 80` to a Dockerfile and expects the site to be reachable on the host:

```bash
printf 'FROM nginx:1.30-alpine\nEXPOSE 80\n' | docker build -q -t my-site:1.0 - > /dev/null
docker run -d --name my-site my-site:1.0 > /dev/null
code=0; curl -s -m 5 http://localhost:80 > /dev/null || code=$?
echo "curl exit code $code"
[ "$code" -eq 0 ]
```

```text
curl exit code 7
```

## Troubleshoot it

curl exit code 7 means "failed to connect": nothing listens on the host's port 80. Check what is published, and what
the image only exposes:

```bash
echo "published: $(docker port my-site)"
echo "exposed:   $(docker inspect my-site --format '{{json .Config.ExposedPorts}}')"
docker ps --filter name=my-site --format 'PORTS column: {{.Ports}}'
```

```text
published: 
exposed:   {"80/tcp":{}}
PORTS column: 80/tcp
```

`published` is empty: `EXPOSE` documented the port, and nobody published it. In `docker ps`, `80/tcp` without an
arrow means "exposed, not published"; a published port looks like `0.0.0.0:8080->80/tcp`.

## Fix it

Publish the port when the container is started. Ports cannot be added to a running container: recreate it.

```bash
docker rm -f my-site > /dev/null
docker run -d --name my-site -p 127.0.0.1:8081:80 my-site:1.0 > /dev/null
docker port my-site
curl -s http://127.0.0.1:8081 | grep -o '<title>.*</title>'
```

```text
80/tcp -> 127.0.0.1:8081
<title>Welcome to nginx!</title>
```

Publishing on `127.0.0.1` keeps a development server private to your computer. On a server, Docker's published ports
bypass many host firewall rules, so publish only what must be public.
