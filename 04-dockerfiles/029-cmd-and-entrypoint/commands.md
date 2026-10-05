<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 029 · CMD and ENTRYPOINT together · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-029 04-dockerfiles/028-entrypoint/examples
cd ~/docker-practice/lesson-029
ls
```

## Demonstration

```bash
cat > Dockerfile <<'EOF'
FROM alpine:3.23
COPY menu.csv /app/
COPY --chmod=0755 price.sh /usr/local/bin/price
ENTRYPOINT ["price"]
CMD ["espresso"]
EOF
docker build -q -t price:2.0 . > /dev/null
echo "default:    $(docker run --rm price:2.0)"
echo "cappuccino: $(docker run --rm price:2.0 cappuccino)"
```

```bash
printf 'FROM alpine:3.23\nENTRYPOINT ["ping", "-c", "2"]\nCMD ["localhost"]\n' > Dockerfile.ping
docker build -q -f Dockerfile.ping -t pinger . > /dev/null
docker run --rm pinger
```

## Hands-on lab

```bash
docker run --rm pinger 127.0.0.1
docker image inspect --format '{{json .Config.Entrypoint}} {{json .Config.Cmd}}' pinger
```

## Break it

```bash
printf 'FROM alpine:3.23\nCOPY menu.csv /app/\nCOPY --chmod=0755 price.sh /usr/local/bin/price\nENTRYPOINT price\nCMD ["espresso"]\n' > Dockerfile.shell
docker build -q -f Dockerfile.shell -t price:shell . > /dev/null 2>&1
docker run --rm price:shell cappuccino
```

## Troubleshoot it

```bash
docker run --name price-shell price:shell cappuccino > /dev/null 2>&1 || true
docker container inspect --format 'path={{.Path}} args={{json .Args}}' price-shell
docker rm price-shell > /dev/null
docker build --check -f Dockerfile.shell . 2>&1 | grep -o "WARNING: [A-Za-z]*"
```

## Fix it

```bash
sed -i.bak 's/^ENTRYPOINT price$/ENTRYPOINT ["price"]/' Dockerfile.shell && rm Dockerfile.shell.bak
docker build -q -f Dockerfile.shell -t price:shell . > /dev/null
docker run --rm price:shell cappuccino
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-029
printf '#!/bin/sh\nset -e\necho "preparing the cafe..."\nexec "$@"\n' > docker-entrypoint.sh
cat > Dockerfile.script <<'EOF'
FROM alpine:3.23
COPY menu.csv /app/
COPY --chmod=0755 price.sh /usr/local/bin/price
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["price", "espresso"]
EOF
docker build -q -f Dockerfile.script -t price:script . > /dev/null
docker run --rm price:script
docker run --rm price:script price "flat white"
```

## Cleanup

```bash
docker image rm -f price:2.0 price:shell price:script pinger > /dev/null
rm -rf ~/docker-practice/lesson-029
```
