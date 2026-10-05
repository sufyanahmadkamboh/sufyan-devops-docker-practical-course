<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 136 · Build and push with GitHub Actions · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-136 examples/node-api
cp -r 19-ci-cd/135-docker-in-ci/examples/. ~/docker-practice/lesson-136/
mkdir -p ~/docker-practice/lesson-136/.github/workflows
cp 19-ci-cd/136-build-and-push-with-github-actions/examples/docker-image.yml ~/docker-practice/lesson-136/.github/workflows/
cd ~/docker-practice/lesson-136
git init -q -b main && git add -A && git -c user.name="Course Learner" -c user.email="learner@example.com" commit -qm "node-api with CI"
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
git log --oneline
```

## Demonstration

```bash
grep -E 'uses:|permissions|packages|target:|push:' .github/workflows/docker-image.yml
```

```bash
sha=$(git rev-parse HEAD)
image=localhost:5000/node-api
docker build -q --target test . > /dev/null && echo "test stage: passed"
docker build -q --target production -t "$image:sha-$sha" -t "$image:main" . > /dev/null
docker push -q "$image:sha-$sha" > /dev/null
docker push -q "$image:main" > /dev/null
curl -s http://localhost:5000/v2/node-api/tags/list && echo
```

## Command breakdown

```bash
git remote add origin https://github.com/YOUR-USER/node-api.git
git push -u origin main
gh run watch                      # follow the workflow (GitHub CLI)
docker pull ghcr.io/YOUR-USER/node-api:main
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-136
git tag v1.0.0
version=$(git describe --tags --exact-match | sed 's/^v//')
docker tag localhost:5000/node-api:main "localhost:5000/node-api:$version"
docker push -q "localhost:5000/node-api:$version" > /dev/null
curl -s http://localhost:5000/v2/node-api/tags/list && echo
```

## Break it

```bash
cd ~/docker-practice/lesson-136
docker tag localhost:5000/node-api:main node-api:main
docker push node-api:main 2>&1 | grep -v Waiting
test "${PIPESTATUS[0]}" -eq 0
```

## Fix it

```bash
cd ~/docker-practice/lesson-136
docker tag node-api:main localhost:5000/node-api:main
docker push -q localhost:5000/node-api:main > /dev/null && echo "pushed localhost:5000/node-api:main"
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-136
grep -n "pull_request" .github/workflows/docker-image.yml
```

## Cleanup

```bash
docker rm -f registry > /dev/null
docker image rm -f node-api:main $(docker image ls -q localhost:5000/node-api | sort -u) > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-136
```
