<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 076 · Docker Hub · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
short=$(docker image inspect alpine:3.23 --format '{{.Id}}')
full=$(docker image inspect docker.io/library/alpine:3.23 --format '{{.Id}}')
echo "alpine:3.23                    -> $short"
echo "docker.io/library/alpine:3.23  -> $full"
[ "$short" = "$full" ] && echo "same image"
```

```bash
docker image inspect nginx:1.30-alpine --format '{{index .RepoDigests 0}}'
```

```bash
digest=$(docker image inspect nginx:1.30-alpine --format '{{index .RepoDigests 0}}')
docker run --rm --entrypoint nginx "$digest" -v 2>&1
```

```bash
docker login -u YOUR_USER                 # paste the access token when asked for the password
docker tag cafe-api:1.0 YOUR_USER/cafe-api:1.0
docker push YOUR_USER/cafe-api:1.0
docker logout
```

## Hands-on lab

```bash
if grep -q '"auths"' ~/.docker/config.json 2> /dev/null && grep -q 'index.docker.io' ~/.docker/config.json; then
  echo "saved logins: Docker Hub"
else
  echo "saved logins: none for Docker Hub"
fi
```

## Break it

```bash
docker tag alpine:3.23 cafe-student/cafe-api:1.0
docker push cafe-student/cafe-api:1.0 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
echo "namespace in the image name: $(echo cafe-student/cafe-api:1.0 | cut -d/ -f1)"
grep -q 'index.docker.io' ~/.docker/config.json 2> /dev/null && echo "logged in: yes" || echo "logged in: no"
```

## Fix it

```bash
echo "$DOCKERHUB_TOKEN" | docker login -u YOUR_USER --password-stdin
docker tag alpine:3.23 YOUR_USER/cafe-api:1.0
docker push YOUR_USER/cafe-api:1.0
```

```bash
docker image rm cafe-student/cafe-api:1.0 > /dev/null
```

## Practice challenge

```bash
docker tag nginx:1.29-alpine cafe/web:stable
pinned=$(docker image inspect nginx:1.29-alpine --format '{{range .RepoDigests}}{{println .}}{{end}}' | grep '^nginx@')
echo "stable before: $(docker run --rm --entrypoint nginx cafe/web:stable -v 2>&1)"
docker tag nginx:1.30-alpine cafe/web:stable
echo "stable after:  $(docker run --rm --entrypoint nginx cafe/web:stable -v 2>&1)"
echo "digest still runs $(docker run --rm --entrypoint nginx "$pinned" -v 2>&1 | cut -d' ' -f3)"
docker image rm cafe/web:stable > /dev/null
```
