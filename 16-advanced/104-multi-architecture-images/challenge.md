<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 104 · Multi-architecture images · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Prove that the build stage ran on the build machine's own platform and was **not** emulated: add a temporary `RUN`
step that prints `$BUILDPLATFORM`, `$TARGETPLATFORM` and `uname -m` in the build stage, and build for `linux/arm64`
with plain progress output.

The solution is in [solution.md](solution.md).
