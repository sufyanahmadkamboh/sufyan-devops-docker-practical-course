<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 067 · Environment variables in Compose · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate clones the repository and runs the stack. `.env` is not in Git, so they do not have it:

```bash
mv .env .env.disabled
docker compose up -d 2>&1 | grep -i warn | head -1
```

```text
time="2026-10-05T19:12:36+02:00" level=warning msg="The \"API_PORT\" variable is not set. Defaulting to a blank string."
```

```bash
curl -s -w '\nHTTP %{http_code}\n' localhost:8080/ | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
HTTP 000
```

## Troubleshoot it

Compose printed a warning, not an error, and started the stack anyway. With `API_PORT` empty, `":5000"` means "publish
container port 5000 on a **random** host port". Ask Compose where it went:

```bash
docker compose config | grep -A 3 'ports:'
docker compose port api 5000
```

```text
time="2026-10-05T19:12:37+02:00" level=warning msg="The \"API_PORT\" variable is not set. Defaulting to a blank string."
    ports:
      - mode: ingress
        target: 5000
        protocol: tcp
time="2026-10-05T19:12:37+02:00" level=warning msg="The \"API_PORT\" variable is not set. Defaulting to a blank string."
0.0.0.0:50812
```

No `published:` line, and a random port. The greeting also fell back to its default (`Hello from Compose`).

## Fix it

Restore the `.env` file, and make the file fail loudly instead of silently when a required value is missing:

```bash
sed -i.bak 's/"${API_PORT}:5000"/"${API_PORT:?API_PORT must be set, copy .env.example to .env}:5000"/' compose.yaml && rm compose.yaml.bak
docker compose config 2>&1 > /dev/null
```

```text
error while interpolating services.api.ports.[]: required variable API_PORT is missing a value: API_PORT must be set, copy .env.example to .env
```

```bash
mv .env.disabled .env
docker compose up -d 2> /dev/null
curl -s localhost:8080/
```
