<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 044 · Containerizing a PHP application · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The PHP container crashes and is removed while Nginx gets restarted, a common situation during a deployment:

```bash
docker rm -f php web > /dev/null
docker run -d --name web --network php-net -p 8088:8080 \
  -v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
```

It starts, and a few seconds later:

```bash
docker ps -a --filter name=web --format '{{.Names}}: {{.Status}}'
```

```text
web: Exited (1) 4 seconds ago
```

## Troubleshoot it

Nginx itself exited. Its log says why:

```bash
docker logs web 2>&1 | grep emerg
```

```text
2026/10/05 17:07:08 [emerg] 1#1: host not found in upstream "php" in /etc/nginx/conf.d/default.conf:8
nginx: [emerg] host not found in upstream "php" in /etc/nginx/conf.d/default.conf:8
```

`host not found in upstream "php"`: Nginx resolves the host names in `fastcgi_pass` **when it starts**. No container
named `php` exists on `php-net`, Docker's DNS has no answer (after a few seconds of trying, which is why the container
was `Up` at first), and Nginx refuses to start with an invalid configuration.
Check what is on the network:

```bash
docker network inspect php-net --format '{{range .Containers}}{{.Name}} {{end}}'
```

## Fix it

Start the backend first, then the proxy (Docker Compose expresses this order with `depends_on`, lesson 068):

```bash
docker rm -f web > /dev/null
docker run -d --name php --network php-net php-app:1.0 > /dev/null
docker run -d --name web --network php-net -p 8088:8080 \
  -v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
sleep 2
curl -s http://localhost:8088/
```
