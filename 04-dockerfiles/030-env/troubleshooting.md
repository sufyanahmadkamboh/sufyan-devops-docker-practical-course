<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 030 · ENV · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Version 1.1 should report its version. A colleague sets it in a `RUN` step:

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

```text
{"message":"Hello from Node.js","hostname":"211012de846a","version":"dev"}
```

The API reports `dev`, its fallback when `APP_VERSION` is not set.

## Troubleshoot it

Ask the container for the variable, then the image:

```bash
docker exec cafe-api-v11 sh -c 'echo "APP_VERSION=${APP_VERSION:-(not set)}"' | sed 's/=(not set)/ is not set/'
docker image inspect --format '{{json .Config.Env}}' cafe-api:1.1
```

```text
APP_VERSION is not set
["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","NODE_VERSION=24.21.0","YARN_VERSION=1.22.22","PORT=3000"]
```

`RUN export …` set the variable in the shell of that one build step. The shell ended with the step, and only files are
saved in a layer, not a shell's variables. The image's environment comes from `ENV` instructions only (yours and the
base image's: `NODE_VERSION` comes from `node:24-alpine`).

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
