<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 051 · EXPOSE vs publishing ports · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start nginx with `-P` (capital P), find out which host port Docker chose, and fetch the page through
it.

**Expected result.** `docker port` shows `80/tcp -> 0.0.0.0:NNNNN`; the page answers on that port.

**Verification.**

```bash
docker run -d --name random-port -P nginx:1.30-alpine > /dev/null && echo "started"
```

```bash
port=$(docker port random-port 80/tcp | head -1 | sed 's/.*://')
echo "nginx is on host port $port"
curl -s "http://localhost:$port" | grep -o '<title>.*</title>'
```
