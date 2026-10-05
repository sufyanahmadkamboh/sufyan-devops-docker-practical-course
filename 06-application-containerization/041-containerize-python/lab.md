<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 041 · Containerizing a Python application · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show the processes of the running container from the host with `docker top` (the slim image has no
`ps`), and check which user they run as.

**Expected result.** Three `gunicorn` processes (one master, two workers), all running as uid `10001`.

**Verification.**

```bash
docker top python-api -o pid,user,args
```

(`docker top` shows the host's view, where the user appears as `10001` because the host has no user named `appuser`.)
