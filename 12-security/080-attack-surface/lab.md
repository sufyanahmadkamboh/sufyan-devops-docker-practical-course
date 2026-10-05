<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 080 · The attack surface of a container · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Count the installed packages of `debian:13-slim` (`dpkg-query -f '.\n' -W | wc -l`) and of
`alpine:3.23` (`apk info | wc -l`). Which image has the smaller attack surface?

**Expected result.** Two numbers; Alpine has fewer packages.

**Verification.**

```bash
echo "debian:13-slim $(docker run --rm debian:13-slim sh -c "dpkg-query -f '.\n' -W | wc -l") packages"
echo "alpine:3.23    $(docker run --rm alpine:3.23 sh -c 'apk info | wc -l') packages"
```
