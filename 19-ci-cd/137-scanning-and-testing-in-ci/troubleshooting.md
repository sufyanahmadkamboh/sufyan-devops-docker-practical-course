<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 137 · Scanning and testing in CI · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A change to the pipeline builds the wrong stage: `--target base` instead of `--target production`. The image works
perfectly:

```bash
cd ~/docker-practice/lesson-137
docker build -q --target base -t node-api:1.0.1 . > /dev/null
docker run --rm node-api:1.0.1 node -e "console.log('it runs')"
bash image-policy.sh node-api:1.0.1
```

```text
it runs
PASS  version tag
FAIL  non-root user: runs as root (set USER)
FAIL  healthcheck: no HEALTHCHECK
PASS  no secrets in ENV
PASS  size (59 MB, budget 300 MB)
```

## Troubleshoot it

The gate names the failing rules: no user, no healthcheck. Both are set only in the `production` stage, so the image
was built from another stage. Confirm with the image's configuration and the Dockerfile's stages:

```bash
cd ~/docker-practice/lesson-137
docker image inspect node-api:1.0.1 --format 'user="{{.Config.User}}" healthcheck={{.Config.Healthcheck}}'
grep -n "^FROM" Dockerfile
```

```text
user="" healthcheck=<nil>
2:FROM node:24-alpine AS base
10:FROM base AS test
15:FROM base AS production
```

`base` has the code and dependencies but no `USER` and no `HEALTHCHECK`: a root image that nobody can monitor would
have been pushed if the gate had not stopped it. A test that only runs the application would never notice.

## Fix it

```bash
cd ~/docker-practice/lesson-137
docker build -q --target production -t node-api:1.0.1 . > /dev/null
bash image-policy.sh node-api:1.0.1
```
