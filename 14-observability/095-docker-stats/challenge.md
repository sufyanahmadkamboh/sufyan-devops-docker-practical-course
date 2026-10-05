<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 095 · docker stats · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Write a command that prints a warning for every running container that uses more than 50% of its memory limit. Test it
by filling the `cache` container's memory: `docker exec cache redis-cli DEBUG POPULATE 550000` writes 550,000
test keys (the `cache` container was started with `--enable-debug-command local` to allow it).

The solution is in [solution.md](solution.md).
