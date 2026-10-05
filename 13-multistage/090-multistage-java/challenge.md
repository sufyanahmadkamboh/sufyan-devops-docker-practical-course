<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 090 · Multi-stage builds for Java · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

`Dockerfile.jlink` uses `jdeps` to find the modules the jar needs and `jlink` to build a runtime with only those,
running on plain `alpine:3.23`. Build it as `java-jlink:1.0`, find out which modules it contains, check that the API
works, and compare its size with `java-multi:1.0`.

The solution is in [solution.md](solution.md).
