<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 080 · The attack surface of a container · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Find out whether `ubuntu:24.04`, `alpine:3.23` and the distroless image contain a shell, a package manager and `wget`
or `curl`. Use `docker run --rm --entrypoint …` or `ls` in images that have a shell; for the distroless image, explain
why you cannot look inside it the same way.

The solution is in [solution.md](solution.md).
