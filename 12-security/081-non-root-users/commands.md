<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 081 · Running as a non-root user · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-081 12-security/081-non-root-users/examples/before 12-security/081-non-root-users/examples/broken 12-security/081-non-root-users/examples/fixed
cd ~/docker-practice/lesson-081
ls
```

## Demonstration

```bash
docker run --rm alpine:3.23 id
```

```bash
docker build -q -t cafe-web:root before > /dev/null
docker run -d --name web-root -p 8080:8080 cafe-web:root > /dev/null
docker image ls cafe-web --format '{{.Repository}}:{{.Tag}}'
```

```bash
curl -s http://localhost:8080/
```

```bash
docker top web-root -o user,pid,args
```

## Hands-on lab

```bash
docker run --rm --user 65534:65534 alpine:3.23 sh -c 'id; touch /root/test 2>&1 || true'
```

## Break it

```bash
docker build -q -t cafe-web:broken broken > /dev/null
docker run -d --name web-broken -p 8081:8080 cafe-web:broken > /dev/null
docker image ls cafe-web --format '{{.Repository}}:{{.Tag}}'
```

```bash
docker ps -a --filter name=web-broken --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

```bash
docker logs web-broken 2>&1 | tail -1
```

```bash
docker run --rm --entrypoint sh cafe-web:broken -c 'id; ls -ld /app'
```

## Fix it

```bash
grep -n "USER\|chown" fixed/Dockerfile
```

```bash
docker rm -f web-broken > /dev/null
docker build -q -t cafe-web:fixed fixed > /dev/null
docker run -d --name web-fixed -p 8081:8080 cafe-web:fixed > /dev/null
docker image ls cafe-web --format '{{.Repository}}:{{.Tag}}'
```

```bash
curl -s http://localhost:8081/
docker exec web-fixed ls -l /app
```

## Practice challenge

```bash
docker exec web-fixed sh -c 'echo "# changed" >> /app/app.py' 2>&1 || true
docker exec web-root sh -c 'echo "# changed" >> /app/app.py && echo "root can change the code"'
```

## Cleanup

```bash
docker rm -f web-root web-broken web-fixed > /dev/null 2>&1 || true
docker image rm -f cafe-web:root cafe-web:broken cafe-web:fixed > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-081
```
