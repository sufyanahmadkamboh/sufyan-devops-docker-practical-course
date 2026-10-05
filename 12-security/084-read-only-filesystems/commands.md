<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 084 · Read-only file systems · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run --rm alpine:3.23 sh -c 'echo "attacker was here" > /etc/motd && echo "written to /etc/motd"'
```

```bash
docker run --rm --read-only alpine:3.23 sh -c 'echo "attacker was here" > /etc/motd'
```

```bash
docker run --rm --read-only --tmpfs /tmp alpine:3.23 sh -c 'echo data > /tmp/scratch && echo "scratch ok"; grep " /tmp " /proc/mounts'
```

## Hands-on lab

```bash
docker run -d --name web-rw nginx:1.30-alpine > /dev/null
sleep 2
docker diff web-rw
docker rm -f web-rw > /dev/null
```

## Break it

```bash
docker run -d --name web-ro --read-only -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web-ro"
```

```bash
docker ps -a --filter name=web-ro --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

```bash
docker logs web-ro 2>&1 | tail -2
```

## Fix it

```bash
docker rm -f web-ro > /dev/null
docker run -d --name web-ro --read-only --tmpfs /var/cache/nginx --tmpfs /run -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web-ro"
```

```bash
curl -s http://localhost:8080/ | grep -o '<title>.*</title>'
```

```bash
docker exec web-ro sh -c 'echo hacked > /usr/share/nginx/html/index.html' 2>&1 || true
```

## Practice challenge

```bash
docker run -d --name py-ro --read-only --tmpfs /srv -w /srv -p 8081:8081 python:3.14-alpine python -m http.server 8081 > /dev/null && echo "started py-ro"
```

```bash
docker exec py-ro sh -c 'echo "hello from tmpfs" > /srv/hello.txt'
curl -s http://localhost:8081/hello.txt
```

## Cleanup

```bash
docker rm -f web-rw web-ro py-ro > /dev/null 2>&1 || true
```
