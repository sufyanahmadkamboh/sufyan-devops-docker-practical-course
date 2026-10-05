<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 032 · EXPOSE · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

The application's port is configurable (`PORT`). Build an image where `ENV PORT=8000` and `EXPOSE` stay consistent by
using the same build argument for both, then check with `-P` that it answers.

## Solution

```bash
cd ~/docker-practice/lesson-032
cat > Dockerfile.port <<'EOF'
FROM node:24-alpine
ARG PORT=8000
WORKDIR /app
COPY . .
ENV PORT=$PORT
EXPOSE $PORT
CMD ["node", "server.js"]
EOF
docker build -q -f Dockerfile.port -t cafe-api:8000 . > /dev/null
docker run -d --name cafe-api-8000 -P cafe-api:8000 > /dev/null
docker port cafe-api-8000
```

```text
8000/tcp -> 0.0.0.0:32787
```

```bash
curl -s "http://localhost:$(docker port cafe-api-8000 8000/tcp | head -1 | sed 's/.*://')"
```

One argument feeds both the application's configuration and the documentation, so they cannot drift apart.
