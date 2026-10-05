<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 131 · Container design · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

The Nginx image also links `error.log` to `/dev/stderr`. Make Nginx write an **error** (not access) log entry, and show
it using only the container's standard error stream.

## Solution

A missing file is logged both as a 404 access entry (stdout) and as an `open() … failed` error (stderr). Discard
standard output to see only standard error:

```bash
curl -s http://localhost:8080/nothing-here.html > /dev/null
docker logs web 2>&1 > /dev/null | grep nothing-here
```

```text
2026/10/05 12:16:50 [error] 33#33: *3 open() "/usr/share/nginx/html/nothing-here.html" failed (2: No such file or directory), client: 172.17.0.1, server: localhost, request: "GET /nothing-here.html HTTP/1.1", host: "localhost:8080"
```

`docker logs` keeps the two streams apart, like the container wrote them: `2>&1 > /dev/null` keeps stderr and drops
stdout.
