<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 092 · HEALTHCHECK · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-092 14-observability/092-healthcheck/examples/broken 14-observability/092-healthcheck/examples/fixed
cd ~/docker-practice/lesson-092
cat fixed/Dockerfile
```

## Demonstration

```bash
docker run -d --name web --health-cmd 'wget -q --spider http://127.0.0.1/ || exit 1' \
  --health-interval 2s --health-retries 3 -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web"
```

```bash
docker ps --filter name=web --format '{{.Names}}: {{.Status}}'
```

```bash
docker inspect --format '{{.State.Health.Status}} {{.State.Health.FailingStreak}}' web
docker inspect --format '{{json (index .State.Health.Log 0)}}' web
```

## Hands-on lab

```bash
docker build -q -t cafe-web:health fixed > /dev/null
docker run -d --name web-fixed -p 8081:80 cafe-web:health > /dev/null && echo "started web-fixed"
```

```bash
docker ps --filter health=healthy --filter name=web-fixed --format '{{.Names}}: {{.Status}}'
```

## Break it

```bash
docker build -q -t cafe-web:broken-health broken > /dev/null
docker run -d --name web-broken -p 8082:80 cafe-web:broken-health > /dev/null && echo "started web-broken"
```

```bash
docker ps --filter name=web-broken --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

```bash
curl -s http://localhost:8082/ | grep -o '<title>.*</title>'
```

```bash
docker inspect --format '{{range .State.Health.Log}}{{.ExitCode}} {{.Output}}{{end}}' web-broken | tail -2
docker inspect --format '{{json .Config.Healthcheck.Test}}' web-broken
```

## Fix it

```bash
docker rm -f web-broken > /dev/null
docker run -d --name web-broken -p 8082:80 cafe-web:health > /dev/null && echo "started web-broken"
```

```bash
docker ps --filter name=web-broken --format '{{.Names}}: {{.Status}}'
```

## Practice challenge

```bash
docker exec web-fixed rm /usr/share/nginx/html/index.html && echo done
```

```bash
docker ps --filter name=web-fixed --format '{{.Names}}: {{.Status}}'
docker inspect --format '{{range .State.Health.Log}}{{.Output}}{{end}}' web-fixed | grep . | tail -1
```

## Cleanup

```bash
docker rm -f web web-fixed web-broken > /dev/null 2>&1 || true
docker image rm -f cafe-web:health cafe-web:broken-health > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-092
```
