<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 067 · Environment variables in Compose · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start the API on port 8090 instead of 8080 without editing any file, and check the greeting on `/`.

**Expected result.** `curl localhost:8090/` answers with `Hello from the .env file`.

**Verification.**

```bash
cd ~/docker-practice/lesson-067
API_PORT=8090 docker compose up -d 2> /dev/null
curl -s localhost:8090/
```

Back to the `.env` value for the next steps:

```bash
docker compose up -d 2> /dev/null
```
