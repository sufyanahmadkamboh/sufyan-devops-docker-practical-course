<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 030 · ENV · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Run `cafe-api:env` so that the application listens on port **4000** inside the container, reachable on port 8083 of
your computer, without rebuilding the image.

## Solution

```bash
docker run -d --name cafe-api-4000 -e PORT=4000 -p 8083:4000 cafe-api:env > /dev/null && echo "started"
```

```bash
curl -s http://localhost:8083 && echo
docker logs cafe-api-4000
```

```text
{"message":"Hello from the cafe","hostname":"30e616f50ecc","version":"1.0.0"}
node-api listening on port 4000
```

`-e PORT=4000` changes where the application listens; `-p 8083:4000` must then publish that port. The image's `ENV`
was only the default.
