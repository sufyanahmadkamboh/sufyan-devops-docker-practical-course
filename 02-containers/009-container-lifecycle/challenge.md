<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 009 · Container lifecycle · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

A container's main process fails at once with exit code 1. Start it with the restart policy `--restart on-failure:3`, so
that Docker restarts it at most three times, and show how many restarts Docker made.

The solution is in [solution.md](solution.md).
