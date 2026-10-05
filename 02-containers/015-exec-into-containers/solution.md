<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 015 · Running commands in containers (exec) · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Check the Nginx configuration of `web` for syntax errors and find out which user the **worker** processes run as,
both from outside the container with `docker exec`.

## Solution

```bash
docker exec web nginx -t 2>&1
docker exec web ps -o user,args | grep 'worker process' | head -1
```

```text
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
nginx    nginx: worker process
```

`nginx -t` validates the configuration (run it before `nginx -s reload` after a change). The master process runs as
root to open port 80; the workers that handle requests run as the unprivileged user `nginx`.
