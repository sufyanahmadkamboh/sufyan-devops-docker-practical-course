<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 022 · Your first Dockerfile · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-022 examples/site
cd ~/docker-practice/lesson-022
ls
```

## Demonstration

```bash
cat > Dockerfile <<'EOF'
# The cafe website, served by Nginx
FROM nginx:1.30-alpine
COPY . /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF
cat Dockerfile
```

```bash
docker build -t cafe-site:1.0 . 2>&1 | grep -E '^#[0-9]+ \[|naming to'
```

```bash
docker run -d --name cafe-site -p 8080:80 cafe-site:1.0 > /dev/null && echo "cafe-site started"
```

```bash
curl -s http://localhost:8080 | grep '<h1>'
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-022
sed -i.bak 's|Welcome to the cafe|Welcome to the cafe, version 1.1|' index.html && rm index.html.bak
docker build -q -t cafe-site:1.1 . > /dev/null
docker run -d --name cafe-site-v11 -p 8081:80 cafe-site:1.1 > /dev/null && echo "lab ready"
```

```bash
curl -s http://localhost:8081 | grep '<h1>'
curl -s http://localhost:8080 | grep '<h1>'
```

## Break it

```bash
printf 'FROM nginx:1.30-alpine\nCOPPY . /usr/share/nginx/html/\n' > Dockerfile.broken
docker build -f Dockerfile.broken -t cafe-site:broken . 2>&1 | grep -E '>>>|ERROR'
```

## Troubleshoot it

```bash
docker image inspect cafe-site:broken > /dev/null 2>&1 || echo "no image cafe-site:broken"
```

## Fix it

```bash
sed -i.bak 's/^COPPY/COPY/' Dockerfile.broken && rm Dockerfile.broken.bak
docker build -q -f Dockerfile.broken -t cafe-site:fixed . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' cafe-site
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-022
printf 'FROM alpine:3.23\nCMD ["echo", "Hello from my first image"]\n' > Dockerfile.hello
docker build -q -f Dockerfile.hello -t hello-image:1.0 . > /dev/null
docker run --rm hello-image:1.0
```

## Cleanup

```bash
docker rm -f cafe-site cafe-site-v11 > /dev/null
docker image rm -f cafe-site:1.0 cafe-site:1.1 cafe-site:fixed hello-image:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-022
```
