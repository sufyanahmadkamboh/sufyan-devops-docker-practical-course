<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 026 · RUN · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Build `run-demo:tools` from `alpine:3.23` with `curl` **and** `jq` installed in a single `RUN` step,
then run `jq --version` in it.

**Expected result.** `jq-1.` followed by the version.

**Verification.**

```bash
cd ~/docker-practice/lesson-026
printf 'FROM alpine:3.23\nRUN apk add --no-cache curl jq\n' > Dockerfile.tools
docker build -q -f Dockerfile.tools -t run-demo:tools . > /dev/null
docker run --rm run-demo:tools jq --version
```
