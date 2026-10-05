<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 132 · Immutable containers · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Version 1.1 has a problem: roll back to version 1.0 and prove the old headline is back, without building anything.

## Solution

```bash
docker rm -f site > /dev/null
docker run -d --name site -p 8080:80 site:1.0 > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<h1>"
```

```text
  <h1>Welcome to the cafe</h1>
```

Because every version is a separate, unchanged image, a rollback is starting the previous one: seconds, and exactly
the bytes that ran before.
