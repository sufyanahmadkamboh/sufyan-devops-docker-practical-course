<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 130 · Production Dockerfile · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-130 examples/node-api
cp 18-production/130-production-dockerfile/examples/before/Dockerfile ~/docker-practice/lesson-130/Dockerfile.before
cp 18-production/130-production-dockerfile/examples/before/start.sh ~/docker-practice/lesson-130/
cp 18-production/130-production-dockerfile/examples/final/Dockerfile 18-production/130-production-dockerfile/examples/final/.dockerignore ~/docker-practice/lesson-130/
cd ~/docker-practice/lesson-130
ls -A
```

## Demonstration

```bash
docker build -q -f Dockerfile.before -t api:before . > /dev/null
docker build -q -t api:final . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' api
```

```bash
for image in api:before api:final; do
  docker image inspect "$image" --format "$image: user={{.Config.User}} workdir={{.Config.WorkingDir}} cmd={{json .Config.Cmd}}"
done
```

```bash
docker image inspect api:final --format '{{json .Config.Labels}}'
docker run -d --name api-final api:final > /dev/null
```

```bash
docker inspect api-final --format '{{.State.Health.Status}}'
```

## Hands-on lab

```bash
docker run --rm api:final sh -c 'echo hacked >> /app/server.js' 2>&1 || true
docker run --rm api:before sh -c 'echo hacked >> /server.js && echo "before: changed"'
```

## Break it

```bash
docker run -d --name api-before api:before > /dev/null
sleep 2
docker stop api-before api-final > /dev/null
docker inspect api-before api-final --format '{{.Name}}: exit code {{.State.ExitCode}}' | tr -d /
```

## Troubleshoot it

```bash
docker start api-before api-final > /dev/null
sleep 2
docker top api-before -o pid,args
docker top api-final -o pid,args
```

## Fix it

```bash
cd ~/docker-practice/lesson-130
grep '^CMD' Dockerfile
grep SIGTERM server.js
```

```bash
cd ~/docker-practice/lesson-130
sed 's|^node server.js|exec node server.js|' start.sh > start.new && mv start.new start.sh
docker rm -f api-before > /dev/null
docker build -q -f Dockerfile.before -t api:before . > /dev/null
docker run -d --name api-before api:before > /dev/null
sleep 2
docker top api-before -o pid,args
docker stop api-before > /dev/null
docker inspect api-before --format '{{.Name}}: exit code {{.State.ExitCode}}' | tr -d /
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-130
printf 'ARG VERSION=dev\nLABEL org.opencontainers.image.version=$VERSION\n' >> Dockerfile
docker build -q --build-arg VERSION=1.2.0 -t api:1.2.0 . > /dev/null
docker image inspect api:1.2.0 --format '{{index .Config.Labels "org.opencontainers.image.version"}}'
```

## Cleanup

```bash
docker rm -f api-before api-final > /dev/null
docker image rm -f api:before api:final api:1.2.0 > /dev/null
rm -rf ~/docker-practice/lesson-130
```
