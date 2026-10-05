<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 006 · Your first container · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run hello-world
```

```bash
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

```bash
docker run --rm hello-world > /dev/null
echo "hello-world containers: $(docker ps -aq --filter ancestor=hello-world | wc -l | tr -d ' ')"
```

## Hands-on lab

```bash
docker run --rm busybox:1.37 echo "my first container"
echo "busybox containers: $(docker ps -aq --filter ancestor=busybox:1.37 | wc -l | tr -d ' ')"
```

## Break it

```bash
docker run hello-word 2>&1
```

## Troubleshoot it

```bash
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep hello
```

## Fix it

```bash
docker run --rm hello-world | grep "Hello from Docker"
```

## Practice challenge

```bash
docker run hello-world > /dev/null
docker run hello-world > /dev/null
echo "hello-world containers: $(docker ps -aq --filter ancestor=hello-world | wc -l | tr -d ' ')"
docker rm $(docker ps -aq --filter ancestor=hello-world) > /dev/null && echo "removed"
echo "hello-world containers: $(docker ps -aq --filter ancestor=hello-world | wc -l | tr -d ' ')"
```

## Cleanup

```bash
docker rm -f $(docker ps -aq --filter ancestor=hello-world) > /dev/null 2>&1 || true
```
