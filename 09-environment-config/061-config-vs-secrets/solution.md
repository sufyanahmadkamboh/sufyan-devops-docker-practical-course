<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 061 · Configuration vs secrets · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

The application needs an API token. Mount it as a secret file into a container and read it from the file in the
container's command, so that neither `docker inspect` nor the command line contains the token.

## Solution

```bash
printf 'example-token-0000-abc' > api_token.txt
docker run -d --name worker -v "$(pwd)/api_token.txt:/run/secrets/api_token:ro" alpine:3.23 \
  sh -c 'TOKEN=$(cat /run/secrets/api_token); echo "token length: ${#TOKEN}"; sleep 300' > /dev/null
sleep 1
docker logs worker
docker inspect worker | grep -q 'example-token' || echo "inspect clean"
```

```text
token length: 22
inspect clean
```

The token is read at runtime inside the container. Logging its length (never the value) is enough to prove it was
loaded.
