<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 036 · The build context · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-036 examples/node-api 05-builds/036-build-context/examples/shared
cp 05-builds/036-build-context/examples/Dockerfile* ~/docker-practice/lesson-036/node-api/
cd ~/docker-practice/lesson-036/node-api
ls . ../shared
```

## Demonstration

```bash
docker build --no-cache -t ctx-api:1.0 . 2>&1 | grep 'transferring context' | tail -1
```

```bash
head -c 50000000 /dev/zero > debug.log
docker build --no-cache -t ctx-api:1.0 . 2>&1 | grep 'transferring context' | tail -1
```

```bash
cat Dockerfile.all
docker build --no-cache -f Dockerfile.all -t ctx-api:all . 2>&1 | grep 'transferring context' | tail -1
```

```bash
docker run --rm ctx-api:all ls -lh /app/debug.log
docker image ls ctx-api
```

```bash
rm debug.log
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-036/node-api
docker build -f Dockerfile -t ctx-api:parent .. 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

## Break it

```bash
cd ~/docker-practice/lesson-036/node-api
docker build -f Dockerfile.config -t ctx-api:config . 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
ls ../shared/config.json
ls ./shared/config.json 2>&1 || true
```

## Fix it

```bash
cd ~/docker-practice/lesson-036
grep COPY node-api/Dockerfile.fixed
```

```bash
docker build -q -f node-api/Dockerfile.fixed -t ctx-api:config . > /dev/null
docker run --rm ctx-api:config cat /app/config.json
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-036/node-api
echo "not for images" > ../../secret-note.txt
printf 'FROM alpine:3.23\nCOPY ../../secret-note.txt ./\n' | docker build -f - -t ctx-api:secret . 2>&1 | grep -o '"/secret-note.txt": not found' | head -1
test "${PIPESTATUS[1]}" -eq 0
```

## Cleanup

```bash
docker image rm -f ctx-api:1.0 ctx-api:all ctx-api:config > /dev/null
rm -rf ~/docker-practice/lesson-036 ~/docker-practice/secret-note.txt
```
