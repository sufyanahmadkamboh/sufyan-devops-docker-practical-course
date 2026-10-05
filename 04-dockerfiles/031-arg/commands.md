<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 031 · ARG · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-031
cd ~/docker-practice/lesson-031
```

## Demonstration

```bash
cat > Dockerfile <<'EOF'
ARG ALPINE_VERSION=3.23
FROM alpine:${ALPINE_VERSION}
ARG VERSION=dev
RUN echo "cafe menu version $VERSION on Alpine $(cat /etc/alpine-release)" > /version
CMD ["cat", "/version"]
EOF
docker build -q --build-arg VERSION=1.4.0 -t menu-arg:1.4.0 . > /dev/null
docker build -q -t menu-arg:dev . > /dev/null
docker run --rm menu-arg:1.4.0
docker run --rm menu-arg:dev
```

```bash
docker run --rm menu-arg:1.4.0 sh -c 'echo "VERSION at run time: [$VERSION]"'
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-031
printf 'FROM alpine:3.23\nARG VERSION=dev\nENV APP_VERSION=$VERSION\n' > Dockerfile.env
docker build -q -f Dockerfile.env --build-arg VERSION=1.5.0 -t menu-arg:1.5.0 . > /dev/null
docker run --rm menu-arg:1.5.0 sh -c 'echo $APP_VERSION'
```

## Break it

```bash
cat > Dockerfile.scope <<'EOF'
ARG ALPINE_VERSION=3.23
ARG VERSION=dev
FROM alpine:${ALPINE_VERSION}
RUN echo "version [$VERSION]" > /version
CMD ["cat", "/version"]
EOF
docker build -q -f Dockerfile.scope --build-arg VERSION=1.4.0 -t menu-arg:scope . > /dev/null
docker run --rm menu-arg:scope
```

## Troubleshoot it

```bash
docker image history --no-trunc --format '{{.CreatedBy}}' menu-arg:scope | grep '^RUN'
```

## Fix it

```bash
awk '{ print } /^FROM / { print "ARG VERSION" }' Dockerfile.scope > Dockerfile.tmp && mv Dockerfile.tmp Dockerfile.scope
cat Dockerfile.scope
docker build -q -f Dockerfile.scope --build-arg VERSION=1.4.0 -t menu-arg:scope . > /dev/null
docker run --rm menu-arg:scope
docker image history --no-trunc --format '{{.CreatedBy}}' menu-arg:scope | grep '^RUN'
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-031
printf 'FROM alpine:3.23\nARG API_TOKEN\nRUN test -n "$API_TOKEN" && echo "downloading with the token"\n' > Dockerfile.leak
docker build -q -f Dockerfile.leak --build-arg API_TOKEN=example-token-123 -t menu-arg:leak . > /dev/null 2>&1
docker image history --no-trunc menu-arg:leak | grep -q example-token-123 && echo "leaked: yes"

printf 'example-token-123' > api_token.txt
cat > Dockerfile.secret <<'EOF'
FROM alpine:3.23
RUN --mount=type=secret,id=api_token \
    test -n "$(cat /run/secrets/api_token)" && echo "downloading with the token"
EOF
docker build -q -f Dockerfile.secret --secret id=api_token,src=api_token.txt -t menu-arg:secret . > /dev/null
docker image history --no-trunc menu-arg:secret | grep -q example-token-123 || echo "with a secret: not in the history"
rm api_token.txt
```

## Cleanup

```bash
docker image rm -f menu-arg:1.4.0 menu-arg:dev menu-arg:1.5.0 menu-arg:scope menu-arg:leak menu-arg:secret > /dev/null
rm -rf ~/docker-practice/lesson-031
```
