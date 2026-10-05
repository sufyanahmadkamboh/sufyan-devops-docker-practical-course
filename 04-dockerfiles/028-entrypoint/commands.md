<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 028 · ENTRYPOINT · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-028 04-dockerfiles/028-entrypoint/examples
cd ~/docker-practice/lesson-028
cat price.sh Dockerfile
```

## Demonstration

```bash
docker build -q -t price:1.0 . > /dev/null
docker run --rm price:1.0 espresso
docker run --rm price:1.0 "flat white"
```

```bash
docker run --rm price:1.0 tea || echo "exit status $?"
```

## Hands-on lab

```bash
docker run --rm price:1.0 cappuccino
docker image inspect --format '{{json .Config.Entrypoint}}' price:1.0
```

## Break it

```bash
docker run --rm price:1.0 sh
```

## Troubleshoot it

```bash
docker run --name price-check price:1.0 sh > /dev/null 2>&1 || true
docker container inspect --format 'path={{.Path}} args={{json .Args}}' price-check
docker rm price-check > /dev/null
```

## Fix it

```bash
docker run --rm --entrypoint sh price:1.0 -c 'ls /app/menu.csv /usr/local/bin/price'
```

## Practice challenge

```bash
docker run --rm --entrypoint wc price:1.0 -l /app/menu.csv
```

## Cleanup

```bash
docker image rm -f price:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-028
```
