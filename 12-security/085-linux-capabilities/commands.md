<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 085 · Linux capabilities · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-085 12-security/085-linux-capabilities/examples
cd ~/docker-practice/lesson-085
cat caps.sh | head -2
```

## Demonstration

```bash
docker run --rm -v "$(pwd)/caps.sh:/caps.sh:ro" alpine:3.23 sh /caps.sh
```

```bash
docker run --rm --cap-drop ALL -v "$(pwd)/caps.sh:/caps.sh:ro" alpine:3.23 sh /caps.sh
```

```bash
docker run --rm alpine:3.23 sh -c 'touch /tmp/f && chown nobody /tmp/f && echo "chown ok"'
docker run --rm --cap-drop ALL alpine:3.23 sh -c 'touch /tmp/f && chown nobody /tmp/f' 2>&1 || true
```

```bash
docker run --rm alpine:3.23 date -s '2030-01-01 00:00' 2>&1 || true
```

## Hands-on lab

```bash
docker run --rm --cap-drop ALL --cap-add CHOWN -v "$(pwd)/caps.sh:/caps.sh:ro" alpine:3.23 \
  sh -c 'sh /caps.sh; touch /tmp/f && chown nobody /tmp/f && echo "chown ok"'
```

## Break it

```bash
docker run -d --name web --cap-drop ALL -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web"
```

```bash
docker ps -a --filter name=web --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

```bash
docker logs web 2>&1 | tail -1
```

```bash
docker run --rm --cap-drop ALL alpine:3.23 sysctl net.ipv4.ip_unprivileged_port_start
```

## Fix it

```bash
docker rm -f web > /dev/null
docker run -d --name web --cap-drop ALL --cap-add CHOWN --cap-add SETUID --cap-add SETGID \
  --security-opt no-new-privileges -p 8080:80 nginx:1.30-alpine > /dev/null && echo "started web"
```

```bash
curl -s http://localhost:8080/ | grep -o '<title>.*</title>'
```

```bash
docker inspect --format 'add={{.HostConfig.CapAdd}} drop={{.HostConfig.CapDrop}}' web
```

## Practice challenge

```bash
docker run -d --name py --cap-drop ALL -p 8081:8081 python:3.14-alpine python -m http.server 8081 > /dev/null && echo "started py"
```

```bash
curl -s http://localhost:8081/ | grep -o '<title>.*</title>'
```

```bash
docker exec py grep CapEff /proc/1/status
```

## Cleanup

```bash
docker rm -f web py > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-085
```
