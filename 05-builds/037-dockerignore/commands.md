<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 037 · .dockerignore · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-037 examples/node-api
cp 05-builds/037-dockerignore/examples/* ~/docker-practice/lesson-037/
cd ~/docker-practice/lesson-037
printf 'API_TOKEN=example-token-change-me\n' > .env
mkdir -p node_modules/left-pad logs/debug
echo "module.exports = () => 'local copy'" > node_modules/left-pad/index.js
echo "debug output" > logs/debug/app.log
ls -a
```

## Demonstration

```bash
docker build -q -t ignore-demo:before . > /dev/null
docker run --rm ignore-demo:before ls -a /app
```

```bash
docker run --rm ignore-demo:before cat /app/.env
```

```bash
printf '.env\nnode_modules\nlogs\nDockerfile*\ndockerignore.example\n.dockerignore\n' > .dockerignore
docker build -q -t ignore-demo:after . > /dev/null
docker run --rm ignore-demo:after ls -a /app
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-037
cp dockerignore.example .dockerignore
docker build -q -t ignore-demo:lab . > /dev/null
docker run --rm ignore-demo:lab ls -a /app
docker run -d --name ignore-api ignore-demo:lab > /dev/null
sleep 1
docker logs ignore-api
docker rm -f ignore-api > /dev/null
```

## Break it

```bash
cd ~/docker-practice/lesson-037
printf '.env\nnode_modules\n*.log\n' > .dockerignore
docker build -q -t ignore-demo:logs . > /dev/null
docker run --rm ignore-demo:logs find /app/logs -type f
```

## Troubleshoot it

```bash
find . -name '*.log'
```

## Fix it

```bash
printf '.env\nnode_modules\n**/*.log\n' > .dockerignore
docker build -q -t ignore-demo:logs . > /dev/null
[ -z "$(docker run --rm ignore-demo:logs find /app -name '*.log')" ] && echo "no log files in the image"
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-037
printf '*\n!server.js\n!package.json\n' > .dockerignore
docker build -q -t ignore-demo:allow . > /dev/null
docker run --rm ignore-demo:allow ls /app
```

## Cleanup

```bash
docker image rm -f ignore-demo:before ignore-demo:after ignore-demo:lab ignore-demo:logs ignore-demo:allow > /dev/null
rm -rf ~/docker-practice/lesson-037
```
