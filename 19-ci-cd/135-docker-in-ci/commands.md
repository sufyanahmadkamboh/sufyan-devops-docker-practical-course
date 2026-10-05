<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 135 · Docker in CI · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-135 examples/node-api
cp -r 19-ci-cd/135-docker-in-ci/examples/. ~/docker-practice/lesson-135/
cd ~/docker-practice/lesson-135
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
ls
```

## Demonstration

```bash
grep -E '^echo "==|docker (build|run|push)' ci.sh
```

```bash
VERSION=1.0.0 bash ci.sh
```

```bash
curl -s http://localhost:5000/v2/node-api/tags/list && echo
```

## Hands-on lab

```bash
docker run --rm localhost:5000/node-api:1.0.0 ls /app
echo "user=$(docker image inspect localhost:5000/node-api:1.0.0 --format '{{.Config.User}}')"
```

## Break it

```bash
cd ~/docker-practice/lesson-135
sed 's|Hello from Node.js|Hi from Node.js|' server.js > server.new && mv server.new server.js
VERSION=1.1.0 bash ci.sh 2>&1
```

## Troubleshoot it

```bash
curl -s http://localhost:5000/v2/node-api/tags/list && echo
```

```bash
cd ~/docker-practice/lesson-135
docker build --target test --progress=plain . 2>&1 | grep -E "not ok|expected|actual" | head -5
test "${PIPESTATUS[0]}" -eq 0
```

## Fix it

```bash
cd ~/docker-practice/lesson-135
sed 's|Hi from Node.js|Hello from Node.js|' server.js > server.new && mv server.new server.js
VERSION=1.1.0 bash ci.sh
```

## Practice challenge

```bash
for v in 1.0.0 1.1.0; do
  docker image inspect localhost:5000/node-api:$v --format "$v {{index .RepoDigests 0}}"
done
digest=$(docker image inspect localhost:5000/node-api:1.0.0 --format '{{index .RepoDigests 0}}')
docker pull -q "$digest" > /dev/null && echo "pulled by digest: $digest"
```

## Cleanup

```bash
docker rm -f registry smoke > /dev/null 2>&1 || true
docker image rm -f node-api:test localhost:5000/node-api:1.0.0 localhost:5000/node-api:1.1.0 > /dev/null
rm -rf ~/docker-practice/lesson-135
```
