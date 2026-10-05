<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 006 · Your first container · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Run `busybox:1.37` with the command `echo "my first container"`, so that the container is removed
automatically when it exits. Then check that no `busybox` container is left.

**Expected result.** The text `my first container`, and `0` containers left from that image.

**Verification.**

```bash
docker run --rm busybox:1.37 echo "my first container"
echo "busybox containers: $(docker ps -aq --filter ancestor=busybox:1.37 | wc -l | tr -d ' ')"
```
