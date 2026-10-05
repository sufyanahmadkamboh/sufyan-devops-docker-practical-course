<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 063 · Your first Compose file · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Add a third service `cache-ui` to `compose.yaml` that only runs `redis-cli -h redis ping` with the `redis:8-alpine`
image, start it, and show its output.

## Solution

```bash
cd ~/docker-practice/lesson-063
cat >> compose.yaml <<'EOF'
  cache-ui:
    image: redis:8-alpine
    command: redis-cli -h redis ping
EOF
docker compose up -d 2> /dev/null
sleep 2
docker compose logs --no-log-prefix cache-ui
```

```text
PONG
```

`command:` replaces the image's default command. The new service joins the project network, so `redis` resolves. It
exits after the ping: not every service is a long-running server.
