<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 030 · ENV · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-030 examples/node-api
cd ~/docker-practice/lesson-030
ls
grep -n "process.env" server.js
```

## Demonstration

```bash
cat > Dockerfile <<'EOF'
FROM node:24-alpine
WORKDIR /app
COPY . .
ENV PORT=3000 \
    GREETING="Hello from the cafe" \
    APP_VERSION=1.0.0
RUN echo "building version $APP_VERSION for port $PORT"
CMD ["node", "server.js"]
EOF
docker build --progress=plain -t cafe-api:env . 2>&1 | grep "building version"
docker run -d --name cafe-api -p 8080:3000 cafe-api:env > /dev/null
```

```bash
docker logs cafe-api
curl -s http://localhost:8080
```

```bash
docker run -d --name cafe-api-de -p 8081:3000 -e GREETING="Hallo aus dem Café" cafe-api:env > /dev/null && echo "lab ready"
```

```bash
curl -s http://localhost:8081
```

## Hands-on lab

```bash
docker image inspect --format '{{json .Config.Env}}' cafe-api:env
docker exec cafe-api-de env | grep -e GREETING -e PORT -e APP_VERSION
```

## Break it

```bash
cat > Dockerfile.v11 <<'EOF'
FROM node:24-alpine
WORKDIR /app
COPY . .
ENV PORT=3000
RUN export APP_VERSION=1.1.0
CMD ["node", "server.js"]
EOF
docker build -q -f Dockerfile.v11 -t cafe-api:1.1 . > /dev/null
docker run -d --name cafe-api-v11 -p 8082:3000 cafe-api:1.1 > /dev/null
docker container ls --format '{{.Names}} {{.Image}}' --filter name=cafe-api-v11
```

```bash
curl -s http://localhost:8082
```

## Troubleshoot it

```bash
docker exec cafe-api-v11 sh -c 'echo "APP_VERSION=${APP_VERSION:-(not set)}"' | sed 's/=(not set)/ is not set/'
docker image inspect --format '{{json .Config.Env}}' cafe-api:1.1
```

## Fix it

```bash
sed -i.bak 's/^RUN export APP_VERSION=1.1.0$/ENV APP_VERSION=1.1.0/' Dockerfile.v11 && rm Dockerfile.v11.bak
docker build -q -f Dockerfile.v11 -t cafe-api:1.1 . > /dev/null
docker rm -f cafe-api-v11 > /dev/null
docker run -d --name cafe-api-v11 -p 8082:3000 cafe-api:1.1 > /dev/null
docker container ls --format '{{.Names}} {{.Image}}' --filter name=cafe-api-v11
```

```bash
curl -s http://localhost:8082
```

## Practice challenge

```bash
docker run -d --name cafe-api-4000 -e PORT=4000 -p 8083:4000 cafe-api:env > /dev/null && echo "started"
```

```bash
docker logs cafe-api-4000
curl -s http://localhost:8083
```

## Cleanup

```bash
docker rm -f cafe-api cafe-api-de cafe-api-v11 cafe-api-4000 > /dev/null
docker image rm -f cafe-api:env cafe-api:1.1 > /dev/null
rm -rf ~/docker-practice/lesson-030
```
