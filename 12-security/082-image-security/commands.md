<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 082 · Image security: trusted, minimal, pinned, scanned · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
for image in python:3.14-slim python:3.14-alpine gcr.io/distroless/static-debian12:nonroot; do
  echo "$image $(docker image inspect --format '{{.Size}}' "$image" | awk '{printf "%.1f MB", $1/1000000}')"
done
```

```bash
docker create --name peek gcr.io/distroless/static-debian12:nonroot nothing-to-run > /dev/null
echo "$(docker export peek | tar -t | grep -vc '/$') files, for example:"
docker export peek | tar -t | grep -E '^etc/(passwd|group|ssl/certs/ca-certificates.crt)$'
docker export peek | tar -t | grep -E 'bin/(sh|bash|busybox)$' || echo "no shell in the image"
docker rm peek > /dev/null
```

```bash
docker run --rm alpine:3.23 apk list --installed 2>/dev/null | grep -E '^(libcrypto3|libssl3|musl)-'
```

```bash
docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23
```

```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23)
docker run --rm "$digest" grep VERSION_ID /etc/os-release
```

```bash
docker scout quickview alpine:3.23              # summary per severity; docker login first
docker scout cves --only-severity critical,high alpine:3.23
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image alpine:3.23
```

## Hands-on lab

```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' python:3.14-slim)
echo "$digest"
docker run --rm "$digest" python --version
```

## Break it

```bash
docker run --rm alpine@sha256:85fe1e81d6758c208f3e1eed 2>&1
```

## Troubleshoot it

```bash
printf '%s' 85fe1e81d6758c208f3e1eed | wc -c
```

## Fix it

```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23)
echo "${digest#*sha256:}" | tr -d '\n' | wc -c
docker run --rm "$digest" true && echo "digest reference works"
```

## Practice challenge

```bash
mkdir -p ~/docker-practice/lesson-082 && cd ~/docker-practice/lesson-082
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' python:3.14-slim)
printf 'FROM python:3.14-slim@%s\nCMD ["python", "--version"]\n' "${digest#*@}" > Dockerfile
head -1 Dockerfile | cut -c1-40
docker build -q -t pinned:1.0 . > /dev/null && docker image ls pinned --format '{{.Repository}}:{{.Tag}}'
```

## Cleanup

```bash
docker image rm -f pinned:1.0 > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-082
```
