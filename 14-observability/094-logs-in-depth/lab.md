<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 094 · Logs in depth · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** `docker logs -f` follows a log until you press Ctrl+C, or until the container stops. Start a short
job that prints a line every second for three seconds, and follow its log from the start.

**Expected result.** The three lines appear one per second, and the command returns by itself when the job ends.

**Verification.**

```bash
docker run -d --name ticker alpine:3.23 sh -c 'for i in 1 2 3; do echo "tick $i"; sleep 1; done' > /dev/null
docker logs -f -t ticker
```
