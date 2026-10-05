<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 133 · Production configuration · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A new colleague deploys the web server for another environment and mounts the configuration file to a slightly wrong
path:

```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 -v "$(pwd)/default.conf:/etc/nginx/default.conf:ro" nginx:1.30-alpine > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<title>"
curl -sI http://localhost:8080/ | grep -ci x-environment || true
```

```text
<title>Welcome to nginx!</title>
0
```

No error anywhere: the container is running, and it serves the Nginx welcome page without the `X-Environment` header.

## Troubleshoot it

A configuration that is silently ignored is the hardest kind of mistake. Ask both sides: where did Docker mount the
file, and which configuration is Nginx actually using?

```bash
docker inspect web --format '{{range .Mounts}}mounted at {{.Destination}} (writable: {{.RW}}){{println}}{{end}}'
docker exec web nginx -T 2>/dev/null | grep "configuration file"
```

```text
mounted at /etc/nginx/default.conf (writable: false)

# configuration file /etc/nginx/nginx.conf:
# configuration file /etc/nginx/mime.types:
# configuration file /etc/nginx/conf.d/default.conf:
```

The file was mounted to `/etc/nginx/default.conf`, but Nginx only loads `/etc/nginx/nginx.conf` and the files it
includes from `/etc/nginx/conf.d/`. `nginx -T` prints the complete configuration Nginx has loaded, with the name of
every file: ours is not among them.

## Fix it

Mount the file to the path the application reads, and verify the loaded configuration, not just the running
container:

```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 -v "$(pwd)/default.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
sleep 1
docker exec web nginx -T 2>/dev/null | grep "configuration file /etc/nginx/conf.d/default.conf"
curl -sI http://localhost:8080/ | grep -i x-environment
```
