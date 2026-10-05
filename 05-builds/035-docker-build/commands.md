<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 035 · docker build · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-035 examples/node-api
cp 05-builds/035-docker-build/examples/Dockerfile ~/docker-practice/lesson-035/
cd ~/docker-practice/lesson-035
ls
cat Dockerfile
```

## Demonstration

```bash
docker build -t node-api:1.0 . 2>&1 | grep -E '^#[0-9]+ \[|naming to|DONE' | tail -8
```

```bash
docker image ls node-api
```

```bash
docker run -d --name api -p 8080:3000 node-api:1.0 > /dev/null
docker ps --filter name=api --format '{{.Names}}: {{.Status}}'
```

```bash
curl -s http://localhost:8080/
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-035
docker build -q -t node-api:1.1 -t node-api:stable . > /dev/null
docker image ls node-api
```

## Break it

```bash
cd ~/docker-practice/lesson-035
mv Dockerfile Dockerfile.prod
docker build -t node-api:prod . 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
ls
```

## Fix it

```bash
docker build -q -f Dockerfile.prod -t node-api:prod . > /dev/null
docker image ls node-api
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-035
id=$(docker build -q -f Dockerfile.prod -t node-api:quiet .)
echo "$id"
[ "$id" = "$(docker image inspect --format '{{.Id}}' node-api:quiet)" ] && echo "same image"
```

## Cleanup

```bash
docker rm -f api > /dev/null
docker image rm -f node-api:1.0 node-api:1.1 node-api:stable node-api:prod node-api:quiet > /dev/null
rm -rf ~/docker-practice/lesson-035
```
