<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 079 · GitHub Container Registry · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-079 11-registry/079-github-container-registry/examples
cd ~/docker-practice/lesson-079
cat Dockerfile
```

## Demonstration

```bash
docker build -q -t ghcr.io/cafe-team-example/cafe-api:1.0 . > /dev/null
docker image ls ghcr.io/cafe-team-example/cafe-api --format '{{.Repository}}:{{.Tag}}'
docker run --rm ghcr.io/cafe-team-example/cafe-api:1.0
```

```bash
docker image inspect ghcr.io/cafe-team-example/cafe-api:1.0 --format '{{range $k, $v := .Config.Labels}}{{$k}}={{$v}}{{"\n"}}{{end}}'
```

```bash
gh auth refresh -s write:packages           # once: adds the scope (opens the browser)
gh auth token | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin
docker tag ghcr.io/cafe-team-example/cafe-api:1.0 ghcr.io/YOUR_GITHUB_USER/cafe-api:1.0
docker push ghcr.io/YOUR_GITHUB_USER/cafe-api:1.0
```

```bash
grep -E "permissions|packages|GITHUB_TOKEN|docker (push|build)" docker-publish.yml
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-079
docker build -q --label org.opencontainers.image.version=1.0 -t ghcr.io/cafe-team-example/cafe-api:1.0 . > /dev/null
docker image inspect ghcr.io/cafe-team-example/cafe-api:1.0 --format '{{index .Config.Labels "org.opencontainers.image.version"}}'
```

## Break it

```bash
docker push ghcr.io/cafe-team-example/cafe-api:1.0 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
grep -q '"ghcr.io"' ~/.docker/config.json 2> /dev/null && echo "ghcr.io login stored: yes" || echo "ghcr.io login stored: no"
```

```bash
gh auth status          # lists "Token scopes: … write:packages …" when the scope is there
```

## Fix it

```bash
gh auth token | docker login ghcr.io -u YOUR_GITHUB_USER --password-stdin
docker tag ghcr.io/cafe-team-example/cafe-api:1.0 ghcr.io/your_github_user/cafe-api:1.0
docker push ghcr.io/your_github_user/cafe-api:1.0
```

## Practice challenge

```bash
GITHUB_REPOSITORY_OWNER=Cafe-Team GITHUB_REF_NAME=v2.3.0 bash -c '
  image=ghcr.io/${GITHUB_REPOSITORY_OWNER,,}/cafe-api:${GITHUB_REF_NAME#v}
  echo "$image"
  docker tag ghcr.io/cafe-team-example/cafe-api:1.0 "$image" && echo "valid name"
  docker image rm "$image" > /dev/null'
```

## Cleanup

```bash
docker image rm ghcr.io/cafe-team-example/cafe-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-079
```
