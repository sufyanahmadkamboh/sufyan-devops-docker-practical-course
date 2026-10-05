<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 055 · Named volumes · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker volume create app-data
docker run --rm -v app-data:/data alpine:3.23 sh -c 'echo "order 1001: 2 coffees" > /data/orders.txt'
```

```bash
docker run --rm -v app-data:/data busybox:1.37 cat /data/orders.txt
```

```bash
docker run -d --name writer -v app-data:/data alpine:3.23 sh -c 'echo "order 1002: 1 tea" >> /data/orders.txt; sleep 300' > /dev/null
sleep 1
docker run --rm -v app-data:/data:ro busybox:1.37 cat /data/orders.txt
```

## Hands-on lab

```bash
docker volume ls --filter name=app-data
docker ps -a --filter volume=app-data --format '{{.Names}} ({{.Status}})'
```

## Break it

```bash
docker volume rm app-data 2>&1
```

## Troubleshoot it

```bash
docker ps -a --filter volume=app-data --format '{{.ID}} {{.Names}} {{.Status}}'
```

## Fix it

```bash
docker rm -f writer > /dev/null
docker volume rm app-data > /dev/null && echo "volume removed"
```

## Practice challenge

```bash
mkdir -p ~/docker-practice/lesson-055 && cd ~/docker-practice/lesson-055
docker run --rm -v menu:/data alpine:3.23 sh -c 'echo "espresso 2.50" > /data/menu.txt'
docker run --rm -v menu:/data:ro -v "$(pwd):/backup" alpine:3.23 tar -cf /backup/menu.tar -C /data .
tar -tf menu.tar
```

## Cleanup

```bash
docker volume rm menu > /dev/null
rm -rf ~/docker-practice/lesson-055
```
