<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 031 · ARG · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

A build step needs a token to download a private package. Show the leak with `ARG` (use the fake value
`example-token-123`), then pass the token with a **build secret** instead (`RUN --mount=type=secret,…` and
`docker build --secret`), and prove it is not in the history.

## Solution

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

```text
leaked: yes
with a secret: not in the history
```

A secret mount makes the file `/run/secrets/api_token` available to that one `RUN` step only; it is never written to a
layer or to the history. Docker also warns about the first Dockerfile: `SecretsUsedInArgOrEnv: Do not use ARG or ENV
instructions for sensitive data`. Secrets are covered in depth in lesson 083.
