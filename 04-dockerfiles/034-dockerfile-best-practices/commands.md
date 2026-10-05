<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 034 · Dockerfile best practices · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-034 examples/node-api
cp 04-dockerfiles/034-dockerfile-best-practices/examples/Dockerfile.* ~/docker-practice/lesson-034/
cd ~/docker-practice/lesson-034
mkdir -p notes && echo "meeting notes, not for the image" > notes/todo.md
ls -A
```

## Demonstration

```bash
docker build -q -f Dockerfile.before -t cafe-api:before . > /dev/null
docker build -q -f Dockerfile.after -t cafe-api:after . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' cafe-api
```

```bash
for v in before after; do
  echo "$v: $(docker run --rm cafe-api:$v whoami), files in /app: $(docker run --rm cafe-api:$v ls -A /app | tr '\n' ' ')"
done
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-034
sed -i.bak 's/Hello from Node.js/Hello from the cafe/' server.js && rm server.js.bak
docker build --progress=plain -f Dockerfile.after -t cafe-api:after . 2>&1 | grep -A1 'RUN npm ci' | grep -q CACHED && echo "after: npm ci CACHED"
docker build --progress=plain -f Dockerfile.before -t cafe-api:before . 2>&1 | grep -A1 'RUN npm install' | grep -q CACHED || echo "before: npm install ran again"
```

## Break it

```bash
docker build --check -f Dockerfile.before . 2>&1
```

## Troubleshoot it

```bash
docker image inspect --format '{{json .Config.Cmd}}' cafe-api:before
```

## Fix it

```bash
docker build --check -f Dockerfile.after . 2>&1 | tail -1
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-034
sed -i.bak 's/^CMD node server.js$/CMD ["node", "server.js"]/' Dockerfile.before && rm Dockerfile.before.bak
printf 'notes/\nDockerfile*\nnode_modules\n' > Dockerfile.before.dockerignore
docker build --check -f Dockerfile.before . 2>&1 | tail -1
docker build -q -f Dockerfile.before -t cafe-api:before . > /dev/null
echo "files in /app: $(docker run --rm cafe-api:before ls -A /app | tr '\n' ' ')"
```

## Cleanup

```bash
docker image rm -f cafe-api:before cafe-api:after > /dev/null
rm -rf ~/docker-practice/lesson-034
```
