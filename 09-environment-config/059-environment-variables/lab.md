<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 059 · Environment variables · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show the complete environment the `configured-api` container was created with, and change the port
the application listens on **inside** its container to `4000` in a new container `port-api`, published on host port
8082.

**Expected result.** `GREETING=Welcome to the cafe` in the list; `port-api` answers on 8082 and logs
`listening on port 4000`.

**Verification.**

```bash
docker inspect configured-api --format '{{range .Config.Env}}{{println .}}{{end}}'
docker run -d --name port-api -p 8082:4000 -e PORT=4000 -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8082 > /dev/null && docker logs port-api
```
