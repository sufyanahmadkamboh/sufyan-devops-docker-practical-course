<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 052 · Network troubleshooting · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

A colleague starts the fixed server with `-p 8081:80` because "web servers use port 80". Reproduce it, prove with the
checklist which step fails, and fix it.

## Solution

```bash
docker run -d --name app2 -p 8081:80 python:3.14-slim python -m http.server 8000 --bind 0.0.0.0 > /dev/null
sleep 1
echo "published: $(docker port app2)"
echo "listening: $(docker run --rm --network container:app2 busybox:1.37 netstat -tln | grep -o '0.0.0.0:8000')"
docker rm -f app2 > /dev/null
docker run -d --name app2 -p 8081:8000 python:3.14-slim python -m http.server 8000 --bind 0.0.0.0 > /dev/null
sleep 1
echo "fixed: $(curl -s -w '\n%{http_code}' http://localhost:8081 | tail -1)"
```

```text
published: 80/tcp -> 0.0.0.0:8081
80/tcp -> [::]:8081
listening: 0.0.0.0:8000
fixed: 200
```

Step 3 fails: the host port forwards to container port 80, but the application listens on 8000. The container port
in `-p HOST:CONTAINER` must be the port the application really listens on.
