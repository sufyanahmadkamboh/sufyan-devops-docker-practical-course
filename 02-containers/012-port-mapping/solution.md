<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 012 · Port mapping · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Start an Nginx container with `-p 80` (no host port), find out which host port Docker chose, and fetch the page through
it.

## Solution

```bash
docker run -d --name temp -p 80 nginx:1.30-alpine
```

```bash
port=$(docker port temp 80/tcp | head -1 | sed 's/.*://')
echo "Docker chose host port $port"
curl -s "http://localhost:$port" | grep '<title>'
```

```text
Docker chose host port 63718
<title>Welcome to nginx!</title>
```

`docker port temp 80/tcp` prints `0.0.0.0:PORT` (and an IPv6 line): everything after the last `:` is the port. Random
ports avoid conflicts in tests and CI, where many copies of the same service run side by side.
