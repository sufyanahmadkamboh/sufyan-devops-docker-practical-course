<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 015 · Running commands in containers (exec) · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker run -d --name web -p 8080:80 -e SHOP_MODE=demo nginx:1.30-alpine
docker ps --format '{{.Names}}: {{.Status}}'
```

## Demonstration

```bash
docker exec web nginx -v 2>&1
docker exec web cat /etc/alpine-release | sed 's/^/Alpine /'
```

```bash
docker exec web ps -o pid,user,args
```

```bash
docker exec web env | grep -E '^(SHOP_MODE|NGINX_VERSION|HOSTNAME)='
```

```bash
docker exec web wget -qO- http://localhost | grep '<title>'
```

```bash
docker exec -it web sh
```

## Hands-on lab

```bash
docker exec web sh -c 'echo "<h1>Changed with exec</h1>" > /usr/share/nginx/html/index.html'
curl -s http://localhost:8080
```

## Break it

```bash
docker exec web bash 2>&1
```

## Troubleshoot it

```bash
docker exec web cat /etc/shells
```

## Fix it

```bash
docker exec web sh -c 'echo "inside the container, as $(whoami), in $(pwd)"'
```

## Practice challenge

```bash
docker exec web nginx -t 2>&1
docker exec web ps -o user,args | grep 'worker process' | head -1
```

## Cleanup

```bash
docker rm -f web > /dev/null
```
