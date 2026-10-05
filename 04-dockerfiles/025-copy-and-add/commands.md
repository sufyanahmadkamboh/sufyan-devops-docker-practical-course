<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 025 · COPY and ADD · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-025 04-dockerfiles/025-copy-and-add/examples
cd ~/docker-practice/lesson-025/menu-service
ls -R
```

## Demonstration

```bash
cat > Dockerfile <<'EOF'
FROM alpine:3.23
WORKDIR /app
COPY menu.csv .
COPY public/ public/
CMD ["find", "/app", "-type", "f"]
EOF
docker build -q -t copy-demo . > /dev/null
docker run --rm copy-demo
```

```bash
printf 'FROM alpine:3.23\nCOPY --chown=nobody:nobody menu.csv /app/\nCMD ["ls", "-l", "/app"]\n' > Dockerfile.chown
docker build -q -f Dockerfile.chown -t copy-demo:chown . > /dev/null
docker run --rm copy-demo:chown
```

```bash
tar -cf assets.tar public
printf 'FROM alpine:3.23\nCOPY assets.tar /copy/\nADD assets.tar /add/\n' > Dockerfile.add
docker build -q -f Dockerfile.add -t copy-demo:add . > /dev/null
echo "COPY keeps:  $(docker run --rm copy-demo:add ls /copy)"
echo "ADD unpacks: $(docker run --rm copy-demo:add find /add -type f | tr '\n' ' ')"
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-025/menu-service
printf 'FROM nginx:1.30-alpine\nCOPY public/ /usr/share/nginx/html/\n' > Dockerfile.site
docker build -q -f Dockerfile.site -t copy-demo:site . > /dev/null
docker run -d --name copy-site -p 8080:80 copy-demo:site > /dev/null && echo "started"
```

```bash
curl -s http://localhost:8080
```

## Break it

```bash
printf 'FROM alpine:3.23\nWORKDIR /app\nCOPY menu.csv .\nCOPY ../shared/config.json .\n' > Dockerfile.config
docker build -f Dockerfile.config -t copy-demo:config . 2>&1 | grep -E '>>>|ERROR'
```

## Troubleshoot it

```bash
ls -R .
```

## Fix it

```bash
cd ~/docker-practice/lesson-025
printf 'FROM alpine:3.23\nWORKDIR /app\nCOPY menu-service/menu.csv .\nCOPY shared/config.json .\nCMD ["cat", "config.json"]\n' > menu-service/Dockerfile.config
docker build -q -f menu-service/Dockerfile.config -t copy-demo:config . > /dev/null
docker run --rm copy-demo:config
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-025/menu-service
tar -czf public.tar.gz public
printf 'FROM alpine:3.23\nADD public.tar.gz /srv/www/\n' > Dockerfile.targz
docker build -q -f Dockerfile.targz -t copy-demo:targz . > /dev/null
docker run --rm copy-demo:targz ls /srv/www/public/index.html
```

## Cleanup

```bash
docker rm -f copy-site > /dev/null
docker image rm -f copy-demo copy-demo:chown copy-demo:add copy-demo:site copy-demo:config copy-demo:targz > /dev/null
rm -rf ~/docker-practice/lesson-025
```
