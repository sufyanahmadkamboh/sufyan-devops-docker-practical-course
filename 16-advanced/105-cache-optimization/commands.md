<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 105 · Build cache optimization · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-105 examples/python-api
cp 16-advanced/105-cache-optimization/examples/* ~/docker-practice/lesson-105/
bash scripts/lab.sh lesson-105-node examples/node-api
cd ~/docker-practice/lesson-105
ls
```

## Demonstration

```bash
sh build-steps.sh -f Dockerfile.before -t cafe-api:before . > /dev/null
sh build-steps.sh -f Dockerfile.before -t cafe-api:before .
```

```bash
echo "# change 1" >> app.py
sh build-steps.sh -f Dockerfile.before -t cafe-api:before .
```

```bash
sh build-steps.sh -f Dockerfile.after -t cafe-api:after . > /dev/null
echo "# change 2" >> app.py
sh build-steps.sh -f Dockerfile.after -t cafe-api:after .
```

## Hands-on lab

```bash
echo "# pinned versions, reviewed" >> requirements.txt
docker build --progress plain -f Dockerfile.after -t cafe-api:after . 2>&1 | grep -m 3 'Using cached'
```

## Break it

```bash
head -4 Dockerfile.broken
```

```bash
sh build-steps.sh -f Dockerfile.broken --build-arg BUILD_TIME=1001 -t cafe-api:broken . > /dev/null
sh build-steps.sh -f Dockerfile.broken --build-arg BUILD_TIME=1002 -t cafe-api:broken .
```

## Fix it

```bash
sh build-steps.sh -f Dockerfile.fixed --build-arg BUILD_TIME=1001 -t cafe-api:fixed . > /dev/null
sh build-steps.sh -f Dockerfile.fixed --build-arg BUILD_TIME=1002 -t cafe-api:fixed .
docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.created"}}' cafe-api:fixed
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-105-node
cp ~/docker-practice/lesson-105/build-steps.sh .
cat > Dockerfile <<'EOF'
FROM node:24-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev
COPY . .
USER node
CMD ["node", "server.js"]
EOF
sh build-steps.sh -t cafe-node:cache . > /dev/null
echo "// change" >> server.js
sh build-steps.sh -t cafe-node:cache .
```

## Cleanup

```bash
docker image rm -f cafe-api:before cafe-api:after cafe-api:broken cafe-api:fixed cafe-node:cache > /dev/null 2>&1 || true
docker buildx prune -f > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-105 ~/docker-practice/lesson-105-node
```
