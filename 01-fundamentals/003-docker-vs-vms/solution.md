<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 003 · Docker vs virtual machines · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

A container only sees its own processes. Prove it: start a long-running container in the background, then list the
processes from a **second** container. Does the second one see the first one's `sleep`?

## Solution

```bash
docker run -d --name sleeper alpine:3.23 sleep 300 > /dev/null
docker run --rm alpine:3.23 ps | grep -q sleep && echo "sleep-visible" || echo "sleep-absent"
docker rm -f sleeper > /dev/null
```

```text
sleep-absent
```

Each container has its own **PID namespace**: process 1 of every container is its own command, and it cannot see the
processes of other containers (the host can see all of them). `-d` runs in the background (lesson 009).
