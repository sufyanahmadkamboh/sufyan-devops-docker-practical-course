<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 060 · Environment files · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Someone "cleans up" the file in the style of a shell script, with quotes:

```bash
printf 'GREETING="Welcome to the cafe"\nAPP_VERSION=1.4.0\n' > quoted.env
docker run -d --name quoted -p 8081:3000 --env-file quoted.env -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8081; echo
```

```text
{"message":"\"Welcome to the cafe\"","hostname":"9be44f568f46","version":"1.4.0"}
```

## Troubleshoot it

The greeting now contains the quotes: `"\"Welcome to the cafe\""` in the JSON. Look at the value exactly as the
container received it:

```bash
docker exec quoted printenv GREETING | sed 's/^/GREETING=/'
```

```text
GREETING="Welcome to the cafe"
```

`docker run --env-file` takes everything after `=` literally: no quote removal, no `$VARIABLE` expansion, no
escaping. (Docker Compose's `.env` handling does remove quotes, which is why the two get mixed up.)

## Fix it

Write values without quotes; spaces inside a value need no quoting:

```bash
printf 'GREETING=Welcome to the cafe\nAPP_VERSION=1.4.0\n' > quoted.env
docker rm -f quoted > /dev/null
docker run -d --name quoted -p 8081:3000 --env-file quoted.env -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8081; echo
```

```text
{"message":"Welcome to the cafe","hostname":"af0a2afce13c","version":"1.4.0"}
```
