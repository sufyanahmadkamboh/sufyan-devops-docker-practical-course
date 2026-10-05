<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 092 · HEALTHCHECK · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Make a healthy container unhealthy on purpose: in `web-fixed`, delete the page nginx serves
(`/usr/share/nginx/html/index.html`) and watch the status change. Explain why `wget --spider` now fails.

## Solution

```bash
docker exec web-fixed rm /usr/share/nginx/html/index.html && echo done
```

```bash
docker ps --filter name=web-fixed --format '{{.Names}}: {{.Status}}'
docker inspect --format '{{range .State.Health.Log}}{{.Output}}{{end}}' web-fixed | grep . | tail -1
```

```text
web-fixed: Up 34 seconds (unhealthy)
wget: server returned error: HTTP/1.1 403 Forbidden
```

Without `index.html`, nginx answers `/` with an error status (403, directory listing is off), and `wget` exits with a
non-zero status for HTTP errors. Three failures in a row → `unhealthy`. A good health check tests what users need, not
just "is the port open".
