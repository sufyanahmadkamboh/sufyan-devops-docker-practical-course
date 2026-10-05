<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 059 · Environment variables · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Without changing any file, run the API for three "environments" at once (ports 8083, 8084, 8085), each with its own
`GREETING` and `APP_VERSION`, and show the three answers.

## Solution

```bash
port=8083
for envname in dev staging production; do
  docker run -d --name "api-$envname" -p "$port:3000" -v "$(pwd):/app:ro" -w /app \
    -e GREETING="Hello from $envname" -e APP_VERSION="1.4.0-$envname" node:24-alpine node server.js > /dev/null
  port=$((port + 1))
done
sleep 1
for port in 8083 8084 8085; do curl -s "http://localhost:$port"; echo; done
```

```text
{"message":"Hello from dev","hostname":"b955ad0fe2e5","version":"1.4.0-dev"}
{"message":"Hello from staging","hostname":"91764306e159","version":"1.4.0-staging"}
{"message":"Hello from production","hostname":"aa600a151131","version":"1.4.0-production"}
```

One artefact, three configurations: exactly how the same image moves from development to production.
