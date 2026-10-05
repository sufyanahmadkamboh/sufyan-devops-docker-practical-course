<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 023 · FROM: choosing a base image · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Write a Dockerfile `FROM debian:13-slim` whose container prints the `PRETTY_NAME` line of
`/etc/os-release`, build it as `base-demo:debian`, and run it.

**Expected result.** `PRETTY_NAME="Debian GNU/Linux 13 (trixie)"`.

**Verification.**

```bash
cd ~/docker-practice/lesson-023
printf 'FROM debian:13-slim\nCMD ["grep", "PRETTY_NAME", "/etc/os-release"]\n' > Dockerfile.debian
docker build -q -f Dockerfile.debian -t base-demo:debian . > /dev/null
docker run --rm base-demo:debian
```
