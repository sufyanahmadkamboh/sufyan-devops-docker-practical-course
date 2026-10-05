<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 090 · Multi-stage builds for Java · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Verify that the running container uses the unprivileged `app` user, and check which maximum heap the
image's `-XX:MaxRAMPercentage=75` gives a container limited to 512 MB (run `java -XX:+PrintFlagsFinal -version` with
the same option and `-m 512m`).

**Expected result.** `uid=…(app)`, and a `MaxHeapSize` of about 384 MB (75 % of 512 MB).

**Verification.**

```bash
docker exec java-multi id
docker run --rm -m 512m --entrypoint java java-multi:1.0 -XX:MaxRAMPercentage=75 -XX:+PrintFlagsFinal -version 2>/dev/null | grep -w MaxHeapSize
```
