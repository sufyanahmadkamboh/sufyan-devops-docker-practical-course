<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 063 · Your first Compose file · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Add a `GREETING` variable with the value `Hello from Compose` to the `api` service, apply it with
`docker compose up -d`, and check the API's `/` endpoint.

**Expected result.** Compose recreates only the `api` container; `/` answers with your greeting.

**Verification.**

```bash
cd ~/docker-practice/lesson-063
awk '{ print } /REDIS_HOST: redis/ { print "      GREETING: Hello from Compose" }' compose.yaml > compose.new
mv compose.new compose.yaml
docker compose up -d 2> /dev/null
curl -s localhost:8080/
```

(`awk` copies every line and adds the new one after `REDIS_HOST`; editing the file in your editor is just as good.)
