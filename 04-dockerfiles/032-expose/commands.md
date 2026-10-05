<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 032 · EXPOSE · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-032 examples/node-api
cd ~/docker-practice/lesson-032
grep -n "listen" server.js
```

## Demonstration

```bash
cat > Dockerfile <<'EOF'
FROM node:24-alpine
WORKDIR /app
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
EOF
docker build -q -t cafe-api:expose . > /dev/null
docker image inspect --format '{{json .Config.ExposedPorts}}' cafe-api:expose
```

```bash
docker run -d --name cafe-api -P cafe-api:expose > /dev/null
docker port cafe-api
```

```bash
port=$(docker port cafe-api 3000/tcp | head -1 | sed 's/.*://')
curl -s "http://localhost:$port"
```

## Hands-on lab

```bash
docker run -d --name cafe-api-internal cafe-api:expose > /dev/null
echo "published: [$(docker port cafe-api-internal)]"
docker container ls --filter name=cafe-api-internal --format 'unpublished: {{.Ports}}'
```

## Break it

```bash
sed 's/^EXPOSE 3000$/EXPOSE 80/' Dockerfile > Dockerfile.wrong
docker build -q -f Dockerfile.wrong -t cafe-api:wrong-port . > /dev/null
docker run -d --name cafe-api-wrong -P cafe-api:wrong-port > /dev/null
sleep 2
port=$(docker port cafe-api-wrong 80/tcp | head -1 | sed 's/.*://')
curl -sS "http://localhost:$port" 2>&1 || echo "no response from the application"
```

## Troubleshoot it

```bash
docker port cafe-api-wrong
docker logs cafe-api-wrong
docker exec cafe-api-wrong wget -qO- http://127.0.0.1:3000
```

## Fix it

```bash
docker rm -f cafe-api-wrong > /dev/null
sed -i.bak 's/^EXPOSE 80$/EXPOSE 3000/' Dockerfile.wrong && rm Dockerfile.wrong.bak
docker build -q -f Dockerfile.wrong -t cafe-api:wrong-port . > /dev/null
docker run -d --name cafe-api-wrong -P cafe-api:wrong-port > /dev/null
docker port cafe-api-wrong
```

```bash
curl -s "http://localhost:$(docker port cafe-api-wrong 3000/tcp | head -1 | sed 's/.*://')"
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-032
cat > Dockerfile.port <<'EOF'
FROM node:24-alpine
ARG PORT=8000
WORKDIR /app
COPY . .
ENV PORT=$PORT
EXPOSE $PORT
CMD ["node", "server.js"]
EOF
docker build -q -f Dockerfile.port -t cafe-api:8000 . > /dev/null
docker run -d --name cafe-api-8000 -P cafe-api:8000 > /dev/null
docker port cafe-api-8000
```

```bash
curl -s "http://localhost:$(docker port cafe-api-8000 8000/tcp | head -1 | sed 's/.*://')"
```

## Cleanup

```bash
docker rm -f cafe-api cafe-api-internal cafe-api-wrong cafe-api-8000 > /dev/null
docker image rm -f cafe-api:expose cafe-api:wrong-port cafe-api:8000 > /dev/null
rm -rf ~/docker-practice/lesson-032
```
