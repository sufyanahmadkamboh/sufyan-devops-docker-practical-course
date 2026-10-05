<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 027 · CMD · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-027 04-dockerfiles/024-workdir/examples
cd ~/docker-practice/lesson-027
rm Dockerfile.*
ls
```

## Demonstration

```bash
cat > Dockerfile <<'EOF'
FROM alpine:3.23
WORKDIR /app
COPY menu.csv .
CMD ["cat", "menu.csv"]
EOF
docker build -q -t menu:cmd . > /dev/null
docker run --rm menu:cmd
```

```bash
docker run --rm menu:cmd wc -l menu.csv
```

```bash
docker image inspect --format '{{json .Config.Cmd}}' menu:cmd
```

```bash
printf 'FROM alpine:3.23\nCMD echo "shell form: $HOME"\n' > Dockerfile.shell
printf 'FROM alpine:3.23\nCMD ["echo", "exec form: $HOME"]\n' > Dockerfile.exec
docker build -q -f Dockerfile.shell -t cmd-form:shell . > /dev/null
docker build -q -f Dockerfile.exec -t cmd-form:exec . > /dev/null
docker run --rm cmd-form:shell
docker run --rm cmd-form:exec
```

## Hands-on lab

```bash
docker run --rm menu:cmd
docker run --rm menu:cmd head -2 menu.csv
docker run --rm menu:cmd grep cappuccino menu.csv
```

## Break it

```bash
printf "FROM alpine:3.23\nCMD ['echo', 'hello']\n" > Dockerfile.quotes
docker build -q -f Dockerfile.quotes -t cmd-form:quotes . > /dev/null
docker run --rm cmd-form:quotes
```

## Troubleshoot it

```bash
docker image inspect --format '{{json .Config.Cmd}}' cmd-form:quotes
```

```bash
docker build --check -f Dockerfile.quotes . 2>&1 | grep -A1 WARNING
```

## Fix it

```bash
printf 'FROM alpine:3.23\nCMD ["echo", "hello"]\n' > Dockerfile.quotes
docker build -q -f Dockerfile.quotes -t cmd-form:quotes . > /dev/null
docker run --rm cmd-form:quotes
docker image inspect --format '{{json .Config.Cmd}}' cmd-form:quotes
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-027
printf 'FROM alpine:3.23\nCMD ["echo", "first"]\nCMD ["echo", "second"]\n' > Dockerfile.twice
docker build -q -f Dockerfile.twice -t cmd-form:twice . > /dev/null 2>&1
docker run --rm cmd-form:twice
docker image inspect --format '{{json .Config.Cmd}}' cmd-form:twice
docker build --check -f Dockerfile.twice . 2>&1 | grep -o "WARNING: [A-Za-z]*"
```

## Cleanup

```bash
docker image rm -f menu:cmd cmd-form:shell cmd-form:exec cmd-form:quotes cmd-form:twice > /dev/null
rm -rf ~/docker-practice/lesson-027
```
