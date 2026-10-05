<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 037 · .dockerignore · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Replace the `.dockerignore` with the course's full example (`dockerignore.example`), rebuild as
`ignore-demo:lab`, and check that neither `.env` nor `node_modules` nor any log is in the image, while the API still
starts.

**Expected result.** `/app` contains only `package.json`, `package-lock.json` and `server.js`, and the server logs
`node-api listening on port 3000`.

**Verification.**

```bash
cd ~/docker-practice/lesson-037
cp dockerignore.example .dockerignore
docker build -q -t ignore-demo:lab . > /dev/null
docker run --rm ignore-demo:lab ls -a /app
docker run -d --name ignore-api ignore-demo:lab > /dev/null
sleep 1
docker logs ignore-api
docker rm -f ignore-api > /dev/null
```
