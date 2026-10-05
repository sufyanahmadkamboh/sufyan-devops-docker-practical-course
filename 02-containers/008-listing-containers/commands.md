<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 008 · Listing containers · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker run -d --name web nginx:1.30-alpine > /dev/null
docker run --name job-ok alpine:3.23 true
docker run --name job-failed alpine:3.23 sh -c 'exit 3' || true
docker create --name not-started alpine:3.23 echo hi > /dev/null
echo done
```

## Demonstration

```bash
docker ps
```

```bash
docker ps -a
```

```bash
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

```bash
docker ps -a --filter status=exited --format '{{.Names}}'
```

```bash
docker ps -aq --filter status=exited | wc -l | tr -d ' '
```

## Hands-on lab

```bash
docker ps -a --filter ancestor=alpine:3.23 --no-trunc --format 'table {{.Names}}\t{{.Command}}'
```

## Break it

```bash
docker ps -a --filter status=stopped
```

## Fix it

```bash
docker ps -a --filter status=exited --format '{{.Names}}: {{.Status}}'
```

## Practice challenge

```bash
docker ps -a --filter exited=3 --format '{{.Names}}: {{.Status}}'
docker ps -a -s --format 'table {{.Names}}\t{{.Size}}'
```

## Cleanup

```bash
docker rm -f web job-ok job-failed not-started > /dev/null
```
