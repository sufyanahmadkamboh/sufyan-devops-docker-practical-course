<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 054 · Bind mounts · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-054 examples/site
cd ~/docker-practice/lesson-054
mkdir site && mv index.html styles.css site/
ls site
```

## Demonstration

```bash
docker run -d --name site -p 8080:80 -v "$(pwd)/site:/usr/share/nginx/html:ro" nginx:1.30-alpine > /dev/null
curl -s http://localhost:8080 | grep -o '<h1>.*</h1>'
```

```bash
sed -i.bak 's|<h1>Welcome to the cafe</h1>|<h1>Welcome to the cafe</h1><p>Now open on Sundays</p>|' site/index.html && rm site/index.html.bak
curl -s http://localhost:8080 | grep -o '<p>Now open on Sundays</p>'
```

```bash
docker inspect site --format '{{range .Mounts}}{{.Type}} {{.Destination}} rw={{.RW}}{{end}}'
```

## Hands-on lab

```bash
docker exec site sh -c 'touch /usr/share/nginx/html/hacked.html' 2>&1 || true
```

## Break it

```bash
docker run -d --name site2 -p 8081:80 -v site:/usr/share/nginx/html nginx:1.30-alpine > /dev/null
curl -s http://localhost:8081 | grep -o '<title>.*</title>'
```

## Troubleshoot it

```bash
docker inspect site2 --format '{{range .Mounts}}{{.Type}} name={{.Name}} -> {{.Destination}}{{end}}'
docker volume ls --filter name=^site$
```

## Fix it

```bash
docker rm -f site2 > /dev/null
docker volume rm site > /dev/null
docker run -d --name site2 -p 8081:80 --mount type=bind,source="$(pwd)/site",target=/usr/share/nginx/html,readonly nginx:1.30-alpine > /dev/null
curl -s http://localhost:8081 | grep -o '<h1>.*</h1>'
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-054
printf 'server {\n  listen 80;\n  location / { return 200 "hello from my config\\n"; }\n}\n' > default.conf
docker run -d --name custom -p 8082:80 -v "$(pwd)/default.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
curl -s http://localhost:8082
```

## Cleanup

```bash
docker rm -f site site2 custom > /dev/null
rm -rf ~/docker-practice/lesson-054
```
