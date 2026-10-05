<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 024 · WORKDIR · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-024 04-dockerfiles/024-workdir/examples
cd ~/docker-practice/lesson-024
ls
```

## Demonstration

```bash
cat > Dockerfile.demo <<'EOF'
FROM alpine:3.23
WORKDIR /app
COPY menu.csv .
RUN pwd && ls
WORKDIR data
RUN pwd
EOF
docker build --no-cache --progress=plain -f Dockerfile.demo -t workdir-demo . 2>&1 | grep -E '^#[0-9]+ [0-9.]+ '
docker run --rm workdir-demo pwd
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-024
docker build -q -f Dockerfile.fixed -t menu:1.0 . > /dev/null
docker run --rm menu:1.0
docker run --rm -w / menu:1.0 ls app
```

## Break it

```bash
cat Dockerfile.broken
docker build -q -f Dockerfile.broken -t menu:broken . > /dev/null
docker run --rm menu:broken
```

## Troubleshoot it

```bash
echo "workdir: [$(docker image inspect --format '{{.Config.WorkingDir}}' menu:broken)]"
docker run --rm menu:broken sh -c 'pwd; ls /app/menu.csv'
```

## Fix it

```bash
diff Dockerfile.broken Dockerfile.fixed || true
docker build -q -f Dockerfile.fixed -t menu:fixed . > /dev/null
docker run --rm menu:fixed
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-024
printf 'FROM alpine:3.23\nWORKDIR /srv/cafe\nWORKDIR menu\nCOPY menu.csv .\nCMD ["wc", "-l", "menu.csv"]\n' > Dockerfile.challenge
docker build -q -f Dockerfile.challenge -t menu:challenge . > /dev/null
docker run --rm menu:challenge
```

## Cleanup

```bash
docker image rm -f workdir-demo menu:1.0 menu:broken menu:fixed menu:challenge > /dev/null
rm -rf ~/docker-practice/lesson-024
```
