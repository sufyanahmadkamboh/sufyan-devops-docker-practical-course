<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 083 · Secrets in images · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-083 12-security/083-secrets-in-images/examples/leaky 12-security/083-secrets-in-images/examples/fixed
cd ~/docker-practice/lesson-083
ls leaky fixed
```

## Demonstration

```bash
docker build -q --build-arg API_TOKEN=example-token-change-me-1234 -t cafe-secrets:leaky leaky > /dev/null
docker image ls cafe-secrets --format '{{.Repository}}:{{.Tag}}'
```

```bash
docker history --no-trunc --format '{{.CreatedBy}}' cafe-secrets:leaky | grep -i token
```

```bash
docker image inspect --format '{{range .Config.Env}}{{println .}}{{end}}' cafe-secrets:leaky
```

## Hands-on lab

```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' cafe-secrets:leaky | head -4
```

## Break it

```bash
docker run --rm cafe-secrets:leaky cat /tmp/credentials.txt 2>&1 || true
```

## Troubleshoot it

```bash
mkdir -p saved
docker save cafe-secrets:leaky -o saved/image.tar
tar -xf saved/image.tar -C saved
for layer in saved/blobs/sha256/*; do tar -xOf "$layer" tmp/credentials.txt 2>/dev/null || true; done
```

## Fix it

```bash
cat fixed/Dockerfile
```

```bash
docker build -q --secret id=api_token,src=fixed/api_token.txt -t cafe-secrets:fixed fixed > /dev/null
docker image ls cafe-secrets --format '{{.Repository}}:{{.Tag}}'
```

```bash
docker history --no-trunc cafe-secrets:fixed | grep -q example-token || echo "no token in history"
docker image inspect cafe-secrets:fixed | grep -q example-token || echo "no token in configuration"
rm -rf saved && mkdir saved
docker save cafe-secrets:fixed -o saved/image.tar && tar -xf saved/image.tar -C saved
found=no; for layer in saved/blobs/sha256/*; do tar -xOf "$layer" 2>/dev/null | grep -q example-token && found=yes; done
[ "$found" = no ] && echo "no token in layers"
```

## Practice challenge

```bash
printf 'DB_PASSWORD=example-password-change-me\n' > db.env
docker image inspect --format '{{.Config.Env}}' cafe-secrets:fixed | grep -q DB_PASSWORD || echo "image: no DB_PASSWORD"
echo "container: $(docker run --rm --env-file db.env cafe-secrets:fixed sh -c 'env | grep DB_PASSWORD')"
```

## Cleanup

```bash
docker image rm -f cafe-secrets:leaky cafe-secrets:fixed > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-083
```
