<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 040 · Containerizing a Node.js application · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

The application reads `PORT` (default 3000) and `GREETING` from the environment. Start the image so that the server
listens on port **4000** inside the container with the greeting `Hallo aus dem Container`, published on port 8081 of
your computer.

## Solution

```bash
docker run -d --name node-api-4000 -p 8081:4000 -e PORT=4000 -e GREETING="Hallo aus dem Container" node-api:fixed > /dev/null
sleep 1
curl -s http://localhost:8081/
```

```text
{"message":"Hallo aus dem Container","hostname":"185f5796615e","version":"dev"}
```

`-p HOST:CONTAINER` must use the port the application really listens on (`4000`), not the one in `EXPOSE`; `EXPOSE` is
documentation (lesson 051).
