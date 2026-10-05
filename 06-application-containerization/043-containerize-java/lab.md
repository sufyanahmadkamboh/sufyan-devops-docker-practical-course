<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 043 · Containerizing a Java application · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Without rebuilding, start the image with a 512 MB limit and `JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=75`
(the JVM reads options from this variable), and check the new maximum heap.

**Expected result.** `MaxHeapSize` of about 384 MB (402653184 bytes, the JVM rounds to its alignment), and a line
`Picked up JAVA_TOOL_OPTIONS` proving the variable was read.

**Verification.**

```bash
docker run --rm -m 512m -e JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=75 java-api:1.0 \
  java -XX:+PrintFlagsFinal -version 2>&1 | grep -E 'Picked up|MaxHeapSize '
```
