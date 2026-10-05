<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 007 · Images vs containers · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run --name red alpine:3.23 sh -c 'echo red > /data.txt'
docker run --name blue alpine:3.23 sh -c 'echo blue > /data.txt'
docker run --name plain alpine:3.23 true
docker ps -a --filter ancestor=alpine:3.23 --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

```bash
echo "red:";   docker container diff red
echo "blue:";  docker container diff blue
echo "plain:"; docker container diff plain
```

```bash
docker run --rm alpine:3.23 cat /data.txt 2>&1 || true
```

```bash
docker cp red:/data.txt ./red-data.txt
cat red-data.txt
rm red-data.txt
```

## Hands-on lab

```bash
docker run --name deleter alpine:3.23 rm /etc/motd
docker container diff deleter
docker run --rm alpine:3.23 ls /etc/motd
```

## Break it

```bash
docker commit red lesson-007:red > /dev/null
docker create --name from-red lesson-007:red cat /data.txt > /dev/null
docker image rm lesson-007:red
```

## Troubleshoot it

```bash
docker ps -a --filter ancestor=lesson-007:red --format '{{.Names}}: {{.Status}}'
```

## Fix it

```bash
docker rm from-red > /dev/null
docker image rm lesson-007:red
```

## Practice challenge

```bash
for n in one two three; do docker run -d --name "sleep-$n" alpine:3.23 sleep 300 > /dev/null; done
docker ps --filter name=sleep- --format '{{.Names}} {{.Image}}'
echo "$(docker ps -q --filter ancestor=alpine:3.23 | wc -l | tr -d ' ') running"
docker inspect --format '{{.Image}}' sleep-one sleep-two sleep-three | sort -u | wc -l | tr -d ' '
docker rm -f sleep-one sleep-two sleep-three > /dev/null
```

## Cleanup

```bash
docker rm -f red blue plain deleter > /dev/null
docker image rm -f lesson-007:red > /dev/null 2>&1 || true
```
