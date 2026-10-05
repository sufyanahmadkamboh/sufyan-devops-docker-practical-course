<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 078 · Private registries · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-078
cd ~/docker-practice/lesson-078
mkdir auth
```

```bash
docker run --rm alpine:3.23 sh -c 'apk add -q apache2-utils > /dev/null && htpasswd -Bbn student example-password-change-me' > auth/htpasswd
cut -c1-20 auth/htpasswd
```

```bash
docker run -d --name private-registry -p 5001:5000 \
  -v "$(pwd)/auth:/auth:ro" \
  -e REGISTRY_AUTH=htpasswd \
  -e REGISTRY_AUTH_HTPASSWD_REALM="Cafe registry" \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  registry:3 > /dev/null
sleep 2
docker inspect private-registry --format '{{.State.Status}}'
```

## Demonstration

```bash
curl -s -w '\nHTTP %{http_code}\n' localhost:5001/v2/ | tail -1
curl -s -w '\nHTTP %{http_code}\n' -u student:example-password-change-me localhost:5001/v2/ | tail -1
```

```bash
echo "example-password-change-me" | docker login localhost:5001 -u student --password-stdin 2>&1
```

```bash
docker tag alpine:3.23 localhost:5001/cafe/api:1.0
docker push -q localhost:5001/cafe/api:1.0
curl -s -u student:example-password-change-me localhost:5001/v2/_catalog
```

```bash
tr -d ' \n\t' < ~/.docker/config.json | grep -o '"localhost:5001":{[^}]*}' | sed 's/"auth":"[^"]*"/"auth":"…"/'
```

## Hands-on lab

```bash
docker logout localhost:5001
grep -c '"localhost:5001":' ~/.docker/config.json || true
```

## Break it

```bash
docker image rm localhost:5001/cafe/api:1.0 > /dev/null
docker pull localhost:5001/cafe/api:1.0 2>&1
```

```bash
echo "wrong-password" | docker login localhost:5001 -u student --password-stdin 2>&1
```

## Troubleshoot it

```bash
grep -q '"localhost:5001":' ~/.docker/config.json && echo "stored: yes" || echo "stored: no"
curl -s -w '\nHTTP %{http_code}\n' -u student:wrong-password localhost:5001/v2/ | tail -1
```

## Fix it

```bash
echo "example-password-change-me" | docker login localhost:5001 -u student --password-stdin > /dev/null 2>&1
docker pull -q localhost:5001/cafe/api:1.0
```

```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.eu-central-1.amazonaws.com
az acr login --name cafe-registry
gcloud auth configure-docker europe-west3-docker.pkg.dev
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-078
docker run --rm alpine:3.23 sh -c 'apk add -q apache2-utils > /dev/null && htpasswd -Bbn ci-bot another-example-change-me' >> auth/htpasswd
sleep 1
echo "another-example-change-me" | docker login localhost:5001 -u ci-bot --password-stdin 2>&1
```

## Cleanup

```bash
docker logout localhost:5001 > /dev/null 2>&1
docker rm -f private-registry > /dev/null
docker image rm localhost:5001/cafe/api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-078
```
