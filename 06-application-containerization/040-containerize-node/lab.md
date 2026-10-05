<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 040 · Containerizing a Node.js application · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Stop the container and check how long it took and how the process ended.

**Expected result.** `docker stop` returns in about a second (not the 10 s timeout), and the exit code is `0`: the
server handled `SIGTERM` (see the last line of `server.js`) and shut down cleanly.

**Verification.**

```bash
start=$(date +%s)
docker stop node-api > /dev/null
echo "stopped in $(( $(date +%s) - start )) s, exit code $(docker inspect --format '{{.State.ExitCode}}' node-api)"
docker rm node-api > /dev/null
```
