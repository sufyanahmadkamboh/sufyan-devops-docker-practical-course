<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 137 · Scanning and testing in CI · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-137 examples/node-api
cp -r 19-ci-cd/135-docker-in-ci/examples/test ~/docker-practice/lesson-137/
cp 19-ci-cd/137-scanning-and-testing-in-ci/examples/* ~/docker-practice/lesson-137/
cd ~/docker-practice/lesson-137
docker build -q --target production -t node-api:1.0.0 . > /dev/null
ls
```

## Demonstration

```bash
bash image-policy.sh node-api:1.0.0
echo "exit code: $?"
```

```bash
docker run -d --name smoke node-api:1.0.0 > /dev/null 2>&1 || true
docker inspect smoke --format '{{.State.Health.Status}}'
```

```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 node-api:1.0.0
docker scout cves --only-severity critical,high --exit-code node-api:1.0.0
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-137
bash image-policy.sh node-api:1.0.0 && echo "push allowed"
```

## Break it

```bash
cd ~/docker-practice/lesson-137
docker build -q --target base -t node-api:1.0.1 . > /dev/null
docker run --rm node-api:1.0.1 node -e "console.log('it runs')"
bash image-policy.sh node-api:1.0.1
```

## Troubleshoot it

```bash
cd ~/docker-practice/lesson-137
docker image inspect node-api:1.0.1 --format 'user="{{.Config.User}}" healthcheck={{.Config.Healthcheck}}'
grep -n "^FROM" Dockerfile
```

## Fix it

```bash
cd ~/docker-practice/lesson-137
docker build -q --target production -t node-api:1.0.1 . > /dev/null
bash image-policy.sh node-api:1.0.1
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-137
MAX_MB=10 bash image-policy.sh node-api:1.0.1 || echo "gate failed: exit code $?"
```

## Cleanup

```bash
docker rm -f smoke > /dev/null
docker image rm -f node-api:1.0.0 node-api:1.0.1 > /dev/null
rm -rf ~/docker-practice/lesson-137
```
