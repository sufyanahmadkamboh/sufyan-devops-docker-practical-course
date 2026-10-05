<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 033 · USER · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-033 04-dockerfiles/033-user/examples
cd ~/docker-practice/lesson-033
cat take-order.sh
```

## Demonstration

```bash
docker run --rm alpine:3.23 id
```

```bash
docker run --rm --user node node:24-alpine id
```

```bash
printf 'FROM alpine:3.23\nRUN addgroup -S cafe && adduser -S -G cafe -u 10001 appuser\nUSER appuser\nCMD ["id"]\n' > Dockerfile.id
docker build -q -f Dockerfile.id -t user-demo:id . > /dev/null
docker run --rm user-demo:id
docker image inspect --format 'image user: {{.Config.User}}' user-demo:id
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-033
docker build -q -f Dockerfile.fixed -t orders:1.0 . > /dev/null
docker run --rm orders:1.0 cappuccino
docker run --rm --entrypoint sh orders:1.0 -c './take-order.sh latte > /dev/null; ls -l /app/data'
```

## Break it

```bash
docker build -q -f Dockerfile.broken -t orders:broken . > /dev/null
docker run --rm orders:broken espresso
```

## Troubleshoot it

```bash
docker run --rm --entrypoint sh orders:broken -c 'id; ls -ld /app; ls -l /app'
```

## Fix it

```bash
diff Dockerfile.broken Dockerfile.fixed || true
docker build -q -f Dockerfile.fixed -t orders:fixed . > /dev/null
docker run --rm orders:fixed espresso
```

## Practice challenge

```bash
docker run --rm --entrypoint sh orders:fixed -c '
  (echo "# changed" >> /app/take-order.sh) 2>/dev/null && echo "script: changed" || echo "script: Permission denied"
  touch /app/data/test && echo "data: ok"'
```

## Cleanup

```bash
docker image rm -f user-demo:id orders:1.0 orders:broken orders:fixed > /dev/null
rm -rf ~/docker-practice/lesson-033
```
