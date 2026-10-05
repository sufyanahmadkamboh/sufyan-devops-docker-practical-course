<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 134 · Security review · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Run the same checks against the hardened image `review-api:after`: build it, then check the user,
the environment, the tools, the command and the healthcheck.

**Expected result.** User `node`, no password in the environment, neither `curl` nor `bash`, the exec-form command and
a healthcheck.

**Verification.**

```bash
cd ~/docker-practice/lesson-134
docker build -q -t review-api:after after/ > /dev/null
echo "user=$(docker image inspect review-api:after --format '{{.Config.User}}')"
docker image inspect review-api:after --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -c PASSWORD || true
echo "tools=$(docker run --rm review-api:after sh -c 'command -v curl || command -v bash' || echo none)"
docker image inspect review-api:after --format 'cmd={{json .Config.Cmd}} healthcheck={{json .Config.Healthcheck.Test}}'
```
