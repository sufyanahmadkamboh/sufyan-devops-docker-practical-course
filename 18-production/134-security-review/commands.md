<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 134 · Security review · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-134 examples/node-api 18-production/134-security-review/examples/before 18-production/134-security-review/examples/broken 18-production/134-security-review/examples/after
cd ~/docker-practice/lesson-134
cp node-api/* before/ && cp node-api/* after/
mkdir -p after/secrets && printf 'example-password-change-me' > after/secrets/db_password.txt
docker build -q -t review-api:before before/ > /dev/null
ls
```

## Demonstration

```bash
cd ~/docker-practice/lesson-134
grep FROM before/Dockerfile
docker run --rm review-api:before ls / | tr '\n' ' ' && echo
```

```bash
echo "user=$(docker image inspect review-api:before --format '{{.Config.User}}')" | sed 's/user=$/user=root (none set)/'
```

```bash
docker image inspect review-api:before --format '{{range .Config.Env}}{{println .}}{{end}}' | grep PASSWORD
docker history --no-trunc --format '{{.CreatedBy}}' review-api:before | grep -o 'NPM_TOKEN=[^ ]*' | head -1
```

```bash
docker run --rm review-api:before sh -c 'command -v curl; command -v bash'
docker image inspect review-api:before --format 'cmd={{json .Config.Cmd}} healthcheck={{.Config.Healthcheck}}'
```

```bash
docker compose -f before/compose.yaml config | grep -E 'privileged|docker.sock|published|PASSWORD'
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-134
docker build -q -t review-api:after after/ > /dev/null
echo "user=$(docker image inspect review-api:after --format '{{.Config.User}}')"
docker image inspect review-api:after --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -c PASSWORD || true
echo "tools=$(docker run --rm review-api:after sh -c 'command -v curl || command -v bash' || echo none)"
docker image inspect review-api:after --format 'cmd={{json .Config.Cmd}} healthcheck={{json .Config.Healthcheck.Test}}'
```

## Break it

```bash
cd ~/docker-practice/lesson-134
cp broken/compose.yaml after/compose.broken.yaml
docker compose -p review -f after/compose.broken.yaml up -d --build --wait 2>&1 | tail -3 || true
docker compose -p review -f after/compose.broken.yaml ps -a --format '{{.Service}}: {{.State}}'
```

## Troubleshoot it

```bash
docker compose -p review -f after/compose.broken.yaml logs web 2>&1 | grep -i "read-only" | tail -2
```

## Fix it

```bash
cd ~/docker-practice/lesson-134
docker compose -p review -f after/compose.broken.yaml down -v > /dev/null 2>&1
grep -A3 "tmpfs" after/compose.yaml
docker compose -p review -f after/compose.yaml up -d --wait > /dev/null 2>&1
docker compose -p review -f after/compose.yaml ps --format '{{.Service}}: {{.State}} {{.Health}}'
curl -s http://localhost:8080/ && echo
```

```bash
cd ~/docker-practice/lesson-134
docker compose -p review -f after/compose.yaml exec web sh -c 'touch /etc/nginx/hacked' 2>&1 || true
```

## Practice challenge

```bash
digest=$(docker image inspect node:24-alpine --format '{{range .RepoDigests}}{{println .}}{{end}}' | head -1 | cut -d@ -f2)
echo "FROM node:24-alpine@$digest"
```

## Cleanup

```bash
cd ~/docker-practice/lesson-134
docker compose -p review -f after/compose.yaml down -v > /dev/null 2>&1
docker image rm -f review-api:before review-api:after > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-134
```
