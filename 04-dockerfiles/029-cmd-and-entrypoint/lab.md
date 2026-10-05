<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 029 · CMD and ENTRYPOINT together · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Run `pinger` against `127.0.0.1` instead of `localhost`, and show the stored entrypoint and command.

**Expected result.** Two pings to 127.0.0.1; `["ping","-c","2"]` and `["localhost"]`.

**Verification.**

```bash
docker run --rm pinger 127.0.0.1
docker image inspect --format '{{json .Config.Entrypoint}} {{json .Config.Cmd}}' pinger
```
