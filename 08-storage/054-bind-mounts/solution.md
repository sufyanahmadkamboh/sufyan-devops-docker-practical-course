<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 054 · Bind mounts · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Override a single **file** instead of a folder: write your own `nginx.conf` server block on the host that returns the
text `hello from my config` on every request, and bind-mount it over `/etc/nginx/conf.d/default.conf`.

## Solution

```bash
cd ~/docker-practice/lesson-054
printf 'server {\n  listen 80;\n  location / { return 200 "hello from my config\\n"; }\n}\n' > default.conf
docker run -d --name custom -p 8082:80 -v "$(pwd)/default.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
curl -s http://localhost:8082
```

```text
hello from my config
```

Mounting single configuration files is how many teams configure off-the-shelf images without building their own.
